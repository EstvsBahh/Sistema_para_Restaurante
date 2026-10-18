from datetime import datetime
from extensions import db


class Garcom(db.Model):
    __tablename__ = "garcons"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(30))
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.now)

    pedidos = db.relationship("Pedido", back_populates="garcom", lazy="dynamic")

    @property
    def iniciais(self):
        partes = [p for p in self.nome.split() if p]
        if not partes:
            return "?"
        if len(partes) == 1:
            return partes[0][0].upper()
        return (partes[0][0] + partes[-1][0]).upper()

    @property
    def pedidos_ativos(self):
        from models.pedido import Pedido
        return self.pedidos.filter(Pedido.status.in_(Pedido.ATIVOS)).count()