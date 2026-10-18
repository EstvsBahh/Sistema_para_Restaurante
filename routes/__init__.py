from routes.rotas_categoria import categoria_bp
from routes.rotas_garcom import garcom_bp
from routes.rotas_mesa import mesa_bp
from routes.rotas_pagamento import pagamento_bp
from routes.rotas_pedido import pedido_bp
from routes.rotas_produto import produto_bp

def registrar_rotas(app):
    for blueprint in (mesa_bp, categoria_bp, produto_bp, garcom_bp, pedido_bp, pagamento_bp):
        app.register_blueprint(blueprint)