from extensions import db

class Garcom(db.Model):
    __tablename__ = "garcom"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)

    pedidos = db.relationship("Pedido", backref="garcom", lazy=True)
