import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

USUARIO = os.environ.get("DB_USUARIO", "root")
SENHA = os.environ.get("DB_SENHA", "")
HOST = os.environ.get("DB_HOST", "localhost")
PORTA = os.environ.get("DB_PORTA", "3306")
NOME_BANCO = os.environ.get("DB_NOME", "sistema_restaurante")

USAR_SSL = os.environ.get("DB_SSL", "1") == "1"


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-chave-secreta-troque-em-producao")
    NOME_RESTAURANTE = os.environ.get("NOME_RESTAURANTE", "Só as Delicias")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{quote_plus(USUARIO)}:{quote_plus(SENHA)}@{HOST}:{PORTA}/{NOME_BANCO}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    if USAR_SSL:
        SQLALCHEMY_ENGINE_OPTIONS["connect_args"] = {"ssl": {"ssl": True}}