import os

USUARIO = os.environ.get("DB_USUARIO", "root")
SENHA = os.environ.get("DB_SENHA", "")
HOST = os.environ.get("DB_HOST", "localhost")
PORTA = os.environ.get("DB_PORTA", "3306")
NOME_BANCO = os.environ.get("DB_NOME", "sistema_restaurante")


class Config:
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{USUARIO}:{SENHA}@{HOST}:{PORTA}/{NOME_BANCO}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"ssl": {"ssl": True}}
    }