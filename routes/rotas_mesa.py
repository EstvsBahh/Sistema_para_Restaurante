from flask import Blueprint, render_template, request, redirect, url_for
from extensions import db
from models.mesa import Mesa

mesa_bp = Blueprint("mesa", __name__, url_prefix="/mesas")


@mesa_bp.route("/", methods=["GET"])
def listar_mesas():
    mesas = Mesa.query.order_by(Mesa.numero).all()
    return render_template("mesas.html", mesas=mesas)


@mesa_bp.route("/nova", methods=["POST"])
def cadastrar_mesa():
    numero = request.form.get("numero")
    mesa = Mesa(numero=numero, situacao="livre")
    db.session.add(mesa)
    db.session.commit()
    return redirect(url_for("mesa.listar_mesas"))


@mesa_bp.route("/<int:numero>/liberar", methods=["POST"])
def liberar_mesa(numero):
    mesa = Mesa.query.get_or_404(numero)
    mesa.liberar()
    db.session.commit()
    return redirect(url_for("mesa.listar_mesas"))
