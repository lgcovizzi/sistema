FROM golang:1.21-alpine AS builder

# Instalar dependências do sistema
RUN apk add --no-cache git

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY go.mod go.sum ./

# Baixar dependências
RUN go mod download

# Copiar código fonte
COPY . .

# Compilar aplicação
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

# Estágio final
FROM alpine:latest

# Instalar ca-certificates para HTTPS
RUN apk --no-cache add ca-certificates

# Criar usuário não-root
RUN adduser -D -s /bin/sh appuser

WORKDIR /app

# Copiar binário do estágio builder
COPY --from=builder /app/main .

# Copiar templates
COPY --from=builder /app/templates ./templates

# Alterar permissões
RUN chown -R appuser:appuser /app

# Mudar para usuário não-root
USER appuser

# Expor porta
EXPOSE 3000

# Comando para executar
CMD ["./main"]