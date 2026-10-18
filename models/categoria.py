from extensions import db


class Categoria(db.Model):
    __tablename__ = "categorias"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False, unique=True)
    descricao = db.Column(db.String(255))

    produtos = db.relationship(
        "Produto", back_populates="categoria", lazy="dynamic", order_by="Produto.nome"
    )