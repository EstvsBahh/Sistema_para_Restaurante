-- CATEGORIAS
INSERT INTO Categoria (nome, descricao) VALUES
('Hambúrgueres', 'Hambúrgueres artesanais'),
('Pizzas', 'Pizzas salgadas'),
('Bebidas', 'Bebidas geladas'),
('Sobremesas', 'Sobremesas variadas');

-- MESAS
INSERT INTO Mesa (numero, capacidade, status) VALUES
(1, 4, 'Livre'),
(2, 4, 'Livre'),
(3, 2, 'Livre'),
(4, 6, 'Livre'),
(5, 8, 'Livre');

-- GARÇONS
INSERT INTO Garcom (nome, telefone) VALUES
('Carlos', '67999990001'),
('Mariana', '67999990002'),
('João', '67999990003');

-- PRODUTOS
INSERT INTO Produto
(nome, descricao, preco, disponibilidade, quantidade_estoque, estoque_minimo, categoria_id)
VALUES
('X-Burger', 'Hambúrguer com carne, queijo e molho', 25.90, TRUE, 20, 5, 1),
('X-Salada', 'Hambúrguer com carne, queijo e salada', 28.90, TRUE, 15, 5, 1),
('Pizza Calabresa', 'Pizza de calabresa e queijo', 45.00, TRUE, 10, 3, 2),
('Pizza Frango', 'Pizza de frango com catupiry', 48.00, TRUE, 8, 3, 2),
('Coca-Cola', 'Refrigerante lata 350ml', 6.00, TRUE, 30, 10, 3),
('Suco de Laranja', 'Suco natural de laranja', 8.00, TRUE, 12, 5, 3),
('Pudim', 'Pudim de leite condensado', 10.00, TRUE, 6, 2, 4),
('Brownie', 'Brownie de chocolate', 12.00, TRUE, 7, 2, 4);

-- CAIXA
INSERT INTO Caixa (valor_inicial, status)
VALUES (100.00, 'Aberto');