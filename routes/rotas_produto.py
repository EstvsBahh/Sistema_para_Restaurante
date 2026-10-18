from decimal import Decimal, InvalidOperation
from flask import Blueprint, flash, redirect, render_template, request, url_for
from extensions import db
from models.categoria import Categoria
from models.produto import Produto

produto_bp = Blueprint("produtos", __name__)

def _ler_decimal(campo):
   bruto = request.form.get(campo, "").strip().replace(",", ".")
   try:
       return Decimal(bruto)
   except (InvalidOperation, ValueError):
       return None

@produto_bp.route("/produtos/")
def listar():
   busca = request.args.get("q", "").strip()
   categoria_id = request.args.get("categoria", type=int)
   situacao = request.args.get("situacao", "todos")

   consulta = Produto.query
   if busca:
       consulta = consulta.filter(Produto.nome.ilike(f"%{busca}%"))
   if categoria_id:
       consulta = consulta.filter(Produto.categoria_id == categoria_id)
   if situacao == "ativos":
       consulta = consulta.filter(Produto.ativo.is_(True))
   elif situacao == "inativos":
       consulta = consulta.filter(Produto.ativo.is_(False))

   return render_template(
       "produtos.html",
       produtos=consulta.order_by(Produto.nome).all(),
       categorias=Categoria.query.order_by(Categoria.nome).all(),
       busca=busca,
       categoria_id=categoria_id,
       situacao=situacao,
   )

@produto_bp.route("/produtos/novo", methods=["POST"])
def criar():
   nome = request.form.get("nome", "").strip()
   preco = _ler_decimal("preco")
   categoria = db.session.get(Categoria, request.form.get("categoria_id", type=int) or 0)
   estoque = request.form.get("estoque_atual", default=0, type=int)

   if not nome:
      flash("Informe o nome do produto.", "danger")
   elif preco is None or preco < 0:
      flash("Informe um preço válido.", "danger")
   elif not categoria:
      flash("Escolha uma categoria. Cadastre uma antes, se ainda não existir.", "danger")
   elif estoque < 0:
      flash("Estoque não pode ser negativo.", "danger")
   else:
      db.session.add(
          Produto(
              nome=nome,
              descricao=request.form.get("descricao", "").strip() or None,
              preco=preco,
              categoria_id=categoria.id,
              estoque_atual=estoque,
              ativo=True,
          )
      )
      db.session.commit()
      flash(f"Produto \"{nome}\" cadastrado.", "success")
   return redirect(url_for("produtos.listar"))

@produto_bp.route("/produtos/<int:produto_id>/editar", methods=["POST"])
def editar(produto_id):
  produto = db.get_or_404(Produto, produto_id)
  nome = request.form.get("nome", "").strip()
  preco = _ler_decimal("preco")
  categoria = db.session.get(Categoria, request.form.get("categoria_id", type=int) or 0)

  if not nome:
     flash("Informe o nome do produto.", "danger")
  elif preco is None or preco < 0:
     flash("Informe um preço válido.", "danger")
  elif not categoria:
     flash("Escolha uma categoria válida.", "danger")
  else:
     produto.nome = nome
     produto.descricao = request.form.get("descricao", "").strip() or None
     produto.preco = preco
     produto.categoria_id = categoria.id
     produto.ativo = request.form.get("ativo") == "on"
     db.session.commit()
     flash("Produto atualizado.", "success")
  return redirect(request.referrer or url_for("produtos.listar"))


@produto_bp.route("/produtos/<int:produto_id>/alternar", methods=["POST"])
def alternar(produto_id):
  produto = db.get_or_404(Produto, produto_id)
  produto.ativo = not produto.ativo
  db.session.commit()
  if produto.ativo:
     flash(f"\"{produto.nome}\" voltou ao cardápio.", "success")
  else:
     flash(f"\"{produto.nome}\" saiu do cardápio.", "info")
  return redirect(request.referrer or url_for("produtos.listar"))


@produto_bp.route("/produtos/<int:produto_id>/excluir", methods=["POST"])
def excluir(produto_id):
  produto = db.get_or_404(Produto, produto_id)
  if produto.itens.count():
     flash("Este produto já foi vendido. Retire-o do cardápio em vez de excluir, para preservar o histórico.", "warning")
  else:
     db.session.delete(produto)
     db.session.commit()
     flash("Produto excluído.", "success")
  return redirect(url_for("produtos.listar"))


@produto_bp.route("/estoque/")
def estoque():
  filtro = request.args.get("filtro", "todos")
  produtos = Produto.query.order_by(Produto.nome).all()
  resumo = {"total": len(produtos), "esgotado": 0, "normal": 0}
  for produto in produtos:
      resumo[produto.situacao_estoque] += 1
  maior_estoque = max((p.estoque_atual for p in produtos), default=1) or 1

  if filtro in ("esgotado", "normal"):
      produtos = [p for p in produtos if p.situacao_estoque == filtro]


  ordem = {"esgotado": 0, "normal": 1}
  produtos.sort(key=lambda p: (ordem[p.situacao_estoque], p.nome.lower()))
  return render_template(
      "estoque.html", produtos=produtos, resumo=resumo, filtro=filtro, maior_estoque=maior_estoque
  )


@produto_bp.route("/estoque/<int:produto_id>/repor", methods=["POST"])
def repor(produto_id):
  produto = db.get_or_404(Produto, produto_id)
  quantidade = request.form.get("quantidade", type=int)

  if not quantidade or quantidade <= 0:
      flash("Informe uma quantidade maior que zero.", "danger")
  else:
      produto.dar_entrada(quantidade)
      db.session.commit()
      flash(f"+{quantidade} un. de \"{produto.nome}\". Estoque atual: {produto.estoque_atual}.", "success")
  return redirect(url_for("produtos.estoque", filtro=request.form.get("filtro", "todos")))

@produto_bp.route("/estoque/<int:produto_id>/ajustar", methods=["POST"])
def ajustar(produto_id):
  produto = db.get_or_404(Produto, produto_id)
  nova = request.form.get("quantidade", type=int)


  if nova is None or nova < 0:
      flash("Informe uma quantidade válida (zero ou mais).", "danger")
  else:
      anterior = produto.estoque_atual
      produto.estoque_atual = nova
      db.session.commit()
      flash(f"Estoque de \"{produto.nome}\" ajustado de {anterior} para {nova}.", "success")
  return redirect(url_for("produtos.estoque", filtro=request.form.get("filtro", "todos")))
