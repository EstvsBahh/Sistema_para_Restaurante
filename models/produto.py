from extensions import db

class Produto(db.Model):
    __tablename__ = "produto"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    descricao = db.Column(db.String(255))
    preco = db.Column(db.Numeric(10, 2), nullable=False)
    disponivel = db.Column(db.Boolean, default=True)
    quantidade_estoque = db.Column(db.Integer, nullable=False, default=0)
    estoque_minimo = db.Column(db.Integer, nullable=False, default=0)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categoria.id"), nullable=False)

    def dar_entrada_estoque(self, quantidade: int):
        self.quantidade_estoque += quantidade

        if self.quantidade_estoque > 0:
            self.disponivel = True

    def dar_baixa_estoque(self, quantidade: int):
        self.quantidade_estoque -= quantidade

        if self.quantidade_estoque <= 0:
            self.quantidade_estoque = 0
            self.disponivel = False

    def estoque_baixo(self) -> bool:
        return self.quantidade_estoque <= self.estoque_minimo