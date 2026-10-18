from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import func

from extensions import db
from models.categoria import Categoria

categoria_bp = Blueprint("categorias", __name__, url_prefix="/categorias")


def _nome_existe(nome, ignorar_id=None):
   consulta = Categoria.query.filter(func.lower(Categoria.nome) == nome.lower())
   if ignorar_id:
      consulta = consulta.filter(Categoria.id != ignorar_id)
   return consulta.first() is not None

@categoria_bp.route("/")
def listar():
   categorias = Categoria.query.order_by(Categoria.nome).all()
   return render_template("categorias.html", categorias=categorias)


@categoria_bp.route("/nova", methods=["POST"])
def criar():
   nome = request.form.get("nome", "").strip()
   descricao = request.form.get("descricao", "").strip() or None

   if not nome:
      flash("Informe o nome da categoria.", "danger")
   elif _nome_existe(nome):
      flash(f"A categoria \"{nome}\" já existe.", "warning")
   else:
      db.session.add(Categoria(nome=nome, descricao=descricao))
      db.session.commit()
      flash("Categoria cadastrada com sucesso.", "success")
   return redirect(url_for("categorias.listar"))


@categoria_bp.route("/<int:categoria_id>/editar", methods=["POST"])
def editar(categoria_id):
   categoria = db.get_or_404(Categoria, categoria_id)
   nome = request.form.get("nome", "").strip()
   descricao = request.form.get("descricao", "").strip() or None

   if not nome:
      flash("Informe o nome da categoria.", "danger")
   elif _nome_existe(nome, ignorar_id=categoria.id):
      flash(f"Já existe outra categoria chamada \"{nome}\".", "warning")
   else:
      categoria.nome = nome
      categoria.descricao = descricao
      db.session.commit()
      flash("Categoria atualizada.", "success")
   return redirect(url_for("categorias.listar"))


@categoria_bp.route("/<int:categoria_id>/excluir", methods=["POST"])
def excluir(categoria_id):
   categoria = db.get_or_404(Categoria, categoria_id)
   if categoria.produtos.count():
      flash("Esta categoria possui produtos. Mova ou remova os produtos antes de excluí-la.", "warning")
   else:
      db.session.delete(categoria)
      db.session.commit()
      flash("Categoria excluída.", "success")
   return redirect(url_for("categorias.listar"))
