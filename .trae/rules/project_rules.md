# Especificações do Projeto

## Estrutura de Containers e Serviços

1. O projeto contém um container chamado **backend**, iniciado no diretório `backend`.
2. O projeto contém um container chamado **frontend-admin**, iniciado no diretório `frontend-admin`.
3. O projeto contém um container chamado **frontend-fundador**, iniciado no diretório `frontend-admin`.
4. O projeto contém um container chamado **frontend-usuario**, iniciado no diretório `frontend-usuario`.
5. O projeto terá um container chamado **frontend-publico**.
6. O projeto terá um container para desenvolvimento de um aplicativo **React Native**, que se conecta ao backend.
7. O Docker Compose inclui **Nginx** como servidor reverso.
8. O Docker Compose inclui **PostgreSQL** como banco de dados.
9. O Docker Compose incluirá **Redis** como serviço de cache, com volume próprio para persistência de dados temporários.
10. O projeto terá um container separado para **serviço de logs**, com volume próprio para persistência.
11. Todos os containers do projeto serão conectados a uma **rede interna** para comunicação segura.
12. Serão criados **volumes dedicados** para persistência de dados do PostgreSQL, para armazenamento do backend, logs, uploads e cache Redis, cada um em volume próprio.
13. O projeto terá ambientes separados de **desenvolvimento** e **produção**, configurados no Docker Compose.
14. Os containers críticos, como **backend**, **PostgreSQL** e **Redis**, terão **health checks** configurados (HEALTHCHECK) para monitoramento de saúde.
15. Os containers essenciais terão política de reinício automática configurada (`restart: unless-stopped`).
16. Os containers terão **limites de CPU e memória** definidos para evitar que consumam todos os recursos do host.
17. Sempre que possível, serão utilizadas **imagens otimizadas e leves** (ex.: Alpine) para reduzir tamanho e tempo de build.
18. O Docker Compose permitirá **escalabilidade**, configurando **réplicas de containers** para backend e frontends quando necessário, utilizando a diretiva `deploy` do Docker Compose v3.
19. O Nginx será integrado ao Docker Compose para atuar como **load balancer** e roteamento entre os containers replicados.

## Variáveis de Ambiente

20. O projeto terá variáveis de ambiente para **desenvolvimento** (locais).
21. O projeto terá variáveis de ambiente para **produção**, com domínio `sindaco.com.br`.
22. Em desenvolvimento, o sistema utilizará **Hogmail** para captura de emails.
23. Em produção, o sistema utilizará um **serviço SMTP configurado no backend** para envio de emails.

## Controle de Acesso e Redirecionamento

24. O sistema terá **três níveis de usuário**: `administrador`, `fundador` e `usuario`.
25. Usuários com nível **administrador** carregarão o **frontend-admin**.
26. Usuários com nível **fundador** carregarão o **frontend-fundador**.
27. Usuários com nível **usuario** carregarão o **frontend-usuario**.
28. Usuários **não autenticados** carregarão o **frontend-publico**.
