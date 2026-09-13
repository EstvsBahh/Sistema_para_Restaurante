
from extensions import db
from routes import registrar_rotas
import models  
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template
from config import Config

def criar_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = "chave-secreta-desenvolvimento"  

    db.init_app(app)
    registrar_rotas(app)

    @app.route("/")
    def home():
        return render_template("home.html")

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = criar_app()
    app.run(debug=True)
