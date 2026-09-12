CREATE DATABASE restaurante;
USE restaurante;

-- 1. MESA
CREATE TABLE Mesa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero INT NOT NULL,
    capacidade INT NOT NULL,
    status VARCHAR(20) DEFAULT 'Livre'
);

-- 2. CATEGORIA
CREATE TABLE Categoria (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao VARCHAR(255)
);

-- 3. PRODUTO
CREATE TABLE Produto (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao VARCHAR(255),
    preco DECIMAL(10,2) NOT NULL,
    disponibilidade BOOLEAN DEFAULT TRUE,
    quantidade_estoque INT DEFAULT 0,
    estoque_minimo INT DEFAULT 5,
    categoria_id INT NOT NULL,

    FOREIGN KEY (categoria_id) REFERENCES Categoria(id)
);

-- 4. GARÇOM
CREATE TABLE Garcom (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    telefone VARCHAR(20)
);

-- 5. PEDIDO
CREATE TABLE Pedido (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mesa_id INT NOT NULL,
    garcom_id INT NOT NULL,
    data_pedido DATETIME DEFAULT CURRENT_TIMESTAMP,
    situacao VARCHAR(30) DEFAULT 'Aberto',
    valor_total DECIMAL(10,2) DEFAULT 0.00,

    FOREIGN KEY (mesa_id) REFERENCES Mesa(id),
    FOREIGN KEY (garcom_id) REFERENCES Garcom(id)
);

-- 6. ITEM PEDIDO
CREATE TABLE ItemPedido (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pedido_id INT NOT NULL,
    produto_id INT NOT NULL,
    quantidade INT NOT NULL,
    preco_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,

    FOREIGN KEY (pedido_id) REFERENCES Pedido(id),
    FOREIGN KEY (produto_id) REFERENCES Produto(id)
);

-- 7. CAIXA
CREATE TABLE Caixa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    data_abertura DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_fechamento DATETIME,
    valor_inicial DECIMAL(10,2) DEFAULT 0.00,
    valor_final DECIMAL(10,2),
    status VARCHAR(20) DEFAULT 'Aberto'
);

-- 8. PAGAMENTO
CREATE TABLE Pagamento (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pedido_id INT NOT NULL,
    caixa_id INT NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    forma_pagamento VARCHAR(30) NOT NULL,
    data_pagamento DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (pedido_id) REFERENCES Pedido(id),
    FOREIGN KEY (caixa_id) REFERENCES Caixa(id)
);