#!/bin/bash

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Iniciando sistema Django...${NC}"

# Função para verificar serviços
check_service() {
    local host=$1
    local port=$2
    local name=$3
    local timeout=60
    local elapsed=0
    
    echo -e "${YELLOW}⏳ Aguardando ${name}...${NC}"
    while ! nc -z $host $port; do
        sleep 2
        elapsed=$((elapsed + 2))
        if [ $elapsed -ge $timeout ]; then
            echo -e "${RED}❌ Timeout esperando ${name}${NC}"
            exit 1
        fi
    done
    echo -e "${GREEN}✅ ${name} está disponível${NC}"
}

# Verificar serviços
check_service "${POSTGRES_HOST:-postgres}" "${POSTGRES_PORT:-5432}" "PostgreSQL"
check_service "${REDIS_HOST:-redis}" "${REDIS_PORT:-6379}" "Redis"

# Verificar e criar diretório de chaves
echo -e "${YELLOW}🔐 Verificando diretório de chaves...${NC}"
if [ ! -d "/app/keys" ]; then
    mkdir -p /app/keys
    chmod 700 /app/keys
    echo -e "${GREEN}✅ Diretório de chaves criado${NC}"
fi

# Executar verificação e geração de chaves
echo -e "${YELLOW}🔐 Verificando chaves de criptografia...${NC}"
python manage.py check_keys

# Executar migrações do banco de dados
echo -e "${YELLOW}🔄 Executando migrações do banco de dados...${NC}"
python manage.py migrate --noinput

# Coletar arquivos estáticos (apenas em produção)
if [ "$DJANGO_SETTINGS_MODULE" = "core.settings.production" ]; then
    echo -e "${YELLOW}📦 Coletando arquivos estáticos...${NC}"
    python manage.py collectstatic --noinput --clear
fi

# Criar superusuário se não existir (apenas em desenvolvimento)
if [ "$DJANGO_SETTINGS_MODULE" = "core.settings.development" ]; then
    echo -e "${YELLOW}👤 Criando superusuário padrão...${NC}"
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Superusuário criado: admin/admin123')
else:
    print('ℹ️  Superusuário já existe')
"
fi

# Verificar integridade do banco de dados
echo -e "${YELLOW}🔍 Verificando integridade do banco de dados...${NC}"
python manage.py check --database default

echo -e "${GREEN}✅ Sistema pronto!${NC}"

# Iniciar servidor Django
if [ "$1" = "gunicorn" ]; then
    exec gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
else
    exec "$@"
fi