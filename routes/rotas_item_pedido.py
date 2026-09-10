from decimal import Decimal

from flask import Blueprint, jsonify, request

from extensions import db
from models.item_pedido import ItemPedido
from models.pedido import Pedido
from models.produto import Produto
from routes.rotas_pedido import calcular_total_pedido, serializar_pedido

item_pedido_bp = Blueprint("itens_pedido", __name__)


def _decimal(valor):
    return Decimal(str(valor or 0))


def _atualizar_disponibilidade(produto):
    """Produto zerado fica indisponível; com estoque volta a ficar disponível."""
    if hasattr(produto, "disponivel"):
        produto.disponivel = produto.quantidade_estoque > 0


@item_pedido_bp.post("/pedidos/<int:pedido_id>/itens")
def adicionar_item(pedido_id):
    """
    Adiciona item e dá baixa automática no estoque.

    JSON esperado:
    {
        "produto_id": 3,
        "quantidade": 2
    }
    """
    pedido = db.session.get(Pedido, pedido_id)
    if pedido is None:
        return jsonify({"erro": "Pedido não encontrado."}), 404

    if pedido.estado == "finalizado":
        return jsonify({"erro": "Não é possível adicionar itens a um pedido finalizado."}), 409

    dados = request.get_json(silent=True) or {}
    produto_id = dados.get("produto_id")
    quantidade = dados.get("quantidade")

    if not produto_id or quantidade is None:
        return jsonify({"erro": "produto_id e quantidade são obrigatórios."}), 400

    if not isinstance(quantidade, int) or isinstance(quantidade, bool) or quantidade <= 0:
        return jsonify({"erro": "quantidade deve ser um número inteiro maior que zero."}), 400

    produto = db.session.get(Produto, produto_id)
    if produto is None:
        return jsonify({"erro": "Produto não encontrado."}), 404

    estoque_atual = produto.quantidade_estoque

    if estoque_atual <= 0:
        _atualizar_disponibilidade(produto)
        db.session.commit()
        return jsonify({"erro": "Produto sem estoque e indisponível para venda."}), 409

    if quantidade > estoque_atual:
        return (
            jsonify(
                {
                    "erro": "Estoque insuficiente.",
                    "estoque_disponivel": estoque_atual,
                }
            ),
            409,
        )

    # Mantém uma única linha por produto dentro do mesmo pedido.
    item = ItemPedido.query.filter_by(pedido_id=pedido.id, produto_id=produto.id).first()

    try:
        if item is None:
            item = ItemPedido(
                pedido_id=pedido.id,
                produto_id=produto.id,
                quantidade=quantidade,
                preco_unitario=_decimal(produto.preco),
            )
            db.session.add(item)
        else:
            item.quantidade += quantidade

        produto.quantidade_estoque -= quantidade
        _atualizar_disponibilidade(produto)

        db.session.flush()
        calcular_total_pedido(pedido)
        db.session.commit()

        return jsonify(serializar_pedido(pedido)), 201
    except Exception:
        db.session.rollback()
        return jsonify({"erro": "Não foi possível adicionar o item ao pedido."}), 500


@item_pedido_bp.delete("/pedidos/<int:pedido_id>/itens/<int:item_id>")
def remover_item(pedido_id, item_id):
    """Remove o item do pedido e devolve a quantidade ao estoque."""
    pedido = db.session.get(Pedido, pedido_id)
    if pedido is None:
        return jsonify({"erro": "Pedido não encontrado."}), 404

    if pedido.estado == "finalizado":
        return jsonify({"erro": "Não é possível remover itens de um pedido finalizado."}), 409

    item = db.session.get(ItemPedido, item_id)
    if item is None or item.pedido_id != pedido.id:
        return jsonify({"erro": "Item não encontrado neste pedido."}), 404

    produto = db.session.get(Produto, item.produto_id)

    try:
        if produto is not None:
            produto.quantidade_estoque += item.quantidade
            _atualizar_disponibilidade(produto)

        db.session.delete(item)
        db.session.flush()

        calcular_total_pedido(pedido)
        db.session.commit()

        return jsonify(serializar_pedido(pedido)), 200
    except Exception:
        db.session.rollback()
        return jsonify({"erro": "Não foi possível remover o item do pedido."}), 500
