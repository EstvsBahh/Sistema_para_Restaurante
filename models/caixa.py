from datetime import datetime
from decimal import Decimal
from extensions import db


ZERO = Decimal("0.00")
FORMA_DINHEIRO = "dinheiro"  

class Caixa(db.Model):
    __tablename__ = "caixas"

    ABERTO = "aberto"
    FECHADO = "fechado"

    id = db.Column(db.Integer, primary_key=True)
    responsavel = db.Column(db.String(80), nullable=False)
    status = db.Column(db.String(20), nullable=False, default=ABERTO, index=True)
    saldo_inicial = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    saldo_final = db.Column(db.Numeric(10, 2))  
    aberto_em = db.Column(db.DateTime, nullable=False, default=datetime.now)
    fechado_em = db.Column(db.DateTime)
    observacao = db.Column(db.String(255))

    pagamentos = db.relationship(
        "Pagamento", back_populates="caixa", order_by="Pagamento.id.desc()"
    )
    movimentacoes = db.relationship(
        "MovimentacaoCaixa",
        back_populates="caixa",
        cascade="all, delete-orphan",
        order_by="MovimentacaoCaixa.id.desc()",
    )

    def __init__(self, **kwargs):
        kwargs.setdefault("status", self.ABERTO)
        kwargs.setdefault("saldo_inicial", ZERO)
        super().__init__(**kwargs)

    @classmethod
    def atual(cls):
        """Retorna o caixa aberto no momento (ou None)."""
        return cls.query.filter_by(status=cls.ABERTO).order_by(cls.id.desc()).first()

    @property
    def aberto(self):
        return self.status == self.ABERTO

    # ---- totais ----
    def total_forma(self, forma):
        return sum((Decimal(str(p.valor)) for p in self.pagamentos if p.forma == forma), ZERO)

    @property
    def total_recebido(self):
        return sum((Decimal(str(p.valor)) for p in self.pagamentos), ZERO)

    @property
    def total_taxas(self):
        """Soma da taxa de serviço arrecadada nesta sessão."""
        return sum((Decimal(str(p.taxa_servico)) for p in self.pagamentos), ZERO)

    @property
    def total_entradas(self):
        return sum(
            (Decimal(str(m.valor)) for m in self.movimentacoes if m.tipo == MovimentacaoCaixa.ENTRADA),
            ZERO,
        )

    @property
    def total_saidas(self):
        return sum(
            (Decimal(str(m.valor)) for m in self.movimentacoes if m.tipo == MovimentacaoCaixa.SAIDA),
            ZERO,
        )

    @property
    def saldo_dinheiro_esperado(self):
        """Dinheiro que deveria estar na gaveta: inicial + vendas em dinheiro + entradas - saídas."""
        return (
            Decimal(str(self.saldo_inicial))
            + self.total_forma(FORMA_DINHEIRO)
            + self.total_entradas
            - self.total_saidas
        )

    @property
    def diferenca(self):
        """Sobra (+) ou falta (-) apurada no fechamento."""
        if self.saldo_final is None:
            return None
        return Decimal(str(self.saldo_final)) - self.saldo_dinheiro_esperado

    def fechar(self, saldo_final, observacao=None):
        self.status = self.FECHADO
        self.saldo_final = saldo_final
        self.fechado_em = datetime.now()
        self.observacao = observacao


class MovimentacaoCaixa(db.Model):
    """Entrada (suprimento) ou saída (sangria) de dinheiro do caixa."""
    __tablename__ = "movimentacoes_caixa"

    ENTRADA = "entrada"
    SAIDA = "saida"
    TIPOS = {ENTRADA: "Suprimento (entrada)", SAIDA: "Sangria (saída)"}

    id = db.Column(db.Integer, primary_key=True)
    caixa_id = db.Column(db.Integer, db.ForeignKey("caixas.id"), nullable=False, index=True)
    tipo = db.Column(db.String(10), nullable=False)
    descricao = db.Column(db.String(150), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.now)

    caixa = db.relationship("Caixa", back_populates="movimentacoes")

    @property
    def tipo_label(self):
        return self.TIPOS.get(self.tipo, self.tipo)
