from flask import Blueprint

garcom_bp = Blueprint("garcom", __name__)

@garcom_bp.route("/garcons", methods=["GET"])
def listar_garcons():
    return {"mensagem": "Lista de garçons"}

@garcom_bp.route("/garcons", methods=["POST"])
def cadastrar_garcom():
    return {"mensagem": "Garçom cadastrado"}

@garcom_bp.route("/garcons/<int:id>", methods=["PUT"])
def atualizar_garcom(id):
    return {"mensagem": "Garçom atualizado"}

@garcom_bp.route("/garcons/<int:id>", methods=["DELETE"])
def excluir_garcom(id):
    return {"mensagem": "Garçom excluído"}