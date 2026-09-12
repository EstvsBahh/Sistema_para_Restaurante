from flask import Blueprint, request
from config import conectar_banco

garcom_bp = Blueprint("garcom", __name__)


@garcom_bp.route("/garcons", methods=["GET"])
def listar_garcons():
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Garcom")
    garcons = cursor.fetchall()

    cursor.close()
    conexao.close()

    return garcons

@garcom_bp.route("/garcons", methods=["POST"])
def cadastrar_garcom():
    dados = request.get_json()

    nome = dados["nome"]
    telefone = dados.get("telefone")

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute(
        "INSERT INTO Garcom (nome, telefone) VALUES (%s, %s)",
        (nome, telefone)
    )

    conexao.commit()

    cursor.close()
    conexao.close()

    return {"mensagem": "Garçom cadastrado com sucesso!"}, 201

@garcom_bp.route("/garcons/<int:id>", methods=["PUT"])
def atualizar_garcom(id):
    dados = request.get_json()

    nome = dados["nome"]
    telefone = dados.get("telefone")

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute(
        "UPDATE Garcom SET nome = %s, telefone = %s WHERE id = %s",
        (nome, telefone, id)
    )

    conexao.commit()

    cursor.close()
    conexao.close()

    return {"mensagem": "Garçom atualizado com sucesso!"}

@garcom_bp.route("/garcons/<int:id>", methods=["DELETE"])
def excluir_garcom(id):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute(
        "DELETE FROM Garcom WHERE id = %s",
        (id,)
    )

    conexao.commit()

    cursor.close()
    conexao.close()

    return {"mensagem": "Garçom excluído com sucesso!"}