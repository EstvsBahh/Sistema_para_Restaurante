from extensions import db

class Mesa(db.Model):
    __tablename__ = "mesa"

    numero = db.Column(db.Integer, primary_key=True)
    situacao = db.Column(db.String(20), nullable=False, default="livre")

    pedidos = db.relationship("Pedido", backref="mesa", lazy=True)

    def ocupar(self):
        self.situacao = "ocupada"

    def liberar(self):
        self.situacao = "livre"
