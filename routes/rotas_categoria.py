from flask import Blueprint, request
from config import conectar_banco

categoria_bp = Blueprint("categoria", __name__)


@categoria_bp.route("/categorias", methods=["GET"])
def listar_categorias():
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Categoria")
    categorias = cursor.fetchall()

    cursor.close()
    conexao.close()

    return categorias

@categoria_bp.route("/categorias", methods=["POST"])
def cadastrar_categoria():
    dados = request.get_json()

    nome = dados["nome"]
    descricao = dados.get("descricao")

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute(
        "INSERT INTO Categoria (nome, descricao) VALUES (%s, %s)",
        (nome, descricao)
    )

    conexao.commit()

    cursor.close()
    conexao.close()

    return {"mensagem": "Categoria cadastrada com sucesso!"}, 201

@categoria_bp.route("/categorias/<int:id>", methods=["PUT"])
def atualizar_categoria(id):
    dados = request.get_json()

    nome = dados["nome"]
    descricao = dados.get("descricao")

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute(
        "UPDATE Categoria SET nome = %s, descricao = %s WHERE id = %s",
        (nome, descricao, id)
    )

    conexao.commit()

    cursor.close()
    conexao.close()

    return {"mensagem": "Categoria atualizada com sucesso!"}

@categoria_bp.route("/categorias/<int:id>", methods=["DELETE"])
def excluir_categoria(id):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute(
        "DELETE FROM Categoria WHERE id = %s",
        (id,)
    )

    conexao.commit()

    cursor.close()
    conexao.close()

    return {"mensagem": "Categoria excluída com sucesso!"}