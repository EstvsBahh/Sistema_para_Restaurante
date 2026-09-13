from flask import Blueprint, render_template, request, redirect, url_for, flash 
from extensions import db 
from models.pedido import Pedido 
from models.item_pedido import ItemPedido 
from models.mesa import Mesa 
from models.garcom import Garcom 
from models.produto import Produto 
 
pedido_bp = Blueprint("pedido", __name__, url_prefix="/pedidos") 
 
@pedido_bp.route("/novo", methods=["GET"]) 
def form_novo_pedido(): 
    mesas_livres = Mesa.query.filter_by(situacao="livre").all() 
    garcons = Garcom.query.all() 
    return render_template("novo_pedido.html", mesas=mesas_livres, garcons=garcons) 
 
@pedido_bp.route("/novo", methods=["POST"]) 
def abrir_pedido(): 
    mesa = Mesa.query.get_or_404(request.form.get("mesa_numero")) 
    if mesa.situacao != "livre": 
        flash("Essa mesa já está ocupada.") 
        return redirect(url_for("pedido.form_novo_pedido")) 
 
    pedido = Pedido(mesa_numero=mesa.numero, garcom_id=request.form.get("garcom_id")) 
    mesa.ocupar() 
    db.session.add(pedido) 
    db.session.commit() 
    return redirect(url_for("pedido.ver_pedido", numero=pedido.numero)) 
 
@pedido_bp.route("/<int:numero>", methods=["GET"]) 
def ver_pedido(numero): 
    pedido = Pedido.query.get_or_404(numero) 
    produtos_disponiveis = Produto.query.filter_by(disponivel=True).all() 
    return render_template("pedido.html", pedido=pedido, produtos=produtos_disponiveis) 
 
@pedido_bp.route("/<int:numero>/itens", methods=["POST"]) 
def adicionar_item(numero): 
    pedido = Pedido.query.get_or_404(numero) 
    produto = Produto.query.get_or_404(request.form.get("produto_id")) 
    quantidade = int(request.form.get("quantidade", 1)) 
 
    if produto.quantidade_estoque < quantidade: 
        flash(f"Estoque insuficiente de {produto.nome} (disponível: {produto.quantidade_estoque}).") 
        return redirect(url_for("pedido.ver_pedido", numero=numero)) 
 
    item = ItemPedido( 
        pedido_numero=pedido.numero, 
        produto_id=produto.id, 
        quantidade=quantidade, 
        preco_unitario=produto.preco, 
    ) 
    produto.dar_baixa_estoque(quantidade) 
    db.session.add(item) 
    pedido.calcular_total() 
    db.session.commit() 
    return redirect(url_for("pedido.ver_pedido", numero=numero)) 
 
@pedido_bp.route("/<int:numero>/enviar-cozinha", methods=["POST"]) 
def enviar_para_cozinha(numero): 
    pedido = Pedido.query.get_or_404(numero) 
    pedido.alterar_estado("em_preparo") 
    db.session.commit() 
    return redirect(url_for("pedido.ver_pedido", numero=numero)) 
 
@pedido_bp.route("/cozinha", methods=["GET"]) 
def painel_cozinha(): 
    pedidos = Pedido.query.filter(Pedido.estado.in_(["em_preparo", "pronto"])).all() 
    return render_template("cozinha.html", pedidos=pedidos) 
 
@pedido_bp.route("/<int:numero>/marcar-pronto", methods=["POST"]) 
def marcar_pronto(numero): 
    pedido = Pedido.query.get_or_404(numero) 
    pedido.alterar_estado("pronto") 
    db.session.commit() 
    return redirect(url_for("pedido.painel_cozinha"))