
from app import create_app
from extensions import db
from models import Categoria, Garcom, Mesa, Produto

CATEGORIAS = ["Entradas", "Pratos Principais", "Bebidas", "Sobremesas"]

PRODUTOS = [
    ("Bruschetta", "Pão italiano, tomate e manjericão", "24.90", "Entradas", 30),
    ("Porção de Batata Frita", "Crocante, serve 2 pessoas", "32.00", "Entradas", 25),
    ("Feijoada Completa", "Serve 2 pessoas", "69.90", "Pratos Principais", 20),
    ("Filé à Parmegiana", "Com arroz e batata frita", "54.90", "Pratos Principais", 15),
    ("Risoto de Cogumelos", "Arroz arbóreo e cogumelos frescos", "48.50", "Pratos Principais", 12),
    ("Refrigerante Lata", "350 ml", "7.00", "Bebidas", 60),
    ("Suco Natural", "500 ml, sabores do dia", "12.00", "Bebidas", 40),
    ("Água Mineral", "500 ml", "5.00", "Bebidas", 50),
    ("Cerveja Long Neck", "330 ml", "14.00", "Bebidas", 48),
    ("Pudim de Leite", "Receita da casa", "16.00", "Sobremesas", 14),
    ("Petit Gâteau", "Com sorvete de creme", "26.90", "Sobremesas", 10),
]
MESAS = [(1, 2), (2, 2), (3, 4), (4, 4), (5, 4), (6, 4), (7, 6), (8, 6), (9, 8), (10, 8)]
GARCONS = [("Bárbara", "(18) 99188-7184")]


def popular():
    app = create_app()
    with app.app_context():
        if Categoria.query.first():
            print("O banco já possui dados. Nada foi alterado.")
            return

        categorias = {nome: Categoria(nome=nome) for nome in CATEGORIAS}
        db.session.add_all(categorias.values())
        db.session.flush()

        for nome, descricao, preco, categoria, estoque in PRODUTOS:
            db.session.add(
                Produto(
                    nome=nome, descricao=descricao, preco=preco,
                    categoria_id=categorias[categoria].id,
                    estoque_atual=estoque, ativo=True,
                )
            )
        db.session.add_all(Mesa(numero=numero, capacidade=cap) for numero, cap in MESAS)
        db.session.add_all(Garcom(nome=nome, telefone=tel) for nome, tel in GARCONS)
        db.session.commit()
        print("Dados de exemplo inseridos: 4 categorias, 11 produtos, 10 mesas e 3 garçons.")


if __name__ == "__main__":
    popular()
