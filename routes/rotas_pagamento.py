
from decimal import Decimal, InvalidOperation


from flask import Blueprint, flash, redirect, render_template, request, url_for


from extensions import db
from models.caixa import Caixa, MovimentacaoCaixa
from models.pagamento import Pagamento
from models.pedido import Pedido


pagamento_bp = Blueprint("pagamentos", __name__)




def _ler_decimal(campo):
  bruto = request.form.get(campo, "").strip().replace(",", ".")
  try:
      return Decimal(bruto)
  except (InvalidOperation, ValueError):
      return None




@pagamento_bp.route("/caixa")
def caixa():
  pendentes = (
      Pedido.query.filter(Pedido.status.in_((Pedido.PRONTO, Pedido.ENTREGUE)))
      .order_by(Pedido.criado_em)
      .all()
  )
  historico = Caixa.query.filter_by(status=Caixa.FECHADO).order_by(Caixa.id.desc()).limit(5).all()
  return render_template(
      "caixa.html",
      caixa=Caixa.atual(),
      pendentes=pendentes,
      historico=historico,
      formas=Pagamento.FORMAS,
      tipos=MovimentacaoCaixa.TIPOS,
      taxa_percentual=int(Pedido.TAXA_SERVICO * 100),
      abrir_pedido=request.args.get("pagar", type=int),
  )




@pagamento_bp.route("/caixa/abrir", methods=["POST"])
def abrir_caixa():
  responsavel = request.form.get("responsavel", "").strip()
  saldo = _ler_decimal("saldo_inicial")
  if saldo is None:
      saldo = Decimal("0")


  if Caixa.atual():
      flash("Já existe um caixa aberto.", "warning")
  elif not responsavel:
      flash("Informe o responsável pelo caixa.", "danger")
  elif saldo < 0:
      flash("O saldo inicial não pode ser negativo.", "danger")
  else:
      db.session.add(Caixa(responsavel=responsavel, saldo_inicial=saldo))
      db.session.commit()
      flash("Caixa aberto. Bom trabalho!", "success")
  return redirect(url_for("pagamentos.caixa"))




@pagamento_bp.route("/caixa/fechar", methods=["POST"])
def fechar_caixa():
  caixa = Caixa.atual()
  saldo_final = _ler_decimal("saldo_final")


  if not caixa:
      flash("Não há caixa aberto.", "warning")
  elif saldo_final is None or saldo_final < 0:
      flash("Informe o valor contado em dinheiro no fechamento.", "danger")
  else:
      caixa.fechar(saldo_final, request.form.get("observacao", "").strip() or None)
      db.session.commit()
      diferenca = caixa.diferenca
      if diferenca == 0:
          flash("Caixa fechado. O valor conferido bate com o esperado.", "success")
      else:
          flash("Caixa fechado com diferença entre o contado e o esperado. Veja o histórico.", "warning")
  return redirect(url_for("pagamentos.caixa"))




@pagamento_bp.route("/caixa/movimentacao", methods=["POST"])
def movimentar():
  caixa = Caixa.atual()
  tipo = request.form.get("tipo")
  valor = _ler_decimal("valor")
  descricao = request.form.get("descricao", "").strip()


  if not caixa:
    flash("Abra o caixa antes de registrar movimentações.", "warning")
  elif tipo not in MovimentacaoCaixa.TIPOS:
    flash("Tipo de movimentação inválido.", "danger")
  elif valor is None or valor <= 0:
    flash("Informe um valor maior que zero.", "danger")
  elif not descricao:
    flash("Descreva o motivo da movimentação.", "danger")
  else:
    db.session.add(MovimentacaoCaixa(caixa=caixa, tipo=tipo, valor=valor, descricao=descricao))
    db.session.commit()
    flash("Movimentação registrada.", "success")
  return redirect(url_for("pagamentos.caixa"))




@pagamento_bp.route("/pedidos/<int:pedido_id>/pagar", methods=["POST"])
def pagar(pedido_id):
  caixa = Caixa.atual()
  if not caixa:
    flash("Abra o caixa antes de receber pagamentos.", "warning")
    return redirect(url_for("pagamentos.caixa"))


  pedido = db.get_or_404(Pedido, pedido_id)
  forma = request.form.get("forma")
  if pedido.pagamento or pedido.status not in (Pedido.PRONTO, Pedido.ENTREGUE):
      flash("Este pedido não está disponível para pagamento.", "warning")
      return redirect(url_for("pagamentos.caixa"))
  if forma not in Pagamento.FORMAS:
      flash("Escolha a forma de pagamento.", "danger")
      return redirect(url_for("pagamentos.caixa", pagar=pedido.id))




  taxa = pedido.calcular_taxa_servico() if request.form.get("taxa_servico") == "on" else Decimal("0.00")
  total = pedido.total + taxa
  recebido = None
  if forma == Pagamento.DINHEIRO:
      recebido = _ler_decimal("valor_recebido")
      if recebido is None:
        recebido = total
      if recebido < total:
        flash("O valor recebido é menor que o total do pedido.", "danger")
        return redirect(url_for("pagamentos.caixa", pagar=pedido.id))


  pagamento = Pagamento(
      pedido=pedido, caixa=caixa, forma=forma, valor=total, taxa_servico=taxa, valor_recebido=recebido
  )
  db.session.add(pagamento)
  pedido.marcar_pago()
  db.session.commit()


  mensagem = f"Pedido #{pedido.id} pago. Mesa {pedido.mesa.numero} liberada."
  if taxa > 0:
      mensagem += f" Taxa de serviço: R$ {taxa:.2f}.".replace(".", ",")
  if pagamento.troco > 0:
      mensagem += f" Troco: R$ {pagamento.troco:.2f}".replace(".", ",")
  flash(mensagem, "success")
  return redirect(url_for("pagamentos.caixa"))
