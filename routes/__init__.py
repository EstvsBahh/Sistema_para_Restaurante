from routes.rotas_mesa import mesa_bp
from routes.rotas_categoria import categoria_bp
from routes.rotas_produto import produto_bp
from routes.rotas_garcom import garcom_bp
from routes.rotas_pedido import pedido_bp
from routes.rotas_pagamento import pagamento_bp


def registrar_rotas(app):
    app.register_blueprint(mesa_bp)
    app.register_blueprint(categoria_bp)
    app.register_blueprint(produto_bp)
    app.register_blueprint(garcom_bp)
    app.register_blueprint(pedido_bp)
    app.register_blueprint(pagamento_bp)
