from flask import Blueprint, flash, redirect, render_template, request, url_for
from extensions import db
from models.mesa import Mesa

mesa_bp = Blueprint("mesas", __name__, url_prefix="/mesas")


@mesa_bp.route("/")
def listar():
    filtro = request.args.get("status", "todas")
    consulta = Mesa.query.order_by(Mesa.numero)
    if filtro in Mesa.STATUS:
        consulta = consulta.filter(Mesa.status == filtro)

    contagem = {status: Mesa.query.filter_by(status=status).count() for status in Mesa.STATUS}
    contagem["todas"] = sum(contagem.values())
    return render_template("mesas.html", mesas=consulta.all(), filtro=filtro, contagem=contagem)


@mesa_bp.route("/nova", methods=["POST"])
def criar():
    numero = request.form.get("numero", type=int)
    capacidade = request.form.get("capacidade", default=4, type=int)

    if not numero or numero <= 0:
        flash("Informe um número de mesa válido.", "danger")
    elif not capacidade or capacidade <= 0:
        flash("A capacidade deve ser de pelo menos 1 lugar.", "danger")
    elif Mesa.query.filter_by(numero=numero).first():
        flash(f"A mesa {numero} já está cadastrada.", "warning")
    else:
        db.session.add(Mesa(numero=numero, capacidade=capacidade))
        db.session.commit()
        flash(f"Mesa {numero} cadastrada com sucesso.", "success")
    return redirect(url_for("mesas.listar"))


@mesa_bp.route("/<int:mesa_id>/editar", methods=["POST"])
def editar(mesa_id):
    mesa = db.get_or_404(Mesa, mesa_id)
    numero = request.form.get("numero", type=int)
    capacidade = request.form.get("capacidade", type=int)

    if not numero or numero <= 0 or not capacidade or capacidade <= 0:
        flash("Número e capacidade devem ser maiores que zero.", "danger")
    elif Mesa.query.filter(Mesa.numero == numero, Mesa.id != mesa.id).first():
        flash(f"Já existe outra mesa com o número {numero}.", "warning")
    else:
        mesa.numero = numero
        mesa.capacidade = capacidade
        db.session.commit()
        flash("Mesa atualizada.", "success")
    return redirect(url_for("mesas.listar"))


@mesa_bp.route("/<int:mesa_id>/status", methods=["POST"])
def alterar_status(mesa_id):
    mesa = db.get_or_404(Mesa, mesa_id)
    novo = request.form.get("status")

    if mesa.pedido_ativo:
        flash(f"A mesa {mesa.numero} tem um pedido em andamento.", "warning")
    elif novo == Mesa.RESERVADA:
        mesa.reservar()
        db.session.commit()
        flash(f"Mesa {mesa.numero} reservada.", "success")
    elif novo == Mesa.LIVRE:
        mesa.liberar()
        db.session.commit()
        flash(f"Mesa {mesa.numero} liberada.", "success")
    return redirect(url_for("mesas.listar"))


@mesa_bp.route("/<int:mesa_id>/excluir", methods=["POST"])
def excluir(mesa_id):
    mesa = db.get_or_404(Mesa, mesa_id)
    if mesa.pedidos.count():
        flash("Esta mesa possui histórico de pedidos e não pode ser excluída.", "warning")
    else:
        db.session.delete(mesa)
        db.session.commit()
        flash(f"Mesa {mesa.numero} excluída.", "success")
    return redirect(url_for("mesas.listar"))
