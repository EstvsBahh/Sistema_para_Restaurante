# Sistema para Restaurante

Sistema web desenvolvido para auxiliar no gerenciamento de um restaurante, permitindo controlar mesas, produtos, garçons, pedidos e pagamentos de forma organizada e centralizada.

## Objetivo

Facilitar o atendimento do restaurante, permitindo registrar pedidos, acompanhar seu andamento, calcular valores e finalizar contas de maneira rápida e confiável.


## Funcionalidades

**Cadastros**
- Cadastro de produtos (com controle de estoque)
- Cadastro de categorias
- Cadastro de mesas
- Cadastro de garçons

**Estoque**
- Controle de quantidade em estoque por produto
- Entrada de estoque (reposição)
- Alerta de estoque baixo (abaixo do mínimo definido)
- Bloqueio automático de produtos sem estoque disponível
- Remoção/retorno de produtos ao cardápio sem apagar o histórico

**Pedidos**
- Abertura de pedidos associados a mesa e garçom
- Adição de produtos aos pedidos, com baixa automática de estoque
- Acompanhamento do estado do pedido (aberto → em preparo → pronto → finalizado)
- Painel da cozinha

**Pagamentos e finalização**
- Cálculo automático do valor total
- Registro de pagamento (dinheiro, cartão, pix)
- Finalização do pedido
- Liberação automática da mesa


## Tecnologias

| Python 
| Flask 
| Flask-SQLAlchemy 
| HTML 
| CSS 
| MYSQL


## Estrutura do projeto

```
sistema_restaurante/
├── app.py               
├── config.py             
├── extensions.py         
├── requirements.txt
├── seed.py               
├── models/               
├── routes/               
├── templates/          
└── static/css/         
```


## Como rodar o projeto

1. Clone o repositório e entre na pasta:
```bash
git clone https://github.com/EstvsBahh/Sistema_para_Restaurante.git
cd Sistema_para_Restaurante
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Crie um arquivo `.env` na raiz do projeto (baseado no `.env.example`) com os dados do seu banco MySQL:
```
DB_USUARIO=seu_usuario
DB_SENHA=sua_senha
DB_HOST=seu_host
DB_PORTA=sua_porta
DB_NOME=sistema_restaurante
```

4. Popule o banco com dados de teste (opcional):
```bash
python seed.py
```

5. Rode a aplicação:
```bash
python app.py
```

6. Acesse em `http://127.0.0.1:5000`


## Integrantes

* Bárbara Ferreira Esteves
* Gabriel Ferrari
* Julia Roberta
* Kamilly Ribeiro
