from flask import Blueprint, request
from config import conectar_banco

produto_bp = Blueprint("produto", __name__)


@produto_bp.route("/produtos", methods=["GET"])
def listar_produtos():
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Produto")
    produtos = cursor.fetchall()

    cursor.close()
    conexao.close()

    return produtos


@produto_bp.route("/produtos", methods=["POST"])
def cadastrar_produto():
    dados = request.get_json()

    nome = dados["nome"]
    descricao = dados.get("descricao")
    preco = dados["preco"]
    categoria_id = dados["categoria_id"]
    quantidade_estoque = dados.get("quantidade_estoque", 0)
    estoque_minimo = dados.get("estoque_minimo", 5)

    disponibilidade = quantidade_estoque > 0

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute(
        """
        INSERT INTO Produto
        (nome, descricao, preco, disponibilidade, quantidade_estoque, estoque_minimo, categoria_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            nome,
            descricao,
            preco,
            disponibilidade,
            quantidade_estoque,
            estoque_minimo,
            categoria_id
        )
    )

    conexao.commit()

    cursor.close()
    conexao.close()

    return {"mensagem": "Produto cadastrado com sucesso!"}, 201

@produto_bp.route("/produtos/<int:id>", methods=["PUT"])
def atualizar_produto(id):
    dados = request.get_json()

    nome = dados["nome"]
    descricao = dados.get("descricao")
    preco = dados["preco"]
    categoria_id = dados["categoria_id"]
    quantidade_estoque = dados["quantidade_estoque"]
    estoque_minimo = dados["estoque_minimo"]

    disponibilidade = quantidade_estoque > 0

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute(
        """
        UPDATE Produto
        SET nome = %s,
            descricao = %s,
            preco = %s,
            categoria_id = %s,
            quantidade_estoque = %s,
            estoque_minimo = %s,
            disponibilidade = %s
        WHERE id = %s
        """,
        (
            nome,
            descricao,
            preco,
            categoria_id,
            quantidade_estoque,
            estoque_minimo,
            disponibilidade,
            id
        )
    )

    conexao.commit()

    cursor.close()
    conexao.close()

    return {"mensagem": "Produto atualizado com sucesso!"}

@produto_bp.route("/produtos/<int:id>/estoque", methods=["PUT"])
def repor_estoque(id):
    dados = request.get_json()

    quantidade = dados["quantidade"]

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute(
        """
        UPDATE Produto
        SET quantidade_estoque = quantidade_estoque + %s,
            disponibilidade = TRUE
        WHERE id = %s
        """,
        (quantidade, id)
    )

    conexao.commit()

    cursor.close()
    conexao.close()

    return {"mensagem": "Estoque atualizado com sucesso!"}

@produto_bp.route("/produtos/estoque-baixo", methods=["GET"])
def listar_estoque_baixo():
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM Produto
        WHERE quantidade_estoque <= estoque_minimo
        """
    )

    produtos = cursor.fetchall()

    cursor.close()
    conexao.close()

    return produtos

@produto_bp.route("/produtos/<int:id>", methods=["DELETE"])
def excluir_produto(id):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute(
        "DELETE FROM Produto WHERE id = %s",
        (id,)
    )

    conexao.commit()

    cursor.close()
    conexao.close()

    return {"mensagem": "Produto excluído com sucesso!"}