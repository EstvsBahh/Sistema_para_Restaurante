from flask import Blueprint

categoria_bp = Blueprint("categoria", __name__)


@categoria_bp.route("/categorias", methods=["GET"])
def listar_categorias():
    return {"mensagem": "Lista de categorias"}


@categoria_bp.route("/categorias", methods=["POST"])
def cadastrar_categoria():
    return {"mensagem": "Categoria cadastrada"}


@categoria_bp.route("/categorias/<int:id>", methods=["PUT"])
def atualizar_categoria(id):
    return {"mensagem": "Categoria atualizada"}


@categoria_bp.route("/categorias/<int:id>", methods=["DELETE"])
def excluir_categoria(id):
    return {"mensagem": "Categoria excluída"}