from extensions import db


class Mesa(db.Model):
    __tablename__ = "mesas"

    LIVRE = "livre"
    OCUPADA = "ocupada"
    RESERVADA = "reservada"
    STATUS = {LIVRE: "Livre", OCUPADA: "Ocupada", RESERVADA: "Reservada"}

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, nullable=False, unique=True)
    capacidade = db.Column(db.Integer, nullable=False, default=4)
    status = db.Column(db.String(20), nullable=False, default=LIVRE, index=True)

    pedidos = db.relationship("Pedido", back_populates="mesa", lazy="dynamic")

    def __init__(self, **kwargs):
        kwargs.setdefault("status", self.LIVRE)
        kwargs.setdefault("capacidade", 4)
        super().__init__(**kwargs)

    @property
    def status_label(self):
        return self.STATUS.get(self.status, self.status)

    @property
    def pedido_ativo(self):
        from models.pedido import Pedido
        return (
            self.pedidos.filter(Pedido.status.in_(Pedido.ATIVOS))
            .order_by(Pedido.id.desc())
            .first()
        )

    def ocupar(self):
        self.status = self.OCUPADA

    def liberar(self):
        self.status = self.LIVRE

    def reservar(self):
        self.status = self.RESERVADA