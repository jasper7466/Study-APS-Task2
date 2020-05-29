from os import environ


class Config:
    DB_CONNECTION = environ.get('DB_CONNECTION', 'example.db')
    SECRET_KEY = environ.get('SECRET_KEY', 'secret_key').encode()
