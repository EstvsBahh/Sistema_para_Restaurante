class Mesa:
    def __init__(self, numero):
        self.numero = numero
        self.situacao = "livre"

    def ocupar(self):
        self.situacao = "ocupada"

    def liberar(self):
        self.situacao = "livre"
