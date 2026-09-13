from app import criar_app
from extensions import db
from models.mesa import Mesa
from models.categoria import Categoria
from models.produto import Produto
from models.garcom import Garcom

app = criar_app()

with app.app_context():
    if not Mesa.query.first():
        db.session.add_all([Mesa(numero=1), Mesa(numero=2), Mesa(numero=3)])

    if not Categoria.query.first():
        pratos = Categoria(nome="Pratos principais")
        bebidas = Categoria(nome="Bebidas")
        db.session.add_all([pratos, bebidas])
        db.session.flush()

        db.session.add_all([
            Produto(nome="Filé Mignon ao Molho Madeirense", preco=35.00, categoria_id=pratos.id,
                    quantidade_estoque=10, estoque_minimo=5, disponivel=True),
            Produto(nome="Coca-Cola", preco=8.00, categoria_id=bebidas.id,
                    quantidade_estoque=20, estoque_minimo=5, disponivel=True),
        ])

    if not Garcom.query.first():
        db.session.add_all([Garcom(nome="Bárbara"), Garcom(nome="Kamilly"), Garcom(nome="Gabriel"), Garcom(nome="Julia")])

    db.session.commit()
    print("Dados de teste inseridos com sucesso")
