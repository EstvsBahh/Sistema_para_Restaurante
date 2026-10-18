from datetime import datetime


from extensions import db


class Produto(db.Model):
    __tablename__ = "produtos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(255))
    preco = db.Column(db.Numeric(10, 2), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias.id"), nullable=False, index=True)
    estoque_atual = db.Column(db.Integer, nullable=False, default=0)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.now)

    categoria = db.relationship("Categoria", back_populates="produtos")
    itens = db.relationship("ItemPedido", back_populates="produto", lazy="dynamic")

    __table_args__ = (
        db.CheckConstraint("preco >= 0", name="ck_produto_preco"),
        db.CheckConstraint("estoque_atual >= 0", name="ck_produto_estoque"),
    )

    @property
    def esgotado(self):
        return self.estoque_atual <= 0

    @property
    def disponivel(self):
        return bool(self.ativo) and not self.esgotado

    @property
    def situacao_estoque(self):
        return "esgotado" if self.esgotado else "normal"

    def dar_entrada(self, quantidade):
        if quantidade <= 0:
            raise ValueError("A quantidade de entrada deve ser maior que zero.")
        self.estoque_atual += quantidade

    def dar_baixa(self, quantidade):
        if quantidade <= 0:
            raise ValueError("A quantidade deve ser maior que zero.")
        if quantidade > self.estoque_atual:
            raise ValueError(
                f"Estoque insuficiente de {self.nome} (disponível: {self.estoque_atual})."
            )
        self.estoque_atual -= quantidade