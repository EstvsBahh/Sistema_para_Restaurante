from extensions import db

class ItemPedido(db.Model):
    __tablename__ = "item_pedido"

    id = db.Column(db.Integer, primary_key=True)
    quantidade = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Numeric(10, 2), nullable=False)

    pedido_numero = db.Column(db.Integer, db.ForeignKey("pedido.numero"), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey("produto.id"), nullable=False)

    produto = db.relationship("Produto")

    def calcular_subtotal(self):
        return self.quantidade * self.preco_unitario
