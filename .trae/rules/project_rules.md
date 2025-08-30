# Especificações do Projeto

## Estrutura de Containers e Serviços

1. O projeto contém um container chamado **backend**, iniciado no diretório `backend`.
2. O projeto contém um container chamado **frontend-admin**, iniciado no diretório `frontend-admin`.
3. O projeto contém um container chamado **frontend-fundador**, iniciado no diretório `frontend-admin`.
4. O projeto contém um container chamado **frontend-usuario**, iniciado no diretório `frontend-usuario`.
5. O projeto terá um container chamado **frontend-publico**.
6. O projeto terá um container para desenvolvimento de um aplicativo **React Native**, que se conecta ao backend.
7. O Docker Compose inclui **Nginx** como servidor reverso, configurado com:
   - **Suporte SSL/TLS** com certificados na porta 443
   - **Redirecionamento HTTP para HTTPS** para comunicação segura
   - **Volume SSL** mapeado para `/etc/nginx/ssl` para certificados
   - **Configuração de ciphers** seguros e protocolos TLS modernos
8. O Docker Compose inclui **PostgreSQL** como banco de dados, configurado com:
   - **Timezone configurado** para America/Sao_Paulo (Brasil)
   - **Configurações de performance** otimizadas para o ambiente
9. O Docker Compose incluirá **Redis** como serviço de cache, com volume próprio para persistência de dados temporários, configurado com:
   - **Autenticação por senha** (requirepass) para segurança
   - **Configurações de performance**: `--maxmemory 256mb --maxmemory-policy allkeys-lru`
   - **Persistência otimizada**: `--appendonly yes --appendfsync everysec`
   - **Timezone configurado** para America/Sao_Paulo (Brasil)
10. O projeto terá um container separado para **serviço de logs**, com volume próprio para persistência.
11. Todos os containers do projeto serão conectados a uma **rede interna** para comunicação segura.
12. Serão criados **volumes dedicados** para persistência de dados do PostgreSQL, para armazenamento do backend, logs, uploads e cache Redis, cada um em volume próprio.
13. O projeto utilizará **múltiplos arquivos Docker Compose** para separação de ambientes:
   - **docker-compose.yml**: configuração base compartilhada
   - **docker-compose.override.yml**: configurações específicas de desenvolvimento (padrão)
   - **docker-compose.prod.yml**: configurações específicas de produção
   - **docker-compose.staging.yml**: configurações específicas de staging (opcional)
14. Os containers críticos, como **backend**, **PostgreSQL** e **Redis**, terão **health checks** configurados (HEALTHCHECK) para monitoramento de saúde.
15. Os containers essenciais terão política de reinício automática configurada (`restart: unless-stopped`).
16. Os containers terão **limites de CPU e memória** definidos para evitar que consumam todos os recursos do host.
17. Sempre que possível, serão utilizadas **imagens otimizadas e leves** (ex.: Alpine) para reduzir tamanho e tempo de build.
18. O Docker Compose permitirá **escalabilidade**, configurando **réplicas de containers** para backend e frontends quando necessário, utilizando a diretiva `deploy` do Docker Compose v3.
19. O Nginx será integrado ao Docker Compose para atuar como **load balancer** e roteamento entre os containers replicados, com:
   - **Configuração SSL/TLS** obrigatória para produção
   - **Certificados SSL** gerenciados via volume `./nginx/ssl:/etc/nginx/ssl`
   - **Headers de segurança** (HSTS, X-Frame-Options, etc.)
   - **Redirecionamento automático** de HTTP (80) para HTTPS (443)
20. **Dependências de inicialização** serão configuradas para evitar dependência circular:
   - Nginx dependerá dos frontends usando `depends_on` com `condition: service_healthy`
   - Frontends dependerão do backend usando `depends_on` com `condition: service_healthy`
   - Backend será o primeiro a inicializar, seguido pelos frontends, e por último o Nginx
   - Health checks obrigatórios em todos os serviços críticos para garantir inicialização ordenada
21. o jwt usará um par de chaves rsa, gerada automaticamente quando o backend for inicializado. 

## Variáveis de Ambiente

20. O projeto terá variáveis de ambiente para **desenvolvimento** (locais).
21. O projeto terá variáveis de ambiente para **produção**, com domínio `sindaco.com.br`.
22. Em desenvolvimento, o sistema utilizará **Hogmail** para captura de emails.
23. Em produção, o sistema utilizará um **serviço SMTP configurado no backend** para envio de emails.

## Configurações de Segurança e Performance

24. **Redis** terá configurações avançadas de segurança:
   - Senha obrigatória para acesso (REDIS_PASSWORD)
   - Configuração de memória máxima para evitar overconsumption
   - Policy de remoção de chaves (LRU) quando atingir limite de memória
   - Persistência configurada com appendfsync para balance entre performance e durabilidade

25. **PostgreSQL** terá configurações otimizadas:
   - Timezone configurado para America/Sao_Paulo
   - Configurações de performance ajustadas para o ambiente
   - Backup automático configurado

26. **Ambientes segregados** usando Docker Compose override:
   - Desenvolvimento: configurações locais com debug habilitado
   - Produção: configurações otimizadas para performance e segurança
   - Staging: ambiente intermediário para testes

27. **Estratégias de inicialização ordenada**:
   - Uso de `depends_on` com condições de saúde para evitar dependências circulares
   - Health checks configurados em todos os serviços críticos
   - Timeouts apropriados para aguardar serviços dependentes
   - Restart policies configuradas para recuperação automática de falhas

28. **Configurações SSL/TLS do Nginx**:
   - **Certificados SSL** obrigatórios para produção (Let's Encrypt ou certificados próprios)
   - **Protocolos seguros**: TLSv1.2 e TLSv1.3 apenas
   - **Ciphers seguros** configurados para evitar vulnerabilidades
   - **Headers de segurança**: HSTS, X-Content-Type-Options, X-Frame-Options, CSP
   - **Redirecionamento forçado** de HTTP para HTTPS em produção
   - **OCSP Stapling** habilitado para melhor performance SSL

## Controle de Acesso e Redirecionamento

29. O sistema terá **três níveis de usuário**: `administrador`, `fundador` e `usuario`.
30. Usuários com nível **administrador** carregarão o **frontend-admin**.
31. Usuários com nível **fundador** carregarão o **frontend-fundador**.
32. Usuários com nível **usuario** carregarão o **frontend-usuario**.
33. Usuários **não autenticados** carregarão o **frontend-publico**.
