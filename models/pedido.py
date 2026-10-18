from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from extensions import db
from models.item_pedido import ItemPedido


class Pedido(db.Model):
    __tablename__ = "pedidos"

    ABERTO = "aberto"
    EM_PREPARO = "em_preparo"
    PRONTO = "pronto"
    ENTREGUE = "entregue"
    PAGO = "pago"
    CANCELADO = "cancelado"

    STATUS = {
        ABERTO: "Aberto",
        EM_PREPARO: "Em preparo",
        PRONTO: "Pronto",
        ENTREGUE: "Entregue",
        PAGO: "Pago",
        CANCELADO: "Cancelado",
    }
    ATIVOS = (ABERTO, EM_PREPARO, PRONTO, ENTREGUE) # ainda em atendimento
    FLUXO = (ABERTO, EM_PREPARO, PRONTO, ENTREGUE, PAGO)
    PROXIMO = {ABERTO: EM_PREPARO, EM_PREPARO: PRONTO, PRONTO: ENTREGUE}

    # Taxa de serviço opcional, cobrada no caixa sobre o total do pedido (10%)
    TAXA_SERVICO = Decimal("0.10")

    id = db.Column(db.Integer, primary_key=True)
    mesa_id = db.Column(db.Integer, db.ForeignKey("mesas.id"), nullable=False, index=True)
    garcom_id = db.Column(db.Integer, db.ForeignKey("garcons.id"), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default=ABERTO, index=True)
    observacao = db.Column(db.String(255))
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.now)
    atualizado_em = db.Column(
        db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )

    mesa = db.relationship("Mesa", back_populates="pedidos")
    garcom = db.relationship("Garcom", back_populates="pedidos")
    itens = db.relationship(
        "ItemPedido", back_populates="pedido", cascade="all, delete-orphan", order_by="ItemPedido.id"
    )
    pagamento = db.relationship("Pagamento", back_populates="pedido", uselist=False)

    def __init__(self, **kwargs):
        kwargs.setdefault("status", self.ABERTO)
        super().__init__(**kwargs)

    @property
    def status_label(self):
        return self.STATUS.get(self.status, self.status)

    @property
    def ativo(self):
        return self.status in self.ATIVOS

    @property
    def aceita_itens(self):
        return self.status in self.ATIVOS

    @property
    def editavel(self):
        return self.status in (self.ABERTO, self.EM_PREPARO)

    @property
    def etapa_atual(self):
        return self.FLUXO.index(self.status) if self.status in self.FLUXO else -1

    @property
    def total(self):
        return sum((item.subtotal for item in self.itens), Decimal("0"))

    @property
    def taxa_servico_sugerida(self):
        return self.calcular_taxa_servico()

    @property
    def total_com_taxa(self):
        return self.total + self.calcular_taxa_servico()

    @property
    def quantidade_itens(self):
        return sum(item.quantidade for item in self.itens)

    @property
    def minutos_decorridos(self):
        return int((datetime.now() - self.criado_em).total_seconds() // 60)

    @property
    def urgencia(self):
        minutos = self.minutos_decorridos
        if minutos >= 25:
            return "atrasado"
        if minutos >= 12:
            return "atencao"
        return "normal"

    def calcular_taxa_servico(self):
        return (self.total * self.TAXA_SERVICO).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def adicionar_item(self, produto, quantidade, observacao=None):
        if not self.aceita_itens:
            raise ValueError("Este pedido não aceita novos itens.")
        if not produto.disponivel:
            raise ValueError(f"{produto.nome} não está disponível.")
        if quantidade <= 0:
            raise ValueError("A quantidade deve ser maior que zero.")

        observacao = (observacao or "").strip() or None
        produto.dar_baixa(quantidade)

        for item in self.itens:
            if item.produto_id == produto.id and (item.observacao or None) == observacao:
                item.quantidade += quantidade
                return item

        item = ItemPedido(
            produto=produto,
            quantidade=quantidade,
            preco_unitario=produto.preco,
            observacao=observacao,
        )
        self.itens.append(item)
        return item

    def remover_item(self, item):
        item.produto.dar_entrada(item.quantidade)
        self.itens.remove(item)

    def alterar_status(self, novo_status):
        self.status = novo_status

    def cancelar(self):
        for item in self.itens:
            item.produto.dar_entrada(item.quantidade)
        self.status = self.CANCELADO
        self.mesa.liberar()

    def marcar_pago(self):
        self.status = self.PAGO
        self.mesa.liberar()