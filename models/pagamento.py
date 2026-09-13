from datetime import datetime
from extensions import db

class Pagamento(db.Model):
    __tablename__ = "pagamento"

    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    forma_pagamento = db.Column(db.String(20), nullable=False)  # dinheiro, cartao, pix
    situacao = db.Column(db.String(20), default="pendente")
    data_hora = db.Column(db.DateTime, default=datetime.utcnow)

    pedido_numero = db.Column(db.Integer, db.ForeignKey("pedido.numero"), unique=True, nullable=False)

    def confirmar_pagamento(self):
        self.situacao = "confirmado"
