import csv
import io
from datetime import date, datetime, time, timedelta
from decimal import Decimal, InvalidOperation

from flask import Blueprint, Response, abort, flash, redirect, render_template, request, url_for

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


TIPOS_CSV = ("pagamentos", "dias", "produtos", "garcons")


def _periodo():
    def ler(nome, padrao):
        try:
            return date.fromisoformat(request.args.get(nome, ""))
        except ValueError:
            return padrao

    fim = ler("fim", date.today())
    inicio = ler("inicio", fim - timedelta(days=29))
    if inicio > fim:
        inicio, fim = fim, inicio
    return inicio, fim


def _dados_relatorio(inicio, fim):
    limite_i = datetime.combine(inicio, time.min)
    limite_f = datetime.combine(fim + timedelta(days=1), time.min)
    pagamentos = (
        Pagamento.query.filter(Pagamento.criado_em >= limite_i, Pagamento.criado_em < limite_f)
        .order_by(Pagamento.criado_em)
        .all()
    )
    zero = Decimal("0")
    faturamento = sum((Decimal(str(p.valor)) for p in pagamentos), zero)
    taxas = sum((Decimal(str(p.taxa_servico)) for p in pagamentos), zero)
    itens = sum((p.pedido.quantidade_itens for p in pagamentos), 0)

    dias, formas, produtos, garcons = {}, {}, {}, {}
    for p in pagamentos:
        valor, taxa = Decimal(str(p.valor)), Decimal(str(p.taxa_servico))
        d = dias.setdefault(p.criado_em.date(), {"data": p.criado_em.date(), "pedidos": 0, "itens": 0, "taxas": zero, "total": zero})
        d["pedidos"] += 1
        d["itens"] += p.pedido.quantidade_itens
        d["taxas"] += taxa
        d["total"] += valor
        f = formas.setdefault(p.forma, {"forma": p.forma, "pedidos": 0, "total": zero})
        f["pedidos"] += 1
        f["total"] += valor
        g = garcons.setdefault(p.pedido.garcom_id, {"nome": p.pedido.garcom.nome, "pedidos": 0, "total": zero})
        g["pedidos"] += 1
        g["total"] += valor
        for item in p.pedido.itens:
            pr = produtos.setdefault(item.produto_id, {"nome": item.produto.nome, "quantidade": 0, "total": zero})
            pr["quantidade"] += item.quantidade
            pr["total"] += item.subtotal

    return {
        "pagamentos": pagamentos,
        "totais": {
            "pedidos": len(pagamentos),
            "faturamento": faturamento,
            "taxas": taxas,
            "itens": itens,
            "ticket": faturamento / len(pagamentos) if pagamentos else zero,
        },
        "dias": sorted(dias.values(), key=lambda x: x["data"]),
        "formas": sorted(formas.values(), key=lambda x: x["total"], reverse=True),
        "produtos": sorted(produtos.values(), key=lambda x: (-x["quantidade"], x["nome"])),
        "garcons": sorted(garcons.values(), key=lambda x: x["total"], reverse=True),
    }


@pagamento_bp.route("/relatorios")
def relatorios():
    inicio, fim = _periodo()
    dados = _dados_relatorio(inicio, fim)
    hoje = date.today()
    atalhos = [
        ("Hoje", hoje, hoje),
        ("7 dias", hoje - timedelta(days=6), hoje),
        ("30 dias", hoje - timedelta(days=29), hoje),
        ("Este mês", hoje.replace(day=1), hoje),
    ]
    grafico = {
        "rotulos": [d["data"].strftime("%d/%m") for d in dados["dias"]],
        "faturamento": [float(d["total"] - d["taxas"]) for d in dados["dias"]],
        "taxas": [float(d["taxas"]) for d in dados["dias"]],
    }
    return render_template(
        "relatorios.html",
        inicio=inicio,
        fim=fim,
        atalhos=atalhos,
        formas_rotulo=Pagamento.FORMAS,
        grafico=grafico,
        taxa_percentual=int(Pedido.TAXA_SERVICO * 100),
        **dados,
    )


def _num(valor):
    return f"{Decimal(str(valor)).quantize(Decimal('0.01')):.2f}".replace(".", ",")


def _seguro(texto):
    texto = str(texto)
    return "'" + texto if texto[:1] in ("=", "+", "-", "@") else texto


@pagamento_bp.route("/relatorios/exportar/<tipo>.csv")
def exportar_csv(tipo):
    if tipo not in TIPOS_CSV:
        abort(404)
    inicio, fim = _periodo()
    dados = _dados_relatorio(inicio, fim)

    if tipo == "pagamentos":
        cabecalho = ["Data", "Hora", "Pedido", "Mesa", "Garçom", "Forma", "Itens", "Subtotal", "Taxa de serviço", "Total"]
        linhas = [
            [p.criado_em.strftime("%d/%m/%Y"), p.criado_em.strftime("%H:%M"), p.pedido_id, p.pedido.mesa.numero,
             _seguro(p.pedido.garcom.nome), p.forma_label, p.pedido.quantidade_itens,
             _num(p.subtotal), _num(p.taxa_servico), _num(p.valor)]
            for p in dados["pagamentos"]
        ]
    elif tipo == "dias":
        cabecalho = ["Data", "Pedidos", "Itens", "Taxa de serviço", "Faturamento"]
        linhas = [[d["data"].strftime("%d/%m/%Y"), d["pedidos"], d["itens"], _num(d["taxas"]), _num(d["total"])] for d in dados["dias"]]
    elif tipo == "produtos":
        cabecalho = ["Produto", "Quantidade vendida", "Total em itens"]
        linhas = [[_seguro(x["nome"]), x["quantidade"], _num(x["total"])] for x in dados["produtos"]]
    else:
        cabecalho = ["Garçom", "Pedidos", "Total atendido"]
        linhas = [[_seguro(x["nome"]), x["pedidos"], _num(x["total"])] for x in dados["garcons"]]

    saida = io.StringIO()
    escritor = csv.writer(saida, delimiter=";", lineterminator="\r\n")
    escritor.writerow(cabecalho)
    escritor.writerows(linhas)
    nome = f"relatorio_{tipo}_{inicio.isoformat()}_{fim.isoformat()}.csv"
    return Response(
        "\ufeff" + saida.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{nome}"'},
    )
