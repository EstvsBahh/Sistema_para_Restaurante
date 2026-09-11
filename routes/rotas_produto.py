from flask import Blueprint

produto_bp = Blueprint("produto", __name__)


@produto_bp.route("/produtos", methods=["GET"])
def listar_produtos():
    return {"mensagem": "Lista de produtos"}

@produto_bp.route("/produtos", methods=["POST"])
def cadastrar_produto():
    return {"mensagem": "Produto cadastrado"}

@produto_bp.route("/produtos/<int:id>", methods=["PUT"])
def atualizar_produto(id):
    return {"mensagem": "Produto atualizado"}

@produto_bp.route("/produtos/<int:id>", methods=["DELETE"])
def excluir_produto(id):
    return {"mensagem": "Produto excluído"} 

@produto_bp.route("/produtos/<int:id>/estoque", methods=["PUT"])
def repor_estoque(id):
    return {"mensagem": "Estoque atualizado"}  

@produto_bp.route("/produtos/estoque-baixo", methods=["GET"])
def listar_estoque_baixo():
    return {"mensagem": "Lista de produtos com estoque baixo"}