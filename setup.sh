#!/bin/bash

# Sistema Setup Script
# This script sets up the entire system including SSL certificates, environment variables, and initial configurations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   error "This script should not be run as root"
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    error "Docker is not installed. Please install Docker first."
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    error "Docker Compose is not installed. Please install Docker Compose first."
fi

log "Starting Sistema setup..."

# Create necessary directories
log "Creating directory structure..."
mkdir -p data/certbot/conf
mkdir -p data/certbot/www
mkdir -p data/backups
mkdir -p data/mailu/{certs,data,dkim,overrides/{nginx,postfix,dovecot}}
mkdir -p monitoring/grafana/provisioning/{dashboards,datasources}
mkdir -p monitoring/grafana/dashboards
mkdir -p monitoring/prometheus
mkdir -p monitoring/alertmanager

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    log "Creating .env file from template..."
    cp .env.example .env
    warn "Please edit .env file with your specific configuration before continuing"
    read -p "Press enter to continue after editing .env..."
fi

# Generate SSL certificates for development
if [ ! -f data/certbot/conf/live/localhost/fullchain.pem ]; then
    log "Generating self-signed SSL certificates for development..."
    openssl req -x509 -nodes -newkey rsa:4096 -days 365 \
        -keyout data/certbot/conf/privkey.pem \
        -out data/certbot/conf/fullchain.pem \
        -subj "/C=BR/ST=SP/L=SaoPaulo/O=Sistema/CN=localhost"
    mkdir -p data/certbot/conf/live/localhost
    cp data/certbot/conf/fullchain.pem data/certbot/conf/live/localhost/
    cp data/certbot/conf/privkey.pem data/certbot/conf/live/localhost/
fi

# Set proper permissions
log "Setting permissions..."
sudo chown -R $USER:$USER data/
sudo chmod -R 755 data/
sudo chmod 600 data/certbot/conf/privkey.pem

# Create initial keys if they don't exist
if [ ! -d keys ]; then
    log "Creating keys directory..."
    mkdir -p keys
    log "Keys will be generated automatically when the backend starts"
fi

# Create monitoring configuration files
log "Creating monitoring configurations..."

# Create Grafana datasource configuration
cat > monitoring/grafana/provisioning/datasources/prometheus.yml << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
EOF

# Create Grafana dashboard configuration
cat > monitoring/grafana/provisioning/dashboards/dashboard.yml << EOF
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    options:
      path: /var/lib/grafana/dashboards
EOF

# Create backup script
cat > scripts/restore.sh << 'EOF'
#!/bin/bash

# Restore script for Sistema

BACKUP_DIR="/app/backups"
LATEST_BACKUP=$(ls -t $BACKUP_DIR/*.sql.gz | head -n 1)

if [ -z "$LATEST_BACKUP" ]; then
    echo "No backup files found in $BACKUP_DIR"
    exit 1
fi

echo "Restoring from backup: $LATEST_BACKUP"

gunzip -c "$LATEST_BACKUP" | PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB"

echo "Restore completed successfully"
EOF

chmod +x scripts/restore.sh

# Create development environment file
cat > .env.dev << EOF
# Development Environment Configuration
DEBUG=true
ENVIRONMENT=development

# Django Configuration
DJANGO_SETTINGS_MODULE=core.settings.development

# Database Configuration (Development)
POSTGRES_DB=sistema_dev_db
POSTGRES_USER=sistema_dev_user
POSTGRES_PASSWORD=dev-password

# Redis Configuration (Development)
REDIS_PASSWORD=dev-redis-password

# Email Configuration (Development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Celery Configuration (Development)
CELERY_BROKER_URL=redis://redis_test:6379/0
CELERY_RESULT_BACKEND=redis://redis_test:6379/0
EOF

log "Setup completed successfully!"
log "Next steps:"
echo "1. Edit .env file with your specific configuration"
echo "2. Run 'docker-compose up -d' to start the production environment"
echo "3. Run 'docker-compose -f docker-compose.dev.yml up -d' to start the development environment"
echo "4. Access the application at https://localhost"
echo "5. Access monitoring at:"
echo "   - Grafana: http://localhost:3000"
echo "   - Prometheus: http://localhost:9090"
echo "   - Flower: http://localhost:5555"