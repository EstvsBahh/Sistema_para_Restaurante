import os

USUARIO = os.environ.get("DB_USUARIO", "avnadmin")
SENHA = os.environ.get("DB_SENHA", "AVNS_BvBkskh9MTJ9PQy8-cY")
HOST = os.environ.get("DB_HOST", "sistema-restaurante-sistemarestaurante.j.aivencloud.com")
PORTA = os.environ.get("DB_PORTA", "24632")
NOME_BANCO = os.environ.get("DB_NOME", "defaultdb")


class Config:
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{USUARIO}:{SENHA}@{HOST}:{PORTA}/{NOME_BANCO}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"ssl": {"ssl": True}}
    }