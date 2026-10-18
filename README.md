# Sistema para Restaurante

Sistema web desenvolvido para auxiliar no gerenciamento de um restaurante, permitindo controlar mesas, produtos, garçons, pedidos e pagamentos de forma organizada e centralizada.

## Objetivo

Facilitar o atendimento do restaurante, permitindo registrar pedidos, acompanhar seu andamento, calcular valores e finalizar contas de maneira rápida e confiável.

## Documentação do Projeto

O detalhamento dos requisitos, diagrama de casos de uso e diagrama de classes podem ser consultados no documento oficial:

**[Acessar Documentação em PDF](./docs/Documentacao_SIstema_para_Restaurantes.pdf)**


## Funcionalidades

| Área | O que faz |
|---|---|
| **Dashboard** | Faturamento do dia, ticket médio, taxa de serviço arrecadada, pedidos em andamento, ocupação das mesas e mais vendidos |
| **Mesas** | Mapa do salão (livre / ocupada / reservada), reserva, edição e acesso direto ao pedido da mesa |
| **Novo pedido** | Comanda ágil: toque nos produtos, ajuste quantidades, observações por item e envio à cozinha |
| **Pedido** | Etapas (aberto → em preparo → pronto → entregue → pago), inclusão/remoção de itens, cancelamento |
| **Cozinha** | Painel em tempo real (atualiza a cada 15 s) com cores por tempo de espera |
| **Caixa** | Abertura/fechamento, recebimento (dinheiro, cartão, pix) com troco, **taxa de serviço opcional de 10%**, suprimento e sangria, conferência do fechamento |
| **Cardápio** | Produtos, categorias, busca e filtros; retirar/voltar ao cardápio sem perder histórico |
| **Estoque** | Baixa automática por pedido, reposição, ajuste por contagem e bloqueio de produtos esgotados |
| **Garçons** | Cadastro, ativação/desativação e pedidos em andamento |


### Regras de negócio implementadas

- Uma mesa só pode ter **um pedido em andamento**; ela fica ocupada até o pagamento ou cancelamento.
- A **baixa de estoque** ocorre quando o item entra no pedido; cancelar o pedido ou remover o item devolve o estoque.
- Produto com estoque zero fica **indisponível** automaticamente e não pode ser pedido.
- A **taxa de serviço** é de 10% sobre o total dos itens, **opcional**: o caixa decide se cobra no momento do pagamento.
- O preço do item fica **congelado** no pedido (reajustes não alteram pedidos antigos).
- Pagamento exige **caixa aberto**; ao pagar, o pedido é finalizado e a **mesa é liberada**.
- Produtos e garçons com histórico não são apagados — apenas desativados.


## Tecnologias

| Python 
| Flask 
| Flask-SQLAlchemy 
| Flask-Migrate
| Jinja2
| Bootstrap 5
| Font Awesome
| HTML 
| CSS 
| MYSQL


## Estrutura do projeto

```
├── app.py              # Application Factory, filtros Jinja e dashboard
├── config.py           # Configurações (lê variáveis do .env)
├── extensions.py       # db e migrate (evita importação circular)
├── seed.py             # Dados de exemplo
├── requirements.txt
├── .env.example
├── models/             # Mesa, Categoria, Produto, Garcom, Pedido, ItemPedido, Pagamento, Caixa
├── routes/             # Blueprints: uma rota por área do sistema
├── templates/          # Telas HTML (Jinja2 + Bootstrap 5)
└── static/css/style.css
```


## Como rodar

```bash
# 1. Instalar as dependências
pip install -r requirements.txt

# 2. (Opcional) criar o arquivo de configuração
cp .env.example .env

# 3. (Opcional) popular com dados de exemplo
python seed.py

# 4. Iniciar o sistema
python app.py
```

No arquivo `.env`, defina:

```
DATABASE_URL=mysql+pymysql://usuario:senha@host:3306/nome_do_banco
# DB_SSL=1   (apenas se o provedor exigir SSL, ex: Aiven)
```

> **Atualizando de uma versão anterior:** esta versão removeu a coluna `estoque_minimo` (produtos) e criou `taxa_servico` (pagamentos). O `create_all` não altera tabelas já existentes, então apague o arquivo `restaurante.db` (ou as tabelas do MySQL) e rode `python seed.py` novamente.

> As tabelas deste projeto usam nomes no plural (`mesas`, `produtos`, `pedidos`...). Se o banco MySQL já tiver tabelas de uma versão anterior (`mesa`, `produto`...), elas não são alteradas — use um banco novo ou apague as tabelas antigas.


## Fluxo de uso

1. **Caixa** → abrir o caixa com o saldo inicial.
2. **Mesas** → “Abrir pedido” na mesa desejada (ou **Novo pedido** no menu).
3. Montar a comanda e lançar → o pedido aparece na **Cozinha**.
4. Cozinha marca **pronto** → garçom marca **entregue**.
5. **Caixa** → receber o pagamento → pedido pago e mesa liberada.
6. Ao fim do dia, **fechar o caixa** e conferir a diferença.


## Integrantes

* Bárbara Ferreira Esteves
* Gabriel Ferrari
* Julia Roberta
* Kamilly Ribeiro
