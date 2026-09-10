from decimal import Decimal

from flask import Blueprint, jsonify, request
from sqlalchemy import func

from extensions import db
from models.mesa import Mesa
from models.pagamento import Pagamento
from models.pedido import Pedido
from routes.rotas_pedido import calcular_total_pedido

pagamento_bp = Blueprint("pagamentos", __name__, url_prefix="/pagamentos")

FORMAS_PAGAMENTO = {"dinheiro", "pix", "credito", "debito"}


def _decimal(valor):
    return Decimal(str(valor or 0))


def _total_confirmado(pedido_id):
    valor = (
        db.session.query(func.coalesce(func.sum(Pagamento.valor), 0))
        .filter(
            Pagamento.pedido_id == pedido_id,
            Pagamento.status == "confirmado",
        )
        .scalar()
    )
    return _decimal(valor)


@pagamento_bp.post("")
def registrar_pagamento():
    """
    Registra um pagamento como pendente.

    JSON esperado:
    {
        "pedido_id": 1,
        "forma_pagamento": "pix",
        "valor": 59.90
    }
    """
    dados = request.get_json(silent=True) or {}
    pedido_id = dados.get("pedido_id")
    forma_pagamento = dados.get("forma_pagamento")
    valor = dados.get("valor")

    if not pedido_id or forma_pagamento is None or valor is None:
        return (
            jsonify({"erro": "pedido_id, forma_pagamento e valor são obrigatórios."}),
            400,
        )

    if forma_pagamento not in FORMAS_PAGAMENTO:
        return (
            jsonify(
                {
                    "erro": "Forma de pagamento inválida.",
                    "formas_aceitas": sorted(FORMAS_PAGAMENTO),
                }
            ),
            400,
        )

    try:
        valor = _decimal(valor)
    except Exception:
        return jsonify({"erro": "valor inválido."}), 400

    if valor <= 0:
        return jsonify({"erro": "O valor do pagamento deve ser maior que zero."}), 400

    pedido = db.session.get(Pedido, pedido_id)
    if pedido is None:
        return jsonify({"erro": "Pedido não encontrado."}), 404

    if pedido.estado == "finalizado":
        return jsonify({"erro": "Este pedido já foi finalizado."}), 409

    total_pedido = calcular_total_pedido(pedido)
    if total_pedido <= 0:
        return jsonify({"erro": "Não é possível pagar um pedido sem itens."}), 409

    confirmado = _total_confirmado(pedido.id)
    restante = total_pedido - confirmado

    if valor > restante:
        return (
            jsonify(
                {
                    "erro": "O pagamento é maior que o valor restante do pedido.",
                    "valor_restante": float(restante),
                }
            ),
            409,
        )

    try:
        pagamento = Pagamento(
            pedido_id=pedido.id,
            valor=valor,
            forma_pagamento=forma_pagamento,
            status="pendente",
        )
        db.session.add(pagamento)
        db.session.commit()

        return (
            jsonify(
                {
                    "id": pagamento.id,
                    "pedido_id": pagamento.pedido_id,
                    "valor": float(_decimal(pagamento.valor)),
                    "forma_pagamento": pagamento.forma_pagamento,
                    "status": pagamento.status,
                }
            ),
            201,
        )
    except Exception:
        db.session.rollback()
        return jsonify({"erro": "Não foi possível registrar o pagamento."}), 500


@pagamento_bp.patch("/<int:pagamento_id>/confirmar")
def confirmar_pagamento(pagamento_id):
    """
    Confirma um pagamento.
    Quando o total confirmado cobre o pedido, finaliza o pedido e libera a mesa.
    """
    pagamento = db.session.get(Pagamento, pagamento_id)
    if pagamento is None:
        return jsonify({"erro": "Pagamento não encontrado."}), 404

    if pagamento.status == "confirmado":
        return jsonify({"erro": "Pagamento já estava confirmado."}), 409

    pedido = db.session.get(Pedido, pagamento.pedido_id)
    if pedido is None:
        return jsonify({"erro": "Pedido associado não encontrado."}), 404

    if pedido.estado == "finalizado":
        return jsonify({"erro": "Pedido já finalizado."}), 409

    try:
        pagamento.status = "confirmado"
        db.session.flush()

        total_pedido = calcular_total_pedido(pedido)
        total_pago = _total_confirmado(pedido.id)
        restante = max(Decimal("0.00"), total_pedido - total_pago)
        finalizado = total_pago >= total_pedido

        if finalizado:
            pedido.estado = "finalizado"
            mesa = db.session.get(Mesa, pedido.mesa_id)
            if mesa is not None:
                mesa.situacao = "livre"

        db.session.commit()

        return (
            jsonify(
                {
                    "pagamento_id": pagamento.id,
                    "status": pagamento.status,
                    "pedido_id": pedido.id,
                    "total_pedido": float(total_pedido),
                    "total_pago_confirmado": float(total_pago),
                    "valor_restante": float(restante),
                    "pedido_finalizado": finalizado,
                    "estado_pedido": pedido.estado,
                }
            ),
            200,
        )
    except Exception:
        db.session.rollback()
        return jsonify({"erro": "Não foi possível confirmar o pagamento."}), 500
