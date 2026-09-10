from decimal import Decimal

from flask import Blueprint, jsonify, request

from extensions import db
from models.garcom import Garcom
from models.mesa import Mesa
from models.pedido import Pedido

pedido_bp = Blueprint("pedidos", __name__, url_prefix="/pedidos")

ESTADOS_COZINHA = {"aberto", "em_preparo", "pronto", "entregue"}


def _decimal(valor):
    """Converte valores do banco/JSON para Decimal sem perder precisão monetária."""
    return Decimal(str(valor or 0))


def calcular_total_pedido(pedido):
    """Recalcula o total usando os itens atuais do pedido."""
    total = Decimal("0.00")

    for item in pedido.itens:
        preco = getattr(item, "preco_unitario", None)
        if preco is None:
            preco = item.produto.preco
        total += _decimal(preco) * item.quantidade

    pedido.valor_total = total
    return total


def serializar_pedido(pedido):
    itens = []
    for item in pedido.itens:
        preco = getattr(item, "preco_unitario", None)
        if preco is None:
            preco = item.produto.preco
        subtotal = _decimal(preco) * item.quantidade

        itens.append(
            {
                "id": item.id,
                "produto_id": item.produto_id,
                "produto": item.produto.nome,
                "quantidade": item.quantidade,
                "preco_unitario": float(_decimal(preco)),
                "subtotal": float(subtotal),
            }
        )

    return {
        "id": pedido.id,
        "mesa_id": pedido.mesa_id,
        "garcom_id": pedido.garcom_id,
        "estado": pedido.estado,
        "valor_total": float(_decimal(pedido.valor_total)),
        "itens": itens,
    }


@pedido_bp.post("")
def abrir_pedido():
    """
    Abre um pedido para uma mesa.

    JSON esperado:
    {
        "mesa_id": 1,
        "garcom_id": 2
    }
    """
    dados = request.get_json(silent=True) or {}
    mesa_id = dados.get("mesa_id")
    garcom_id = dados.get("garcom_id")

    if not mesa_id or not garcom_id:
        return jsonify({"erro": "mesa_id e garcom_id são obrigatórios."}), 400

    mesa = db.session.get(Mesa, mesa_id)
    if mesa is None:
        return jsonify({"erro": "Mesa não encontrada."}), 404

    garcom = db.session.get(Garcom, garcom_id)
    if garcom is None:
        return jsonify({"erro": "Garçom não encontrado."}), 404

    if mesa.situacao != "livre":
        return jsonify({"erro": "Esta mesa já está ocupada."}), 409

    try:
        pedido = Pedido(
            mesa_id=mesa.id,
            garcom_id=garcom.id,
            estado="aberto",
            valor_total=Decimal("0.00"),
        )
        mesa.situacao = "ocupada"

        db.session.add(pedido)
        db.session.commit()

        return jsonify(serializar_pedido(pedido)), 201
    except Exception:
        db.session.rollback()
        return jsonify({"erro": "Não foi possível abrir o pedido."}), 500


@pedido_bp.get("/<int:pedido_id>")
def buscar_pedido(pedido_id):
    pedido = db.session.get(Pedido, pedido_id)
    if pedido is None:
        return jsonify({"erro": "Pedido não encontrado."}), 404

    calcular_total_pedido(pedido)
    return jsonify(serializar_pedido(pedido)), 200


@pedido_bp.get("/<int:pedido_id>/total")
def total_pedido(pedido_id):
    pedido = db.session.get(Pedido, pedido_id)
    if pedido is None:
        return jsonify({"erro": "Pedido não encontrado."}), 404

    total = calcular_total_pedido(pedido)
    db.session.commit()
    return jsonify({"pedido_id": pedido.id, "valor_total": float(total)}), 200


@pedido_bp.patch("/<int:pedido_id>/estado")
def atualizar_estado(pedido_id):
    """
    Atualiza o estado acompanhado pela cozinha.

    JSON esperado:
    {
        "estado": "em_preparo"
    }

    Estados aceitos aqui: aberto, em_preparo, pronto e entregue.
    'finalizado' é reservado para a confirmação do pagamento.
    """
    pedido = db.session.get(Pedido, pedido_id)
    if pedido is None:
        return jsonify({"erro": "Pedido não encontrado."}), 404

    if pedido.estado == "finalizado":
        return jsonify({"erro": "Pedido já finalizado não pode ser alterado."}), 409

    dados = request.get_json(silent=True) or {}
    novo_estado = dados.get("estado")

    if novo_estado not in ESTADOS_COZINHA:
        return (
            jsonify(
                {
                    "erro": "Estado inválido.",
                    "estados_aceitos": sorted(ESTADOS_COZINHA),
                }
            ),
            400,
        )

    pedido.estado = novo_estado
    db.session.commit()

    return jsonify({"pedido_id": pedido.id, "estado": pedido.estado}), 200
