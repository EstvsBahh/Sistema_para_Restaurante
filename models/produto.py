class Produto:
    def __init__(self, nome, preco, categoria, quantidade_estoque=0, estoque_minimo=0):
        self.nome = nome
        self.preco = preco
        self.categoria = categoria
        self.quantidade_estoque = quantidade_estoque
        self.estoque_minimo = estoque_minimo
        self.disponibilidade = quantidade_estoque > 0
