from datetime import datetime
from decimal import Decimal

from extensions import db

class Pagamento(db.Model):
    __tablename__ = "pagamentos"

    DINHEIRO = "dinheiro"
    CARTAO = "cartao"
    PIX = "pix"
    FORMAS = {DINHEIRO: "Dinheiro", CARTAO: "Cartão", PIX: "Pix"}

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedidos.id"), nullable=False, unique=True)
    caixa_id = db.Column(db.Integer, db.ForeignKey("caixas.id"), nullable=False, index=True)
    forma = db.Column(db.String(20), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)  
    taxa_servico = db.Column(db.Numeric(10, 2), nullable=False, default=0) 
    valor_recebido = db.Column(db.Numeric(10, 2)) 
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.now)

    pedido = db.relationship("Pedido", back_populates="pagamento")
    caixa = db.relationship("Caixa", back_populates="pagamentos")

    def __init__(self, **kwargs):
        kwargs.setdefault("taxa_servico", Decimal("0.00"))
        super().__init__(**kwargs)

    @property
    def subtotal(self):
        return Decimal(str(self.valor)) - Decimal(str(self.taxa_servico))

    @property
    def taxa_cobrada(self):
        return Decimal(str(self.taxa_servico)) > 0

    @property
    def forma_label(self):
        return self.FORMAS.get(self.forma, self.forma)

    @property
    def troco(self):
        if self.forma == self.DINHEIRO and self.valor_recebido is not None:
            return max(Decimal(str(self.valor_recebido)) - Decimal(str(self.valor)), Decimal("0"))
        return Decimal("0")
