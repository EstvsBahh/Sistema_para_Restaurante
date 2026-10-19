from flask import Blueprint, flash, redirect, render_template, request, url_for
from extensions import db
from models.categoria import Categoria
from models.garcom import Garcom
from models.mesa import Mesa
from models.pedido import Pedido
from models.produto import Produto

pedido_bp = Blueprint("pedidos", __name__)


def _voltar(pedido):
    destino = request.form.get("voltar_para", "pedido")
    if destino == "cozinha":
        return redirect(url_for("pedidos.cozinha"))
    if destino == "mesas":
        return redirect(url_for("mesas.listar"))
    return redirect(url_for("pedidos.ver", pedido_id=pedido.id))



@pedido_bp.route("/pedidos/novo", methods=["GET"])
def novo():
    return render_template(
        "novo_pedido.html",
        mesas=Mesa.query.filter(Mesa.status != Mesa.OCUPADA).order_by(Mesa.numero).all(),
        garcons=Garcom.query.filter_by(ativo=True).order_by(Garcom.nome).all(),
        categorias=Categoria.query.order_by(Categoria.nome).all(),
        produtos=Produto.query.filter_by(ativo=True).order_by(Produto.nome).all(),
        mesa_selecionada=request.args.get("mesa", type=int),
    )


@pedido_bp.route("/pedidos/novo", methods=["POST"])
def criar():
    mesa_id = request.form.get("mesa_id", type=int)
    garcom_id = request.form.get("garcom_id", type=int)
    mesa = db.session.get(Mesa, mesa_id) if mesa_id else None
    garcom = db.session.get(Garcom, garcom_id) if garcom_id else None

    if not mesa or not garcom or not garcom.ativo:
        flash("Escolha uma mesa e um garçom ativo.", "danger")
        return redirect(url_for("pedidos.novo"))

    existente = mesa.pedido_ativo
    if existente:
        flash(f"A mesa {mesa.numero} já tem o pedido #{existente.id} em andamento.", "warning")
        return redirect(url_for("pedidos.ver", pedido_id=existente.id))


    ids = request.form.getlist("produto_id")
    quantidades = request.form.getlist("quantidade")
    observacoes = request.form.getlist("observacao_item")
    linhas = []
    for indice, bruto_id in enumerate(ids):
        try:
            produto_id = int(bruto_id)
            quantidade = int(quantidades[indice])
        except (ValueError, IndexError):
            continue
        observacao = observacoes[indice] if indice < len(observacoes) else ""
        if quantidade > 0:
            linhas.append((produto_id, quantidade, observacao))

    if not linhas:
        flash("Adicione ao menos um produto ao pedido.", "danger")
        return redirect(url_for("pedidos.novo", mesa=mesa.id))

    pedido = Pedido(
        mesa=mesa,
        garcom=garcom,
        observacao=request.form.get("observacao", "").strip() or None,
    )
    db.session.add(pedido)
    try:
        for produto_id, quantidade, observacao in linhas:
            produto = db.session.get(Produto, produto_id)
            if not produto:
                raise ValueError("Produto inválido no pedido.")
            pedido.adicionar_item(produto, quantidade, observacao)
        mesa.ocupar()
        if request.form.get("enviar") == "on":
            pedido.alterar_status(Pedido.EM_PREPARO)
        db.session.commit()
    except ValueError as erro:
        db.session.rollback()
        flash(str(erro), "danger")
        return redirect(url_for("pedidos.novo", mesa=mesa_id))

    if pedido.status == Pedido.EM_PREPARO:
        flash(f"Pedido #{pedido.id} enviado para a cozinha.", "success")
    else:
        flash(f"Pedido #{pedido.id} criado. Envie para a cozinha quando estiver pronto.", "success")
    return redirect(url_for("pedidos.ver", pedido_id=pedido.id))



@pedido_bp.route("/pedidos/<int:pedido_id>")
def ver(pedido_id):
    pedido = db.get_or_404(Pedido, pedido_id)
    produtos = (
        Produto.query.filter(Produto.ativo.is_(True), Produto.estoque_atual > 0)
        .order_by(Produto.nome)
        .all()
    )
    return render_template(
        "pedido.html",
        pedido=pedido,
        produtos=produtos,
        fluxo=Pedido.FLUXO,
        status_labels=Pedido.STATUS,
        taxa_percentual=int(Pedido.TAXA_SERVICO * 100),
    )


@pedido_bp.route("/pedidos/<int:pedido_id>/itens", methods=["POST"])
def adicionar_item(pedido_id):
    pedido = db.get_or_404(Pedido, pedido_id)
    produto = db.session.get(Produto, request.form.get("produto_id", type=int) or 0)
    quantidade = request.form.get("quantidade", default=1, type=int)

    if not produto:
        flash("Escolha um produto.", "danger")
        return redirect(url_for("pedidos.ver", pedido_id=pedido.id))

    try:
        pedido.adicionar_item(produto, quantidade, request.form.get("observacao"))
        if pedido.status in (Pedido.PRONTO, Pedido.ENTREGUE):
            pedido.alterar_status(Pedido.EM_PREPARO) 
            flash("Novo item enviado: o pedido voltou para a cozinha.", "info")
        db.session.commit()
        flash(f"{quantidade}x {produto.nome} adicionado.", "success")
    except ValueError as erro:
        db.session.rollback()
        flash(str(erro), "danger")
    return redirect(url_for("pedidos.ver", pedido_id=pedido.id))


@pedido_bp.route("/pedidos/<int:pedido_id>/itens/<int:item_id>/remover", methods=["POST"])
def remover_item(pedido_id, item_id):
    pedido = db.get_or_404(Pedido, pedido_id)
    item = next((i for i in pedido.itens if i.id == item_id), None)

    if not item:
        flash("Item não encontrado neste pedido.", "danger")
    elif not pedido.editavel:
        flash("Não é possível remover itens de um pedido que já ficou pronto.", "warning")
    elif len(pedido.itens) == 1:
        flash("O pedido precisa ter ao menos um item. Para desistir, cancele o pedido.", "warning")
    else:
        nome = item.produto.nome
        pedido.remover_item(item)
        db.session.commit()
        flash(f"{nome} removido e devolvido ao estoque.", "success")
    return redirect(url_for("pedidos.ver", pedido_id=pedido.id))



@pedido_bp.route("/pedidos/<int:pedido_id>/avancar", methods=["POST"])
def avancar(pedido_id):
    pedido = db.get_or_404(Pedido, pedido_id)
    proximo = Pedido.PROXIMO.get(pedido.status)

    if not proximo:
        flash("Este pedido não pode avançar de etapa.", "warning")
    elif pedido.status == Pedido.ABERTO and not pedido.itens:
        flash("Adicione itens antes de enviar para a cozinha.", "warning")
    else:
        pedido.alterar_status(proximo)
        db.session.commit()
        flash(f"Pedido #{pedido.id}: {pedido.status_label}.", "success")
    return _voltar(pedido)


@pedido_bp.route("/pedidos/<int:pedido_id>/cancelar", methods=["POST"])
def cancelar(pedido_id):
    pedido = db.get_or_404(Pedido, pedido_id)
    if not pedido.ativo:
        flash("Este pedido não pode mais ser cancelado.", "warning")
        return redirect(url_for("pedidos.ver", pedido_id=pedido.id))

    pedido.cancelar()
    db.session.commit()
    flash(f"Pedido #{pedido.id} cancelado, estoque devolvido e mesa liberada.", "info")
    return redirect(url_for("mesas.listar"))



@pedido_bp.route("/cozinha")
def cozinha():
    em_preparo = Pedido.query.filter_by(status=Pedido.EM_PREPARO).order_by(Pedido.criado_em).all()
    prontos = Pedido.query.filter_by(status=Pedido.PRONTO).order_by(Pedido.atualizado_em).all()
    return render_template("cozinha.html", em_preparo=em_preparo, prontos=prontos)
