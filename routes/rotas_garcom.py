from flask import Blueprint, flash, redirect, render_template, request, url_for

from extensions import db
from models.garcom import Garcom


garcom_bp = Blueprint("garcons", __name__, url_prefix="/garcons")

@garcom_bp.route("/")
def listar():
   garcons = Garcom.query.order_by(Garcom.nome).all()
   return render_template("garcons.html", garcons=garcons)


@garcom_bp.route("/novo", methods=["POST"])
def criar():
   nome = request.form.get("nome", "").strip()
   telefone = request.form.get("telefone", "").strip() or None


   if not nome:
      flash("Informe o nome do garçom.", "danger")
   else:
      db.session.add(Garcom(nome=nome, telefone=telefone))
      db.session.commit()
      flash(f"Garçom {nome} cadastrado.", "success")
   return redirect(url_for("garcons.listar"))


@garcom_bp.route("/<int:garcom_id>/editar", methods=["POST"])
def editar(garcom_id):
  garcom = db.get_or_404(Garcom, garcom_id)
  nome = request.form.get("nome", "").strip()


  if not nome:
     flash("Informe o nome do garçom.", "danger")
  else:
     garcom.nome = nome
     garcom.telefone = request.form.get("telefone", "").strip() or None
     db.session.commit()
     flash("Dados do garçom atualizados.", "success")
  return redirect(url_for("garcons.listar"))


@garcom_bp.route("/<int:garcom_id>/alternar", methods=["POST"])
def alternar(garcom_id):
  garcom = db.get_or_404(Garcom, garcom_id)
  if garcom.ativo and garcom.pedidos_ativos:
     flash(f"{garcom.nome} ainda tem pedidos em andamento.", "warning")
  else:
     garcom.ativo = not garcom.ativo
     db.session.commit()
     flash(f"{garcom.nome} agora está {'ativo' if garcom.ativo else 'inativo'}.", "success")
  return redirect(url_for("garcons.listar"))


@garcom_bp.route("/<int:garcom_id>/excluir", methods=["POST"])
def excluir(garcom_id):
  garcom = db.get_or_404(Garcom, garcom_id)
  if garcom.pedidos.count():
     flash("Este garçom possui histórico de pedidos. Desative-o em vez de excluir.", "warning")
  else:
     db.session.delete(garcom)
     db.session.commit()
     flash("Garçom excluído.", "success")
  return redirect(url_for("garcons.listar"))
