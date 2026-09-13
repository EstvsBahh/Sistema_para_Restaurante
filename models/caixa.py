from extensions import db

class Caixa(db.Model):
    __tablename__ = "caixa"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
