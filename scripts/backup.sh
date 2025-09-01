#!/bin/bash

# Database Backup Script
# This script creates a compressed backup of the PostgreSQL database

set -e

BACKUP_DIR="/app/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backup_${POSTGRES_DB:-sistema}_${TIMESTAMP}.sql.gz"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "Creating database backup..."
echo "Database: ${POSTGRES_DB:-sistema}"
echo "Backup file: ${BACKUP_DIR}/${BACKUP_FILE}"

# Run backup using Python script
cd /app
python backup_manager.py backup

echo "Backup completed successfully"

# Clean old backups (keep last 7 days)
find "$BACKUP_DIR" -name "backup_*.sql.gz" -mtime +7 -delete
find "$BACKUP_DIR" -name "backup_*.json" -mtime +7 -delete

echo "Old backups cleaned up"