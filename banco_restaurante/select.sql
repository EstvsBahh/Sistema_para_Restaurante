SELECT 
    p.nome AS produto,
    p.preco,
    p.quantidade_estoque,
    c.nome AS categoria
FROM Produto p
INNER JOIN Categoria c
ON p.categoria_id = c.id;