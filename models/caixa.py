class Caixa:
    def __init__(self, nome):
        self.nome = nome

    def registrar_pagamento(self, pedido):
        print(f"Caixa {self.nome} registrou o pagamento de R$ {pedido.valor_total:.2f}")

    def fechar_conta(self, pedido):
        pedido.finalizar()
        print(f"Caixa {self.nome} finalizou o pedido e liberou a mesa {pedido.mesa.numero}")
