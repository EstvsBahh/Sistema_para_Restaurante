from flask import Blueprint, render_template, request, redirect, url_for
from extensions import db
from models.produto import Produto
from models.categoria import Categoria

produto_bp = Blueprint("produto", __name__, url_prefix="/produtos")

@produto_bp.route("/", methods=["GET"])
def listar_produtos():
    produtos = Produto.query.order_by(Produto.nome).all()
    categorias = Categoria.query.order_by(Categoria.nome).all()

    return render_template(
        "produtos.html",
        produtos=produtos,
        categorias=categorias
    )

@produto_bp.route("/novo", methods=["POST"])
def cadastrar_produto():
    produto = Produto(
        nome=request.form.get("nome"),
        descricao=request.form.get("descricao"),
        preco=request.form.get("preco"),
        categoria_id=request.form.get("categoria_id"),
        quantidade_estoque=int(request.form.get("quantidade_estoque", 0)),
        estoque_minimo=int(request.form.get("estoque_minimo", 0)),
        disponivel=int(request.form.get("quantidade_estoque", 0)) > 0,
    )

    db.session.add(produto)
    db.session.commit()

    return redirect(url_for("produto.listar_produtos"))

@produto_bp.route("/<int:produto_id>/entrada-estoque", methods=["POST"])
def entrada_estoque(produto_id):
    produto = Produto.query.get_or_404(produto_id)
    quantidade = int(request.form.get("quantidade", 0))

    produto.dar_entrada_estoque(quantidade)
    db.session.commit()

    return redirect(url_for("produto.listar_produtos"))

@produto_bp.route("/estoque", methods=["GET"])
def ver_estoque():
    produtos = Produto.query.order_by(Produto.nome).all()
    return render_template("estoque.html", produtos=produtos)

@produto_bp.route("/<int:produto_id>/remover-cardapio", methods=["POST"])
def remover_do_cardapio(produto_id):
    produto = Produto.query.get_or_404(produto_id)
    produto.disponivel = False

    db.session.commit()

    return redirect(url_for("produto.listar_produtos"))

@produto_bp.route("/<int:produto_id>/voltar-cardapio", methods=["POST"])
def voltar_ao_cardapio(produto_id):
    produto = Produto.query.get_or_404(produto_id)
    produto.disponivel = True

    db.session.commit()

    return redirect(url_for("produto.listar_produtos"))