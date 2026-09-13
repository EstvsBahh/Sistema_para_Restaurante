from datetime import datetime
from extensions import db

class Pedido(db.Model):
    __tablename__ = "pedido"

    numero = db.Column(db.Integer, primary_key=True)
    data_hora = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default="aberto")  # aberto, em_preparo, pronto, finalizado
    valor_total = db.Column(db.Numeric(10, 2), default=0)

    mesa_numero = db.Column(db.Integer, db.ForeignKey("mesa.numero"), nullable=False)
    garcom_id = db.Column(db.Integer, db.ForeignKey("garcom.id"), nullable=False)

    itens = db.relationship("ItemPedido", backref="pedido", lazy=True, cascade="all, delete-orphan")
    pagamento = db.relationship("Pagamento", backref="pedido", uselist=False, lazy=True)

    def calcular_total(self):
        self.valor_total = sum(item.calcular_subtotal() for item in self.itens)
        return self.valor_total

    def alterar_estado(self, novo_estado: str):
        self.estado = novo_estado

    def finalizar(self):
        self.estado = "finalizado"
