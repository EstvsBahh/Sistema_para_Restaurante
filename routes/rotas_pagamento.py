from flask import Blueprint, render_template, request, redirect, url_for 
from extensions import db 
from models.pedido import Pedido 
from models.pagamento import Pagamento 
 
pagamento_bp = Blueprint("pagamento", __name__, url_prefix="/caixa") 
 
@pagamento_bp.route("/", methods=["GET"]) 
def painel_caixa(): 
    pedidos = Pedido.query.filter_by(estado="pronto").all() 
    return render_template("caixa.html", pedidos=pedidos) 
 
@pagamento_bp.route("/<int:numero>/pagar", methods=["POST"]) 
def registrar_pagamento(numero): 
    pedido = Pedido.query.get_or_404(numero) 
    pagamento = Pagamento( 
        pedido_numero=pedido.numero, 
        valor=pedido.valor_total, 
        forma_pagamento=request.form.get("forma_pagamento"), 
    ) 
    pagamento.confirmar_pagamento() 
    pedido.finalizar() 
    pedido.mesa.liberar() 
    db.session.add(pagamento) 
    db.session.commit() 
    return redirect(url_for("pagamento.painel_caixa"))