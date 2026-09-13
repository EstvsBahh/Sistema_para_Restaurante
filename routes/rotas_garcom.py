from flask import Blueprint, render_template, request, redirect, url_for
from extensions import db
from models.garcom import Garcom

garcom_bp = Blueprint("garcom", __name__, url_prefix="/garcons")

@garcom_bp.route("/", methods=["GET"])
def listar_garcons():
    garcons = Garcom.query.order_by(Garcom.nome).all()
    return render_template("garcons.html", garcons=garcons)

@garcom_bp.route("/novo", methods=["POST"])
def cadastrar_garcom():
    nome = request.form.get("nome")

    garcom = Garcom(nome=nome)

    db.session.add(garcom)
    db.session.commit()

    return redirect(url_for("garcom.listar_garcons"))