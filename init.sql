-- Inicialização do banco de dados
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabela de usuários
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de produtos (exemplo)
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    stock INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inserir dados de exemplo
INSERT INTO users (name, email, password_hash) VALUES 
('Admin', 'admin@sistema.com', '$2a$10$example_hash_here'),
('Usuario Teste', 'user@sistema.com', '$2a$10$example_hash_here')
ON CONFLICT (email) DO NOTHING;

INSERT INTO products (name, description, price, stock) VALUES 
('Produto 1', 'Descrição do produto 1', 29.99, 100),
('Produto 2', 'Descrição do produto 2', 49.99, 50),
('Produto 3', 'Descrição do produto 3', 19.99, 200)
ON CONFLICT DO NOTHING;