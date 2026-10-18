from decimal import Decimal


from extensions import db


class ItemPedido(db.Model):
    __tablename__ = "itens_pedido"

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedidos.id"), nullable=False, index=True)
    produto_id = db.Column(db.Integer, db.ForeignKey("produtos.id"), nullable=False, index=True)
    quantidade = db.Column(db.Integer, nullable=False)

    preco_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    observacao = db.Column(db.String(200))

    pedido = db.relationship("Pedido", back_populates="itens")
    produto = db.relationship("Produto", back_populates="itens")

    __table_args__ = (db.CheckConstraint("quantidade > 0", name="ck_item_quantidade"),)

    @property
    def subtotal(self):
        return Decimal(str(self.preco_unitario)) * self.quantidade