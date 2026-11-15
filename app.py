import warnings
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from flask import Flask, flash, redirect, render_template, url_for
from sqlalchemy import desc, func
from sqlalchemy.exc import SAWarning

from config import Config
from extensions import db, migrate
from routes import registrar_rotas

warnings.filterwarnings("ignore", message=r".*does \*not\* support Decimal.*", category=SAWarning)


def brl(valor):
    valor = Decimal(str(valor or 0)).quantize(Decimal("0.01"))
    texto = f"{valor:,.2f}".replace(",", "#").replace(".", ",").replace("#", ".")
    return f"R$ {texto}"


def data_hora(valor):
    return valor.strftime("%d/%m/%Y %H:%M") if valor else "-"


def hora(valor):
    return valor.strftime("%H:%M") if valor else "-"


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    import models  
    from models.caixa import Caixa
    from models.mesa import Mesa
    from models.pagamento import Pagamento
    from models.pedido import Pedido
    from models.produto import Produto
    from models.item_pedido import ItemPedido

    registrar_rotas(app)

    app.jinja_env.filters["brl"] = brl
    app.jinja_env.filters["data_hora"] = data_hora
    app.jinja_env.filters["hora"] = hora

    @app.context_processor
    def variaveis_globais():
        return {
            "caixa_atual": Caixa.atual(),
            "nome_restaurante": app.config["NOME_RESTAURANTE"],
            "ano_atual": datetime.now().year,
        }

    @app.route("/")
    def home():
        inicio_do_dia = datetime.combine(date.today(), time.min)

        mesas = {status: Mesa.query.filter_by(status=status).count() for status in Mesa.STATUS}
        mesas["total"] = sum(mesas.values())

        pagamentos_hoje = Pagamento.query.filter(Pagamento.criado_em >= inicio_do_dia).all()
        faturamento_hoje = sum((Decimal(str(p.valor)) for p in pagamentos_hoje), Decimal("0"))
        taxas_hoje = sum((Decimal(str(p.taxa_servico)) for p in pagamentos_hoje), Decimal("0"))
        ticket_medio = faturamento_hoje / len(pagamentos_hoje) if pagamentos_hoje else Decimal("0")

        dias_sem = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]
        hoje = date.today()
        sete_dias = [hoje - timedelta(days=i) for i in range(6, -1, -1)]
        recentes = Pagamento.query.filter(
            Pagamento.criado_em >= datetime.combine(hoje - timedelta(days=29), time.min)
        ).all()
        por_dia = {d: [0.0, 0.0] for d in sete_dias}
        por_forma = {}
        for p in recentes:
            valor, taxa = float(p.valor), float(p.taxa_servico)
            if p.criado_em.date() in por_dia:
                por_dia[p.criado_em.date()][0] += valor - taxa
                por_dia[p.criado_em.date()][1] += taxa
            por_forma[p.forma] = por_forma.get(p.forma, 0.0) + valor
        grafico = {
            "rotulos": [f"{dias_sem[d.weekday()]} {d.strftime('%d/%m')}" for d in sete_dias],
            "faturamento": [round(por_dia[d][0], 2) for d in sete_dias],
            "taxas": [round(por_dia[d][1], 2) for d in sete_dias],
            "formas": [{"rotulo": Pagamento.FORMAS.get(k, k), "valor": round(v, 2)} for k, v in por_forma.items()],
        }

        total_vendido = func.sum(ItemPedido.quantidade).label("total")
        top_produtos = (
            db.session.query(Produto.nome, total_vendido)
            .join(ItemPedido, ItemPedido.produto_id == Produto.id)
            .join(Pedido, Pedido.id == ItemPedido.pedido_id)
            .filter(Pedido.status != Pedido.CANCELADO)
            .group_by(Produto.id, Produto.nome)
            .order_by(desc("total"))
            .limit(5)
            .all()
        )

        return render_template(
            "home.html",
            agora=datetime.now(),
            mesas=mesas,
            pedidos_ativos=Pedido.query.filter(Pedido.status.in_(Pedido.ATIVOS)).count(),
            faturamento_hoje=faturamento_hoje,
            vendas_hoje=len(pagamentos_hoje),
            ticket_medio=ticket_medio,
            taxas_hoje=taxas_hoje,
            grafico=grafico,
            top_produtos=top_produtos,
            top_maximo=int(top_produtos[0][1]) if top_produtos else 0,
            pedidos_recentes=Pedido.query.order_by(Pedido.id.desc()).limit(8).all(),
        )

    @app.errorhandler(404)
    def nao_encontrado(_erro):
        flash("Página ou registro não encontrado.", "warning")
        return redirect(url_for("home"))

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
