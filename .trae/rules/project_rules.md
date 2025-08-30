# Regras do Projeto - Sistema de Administração

## Tecnologias e Versões
- Desenvolvido em Go 1.25
- PostgreSQL como banco de dados
- Docker e Docker Compose para containerização
- Nginx como proxy reverso
- GraphQL com gqlgen para API
- HTML/CSS/JavaScript para frontend

## Arquitetura
- Organização do projeto seguindo Clean Architecture / Hexagonal Architecture
- Estrutura modular em camadas (handlers, services, repositories)
- Uso de Go Modules para gerenciamento de dependências
- gqlgen para geração de código GraphQL
- Separação clara entre backend e frontend

## Autenticação e Segurança

### Tokens de Acesso
- refresh token e access token são gerados e armazenados em cookies httpOnly, Secure, SameSite=Lax
- expires 7d para refresh token
- expires 15m para access token
- utilize refresh token para renovar o access token
- se o refresh token expirar, o usuário é redirecionado para a página de login
- blacklist de refresh token
- utilize o refresh token para blacklistar o access token

### CSRF Protection
- segurança com csrf token
- utilize o csrf token para proteger contra ataques csrf
- a configuração do csrf token é feita no frontend/backend
- o backend deve gerar o csrf token e armazenar em cookie httpOnly, Secure, SameSite=Lax, expires 7d
- o frontend deve obter o csrf token do cookie e adicionar em cabeçalho de requisição
- o usuário deve validar o email, senha e csrf token
- o backend deve validar o csrf token
- se o csrf token for inválido, o backend deve retornar um erro
- o frontend deve tratar o erro e redirecionar o usuário para a página de login
- o backend deve invalidar o refresh token

## Sistema de Usuários

### Tipos de Usuário
- o usuário pode ser administrador, fundador ou usuário normal
- o primeiro usuário do banco precisa ser administrador
- o fundador pode criar outros usuários
- o usuário pode se tornar fundador
- o usuário pode se tornar administrador
- o administrador pode gerenciar outros usuários
- o usuário pode se tornar normal

### Registro e Login
- para registro o usuário precisa de nome, email e senha
- o nome é obrigatório
- o email é obrigatório
- a senha é obrigatória
- após a validação o login é feito automaticamente

### Avatar do Usuário
- todos usuários possuem um avatar
- o avatar é armazenado na pasta uploads/avatar
- o avatar é redimensionado para 200x200
- o avatar é armazenado com extensão .jpg
- o avatar é armazenado com hash no nome

## Estrutura do Banco de Dados

### Tabela Users
- id (UUID, primary key)
- name (string, not null)
- email (string, unique, not null)
- password_hash (string, not null)
- role (enum: user, admin, founder)
- avatar_url (string, nullable)
- email_verified (boolean, default false)
- created_at (timestamp)
- updated_at (timestamp)

### Tabela Products
- id (UUID, primary key)
- name (string, not null)
- description (text)
- price (decimal)
- created_at (timestamp)
- updated_at (timestamp)

## Estrutura de Pastas

```
sistema/
├── backend/
│   ├── database/
│   ├── graph/
│   │   ├── generated/
│   │   ├── model/
│   │   └── schema.graphqls
│   ├── models/
│   ├── handlers/
│   ├── services/
│   ├── repositories/
│   ├── middleware/
│   ├── utils/
│   └── uploads/
│       └── avatar/
├── frontend-admin/
│   ├── templates/
│   ├── static/
│   └── handlers/
├── nginx/
│   └── conf.d/
└── docker-compose.yml
```

## Configurações de Desenvolvimento

### Docker Compose
- PostgreSQL na porta 5432
- Backend na porta 8080
- Frontend na porta 8081
- Nginx na porta 3000 (proxy reverso)

### Variáveis de Ambiente
- DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
- JWT_SECRET para assinatura de tokens
- CSRF_SECRET para proteção CSRF
- UPLOAD_PATH para armazenamento de arquivos

## Padrões de Código

### Backend (Go)
- Usar context.Context em todas as funções
- Tratamento adequado de erros
- Logging estruturado
- Validação de entrada
- Testes unitários obrigatórios

### Frontend
- Templates HTML semânticos
- CSS responsivo
- JavaScript vanilla ou frameworks mínimos
- Validação client-side e server-side

### GraphQL
- Schemas bem documentados
- Resolvers eficientes
- Paginação para listas
- Tratamento de erros padronizado

## Segurança

### Gerais
- Validação de entrada em todas as camadas
- Sanitização de dados
- Rate limiting
- HTTPS obrigatório em produção
- Headers de segurança configurados

### Senhas
- Hash com bcrypt
- Política de senha forte
- Rotação de tokens
- Logout seguro

## Performance

### Backend
- Connection pooling para banco de dados
- Cache quando apropriado
- Queries otimizadas
- Compressão de resposta

### Frontend
- Minificação de assets
- Lazy loading quando possível
- Otimização de imagens
- CDN para assets estáticos

## Monitoramento e Logs

### Logs
- Logs estruturados (JSON)
- Níveis apropriados (DEBUG, INFO, WARN, ERROR)
- Não logar informações sensíveis
- Rotação de logs

### Métricas
- Tempo de resposta
- Taxa de erro
- Uso de recursos
- Métricas de negócio

## Telemetria e Observabilidade

### Coleta de Métricas
- **Prometheus** para coleta e armazenamento de métricas
- **Grafana** para visualização de dashboards
- Métricas de aplicação (latência, throughput, taxa de erro)
- Métricas de infraestrutura (CPU, memória, disco, rede)
- Métricas de banco de dados (conexões, queries, locks)
- Métricas de negócio (usuários ativos, transações, conversões)

### Distributed Tracing
- **OpenTelemetry** para instrumentação distribuída
- **Jaeger** ou **Zipkin** para visualização de traces
- Rastreamento de requisições entre serviços
- Correlação de logs com traces
- Identificação de gargalos e latências

### Health Checks
- Endpoints de health check para cada serviço
- Verificação de dependências (banco, cache, APIs externas)
- Readiness e liveness probes para Kubernetes
- Alertas automáticos em caso de falha

### Alertas e Notificações
- **AlertManager** para gerenciamento de alertas
- Integração com Slack, email, PagerDuty
- Alertas baseados em SLIs (Service Level Indicators)
- Escalação automática de alertas críticos
- Supressão de alertas duplicados

### Service Level Objectives (SLOs)
- Definição de SLIs para cada serviço crítico
- SLOs de disponibilidade (99.9% uptime)
- SLOs de latência (P95 < 200ms)
- SLOs de taxa de erro (< 0.1%)
- Error budgets para releases

### Instrumentação de Código
- Métricas customizadas em pontos críticos
- Contadores de eventos de negócio
- Histogramas para distribuição de latências
- Gauges para valores instantâneos
- Spans customizados para operações importantes

### Dashboards e Visualização
- Dashboard de overview do sistema
- Dashboards específicos por serviço
- Dashboard de métricas de negócio
- Dashboard de infraestrutura
- Alertas visuais em tempo real

### Retenção de Dados
- Métricas de alta resolução: 7 dias
- Métricas agregadas: 30 dias
- Métricas históricas: 1 ano
- Traces: 7 dias
- Logs críticos: 90 dias

### Ferramentas de Telemetria
- **Prometheus** + **Grafana** para métricas
- **OpenTelemetry** para instrumentação
- **Jaeger** para distributed tracing
- **ELK Stack** (Elasticsearch, Logstash, Kibana) para logs
- **AlertManager** para alertas
- **Node Exporter** para métricas de sistema

## Deploy e CI/CD

### Ambientes
- Development (local)
- Staging (pré-produção)
- Production (produção)

### Pipeline
- Testes automatizados
- Build de imagens Docker
- Deploy automatizado
- Rollback automático em caso de falha

## Backup e Recuperação

### Banco de Dados
- Backup diário automatizado
- Retenção de 30 dias
- Teste de recuperação mensal

### Arquivos
- Backup de uploads
- Sincronização com storage externo
- Versionamento de arquivos críticos
