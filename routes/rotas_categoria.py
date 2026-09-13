from flask import Blueprint, render_template, request, redirect, url_for
from extensions import db
from models.categoria import Categoria

categoria_bp = Blueprint("categoria", __name__, url_prefix="/categorias")

@categoria_bp.route("/", methods=["GET"])
def listar_categorias():
    categorias = Categoria.query.order_by(Categoria.nome).all()
    return render_template("categorias.html", categorias=categorias)

@categoria_bp.route("/nova", methods=["POST"])
def cadastrar_categoria():
    nome = request.form.get("nome")
    categoria = Categoria(nome=nome)

    db.session.add(categoria)
    db.session.commit()

    return redirect(url_for("categoria.listar_categorias"))