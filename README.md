# Sistema Django com Docker Compose

Sistema completo com Django 5.2, PostgreSQL 15, Redis, Celery, Flower, Nginx, Certbot, Grafana, Prometheus e sistema de backup automatizado.

## 🚀 Características

- **Django 5.2** com PostgreSQL 15 e Redis
- **Celery** para tarefas assíncronas
- **Flower** para monitoramento de tarefas
- **Nginx** como proxy reverso
- **Certbot** para SSL automático
- **Grafana** com dashboards de monitoramento
- **Prometheus** para coleta de métricas
- **Alertmanager** para gestão de alertas
- **Sistema de Backup** automatizado diariamente
- **Ambientes separados** para desenvolvimento e produção

## 📋 Pré-requisitos

- Docker e Docker Compose
- Make (opcional, para comandos simplificados)

## 🏗️ Configuração Inicial

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd sistema
```

### 2. Configure as variáveis de ambiente
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

### 3. Configure as permissões
```bash
chmod +x scripts/*.sh
```

## 🚀 Iniciar o Sistema

### Ambiente de Desenvolvimento
```bash
# Iniciar todos os serviços
docker compose -f docker-compose.dev.yml up -d

# Verificar logs
docker compose -f docker-compose.dev.yml logs -f

# Parar serviços
docker compose -f docker-compose.dev.yml down
```

### Ambiente de Produção
```bash
# Iniciar todos os serviços
docker compose up -d

# Verificar logs
docker compose logs -f

# Parar serviços
docker compose down
```

## 📊 Acessos aos Serviços

| Serviço | Desenvolvimento | Produção |
|---------|----------------|----------|
| Django Admin | http://localhost:8000/admin | https://seu-dominio.com/admin |
| Flower (Celery) | http://localhost:5555 | https://seu-dominio.com/flower |
| Grafana | http://localhost:3000 | https://seu-dominio.com/grafana |
| Prometheus | http://localhost:9090 | https://seu-dominio.com/prometheus |

**Credenciais padrão:**
- Grafana: admin/admin123 (mudar na primeira conexão)

## 🔧 Comandos Úteis

### Backup e Restauração
```bash
# Backup manual
docker compose exec postgres /scripts/backup.sh

# Listar backups
docker compose exec postgres /scripts/restore.sh --list

# Restaurar último backup
docker compose exec postgres /scripts/restore.sh --latest

# Restaurar backup específico
docker compose exec postgres /scripts/restore.sh /backup/nome_do_backup.sql.gz
```

### Gerenciar Chaves de Criptografia
```bash
# As chaves são geradas automaticamente ao iniciar
# Verificar chaves existentes
docker compose exec backend ls -la /app/keys/
```

### Logs e Monitoramento
```bash
# Ver logs de um serviço específico
docker compose logs backend
docker compose logs celery
docker compose logs nginx

# Ver todos os serviços
docker compose ps

# Estatísticas de uso
docker stats
```

## 📈 Monitoramento

### Dashboards Incluídos
- **Django Application**: Métricas de requests, tempo de resposta
- **PostgreSQL**: Conexões, performance do banco
- **Redis**: Uso de memória, performance
- **Sistema**: CPU, memória, disco

### Alertas Configurados
- CPU acima de 80%
- Memória acima de 85%
- Espaço em disco abaixo de 10%
- PostgreSQL, Redis, Django fora do ar

## 🔄 Migrações e Atualizações

### Executar migrações
```bash
docker compose exec backend python manage.py migrate
```

### Criar superusuário
```bash
docker compose exec backend python manage.py createsuperuser
```

### Coletar arquivos estáticos (produção)
```bash
docker compose exec backend python manage.py collectstatic --noinput
```

## 🐛 Solução de Problemas

### Problemas comuns

1. **Portas já em uso**
   ```bash
   # Verificar portas em uso
   netstat -tulpn | grep :8000
   
   # Parar serviços conflitantes ou mudar portas no .env
   ```

2. **Permissões de arquivos**
   ```bash
   sudo chown -R $USER:$USER .
   chmod +x scripts/*.sh
   ```

3. **Banco de dados corrompido**
   ```bash
   # Restaurar do backup
   docker compose exec postgres /scripts/restore.sh --latest
   ```

4. **SSL não funcionando**
   ```bash
   # Verificar certificados
   docker compose logs certbot
   
   # Forçar renovação
   docker compose exec certbot certbot renew --force-renewal
   ```

## 🏭 Configuração de Produção

### 1. Configure seu domínio
Edite o arquivo `.env`:
```bash
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com
DEBUG=false
```

### 2. Configure o Nginx
Edite `nginx/nginx.conf` para seu domínio.

### 3. Configure SSL
```bash
# Gerar certificados SSL
sudo certbot certonly --webroot -w ./data/certbot/www -d seu-dominio.com
```

### 4. Configure email
Edite as configurações de email no `.env`:
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.seu-servidor.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@dominio.com
EMAIL_HOST_PASSWORD=sua-senha
```

## 📁 Estrutura do Projeto

```
sistema/
├── backend/                 # Aplicação Django
│   ├── core/               # Configurações principais
│   ├── apps/               # Aplicações Django
│   ├── keys/               # Chaves de criptografia
│   ├── static/             # Arquivos estáticos
│   ├── media/              # Arquivos de mídia
│   └── requirements.txt    # Dependências Python
├── nginx/                  # Configuração Nginx
├── scripts/                # Scripts de backup e restauração
├── monitoring/             # Configurações de monitoramento
│   ├── prometheus/
│   ├── grafana/
│   └── alertmanager/
├── data/                   # Dados persistentes
│   ├── certbot/           # Certificados SSL
│   ├── media/             # Arquivos de mídia
│   └── static/            # Arquivos estáticos
├── backup/                # Backups do banco de dados
├── docker-compose.yml     # Produção
├── docker-compose.dev.yml # Desenvolvimento
└── .env                   # Variáveis de ambiente
```

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.