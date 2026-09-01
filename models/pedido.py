from models.item_pedido import ItemPedido


class Pedido:
    def __init__(self, mesa, garcom):
        self.mesa = mesa
        self.garcom = garcom
        self.itens = []
        self.estado = "aberto"
        self.valor_total = 0

    def adicionar_item(self, produto, quantidade):
        item = ItemPedido(produto, quantidade)
        self.itens.append(item)
        self.calcular_total()

    def calcular_total(self):
        self.valor_total = sum(item.calcular_subtotal() for item in self.itens)
        return self.valor_total

    def finalizar(self):
        self.estado = "finalizado"
        self.mesa.liberar()
