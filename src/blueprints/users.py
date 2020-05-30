import sqlite3 as sqlite
from flask import (
    Blueprint,
    request
)
from flask.views import MethodView
from werkzeug.security import generate_password_hash
from database import db


bp = Blueprint('users', __name__)


class UsersView(MethodView):
    # Регистрация
    def post(self):
        # Получение данных запроса
        request_json = request.json

        # Обязательные поля для любого аккаунта
        account = {
            'email': None,
            'password': None,
            'first_name': None,
            'last_name': None,
            'is_seller': None
        }

        # Заполнение в полей словаря
        for key in account:
            account[key] = request_json.get(key)

        # Проверка на наличие минимально необходимого набора полей
        for key in account:
            if account[key] is None:
                return '', 400

        # Проверка на наличие дополнительного набора полей
        if account['is_seller']:
            # Обязательные поля для аккаунта продавца
            seller = {
                'phone': None,
                'zip_code': None,
                'city_id': None,
                'street': None,
                'home': None
            }

            # Заполнение в полей словаря
            for key in seller:
                seller[key] = request_json.get(key)

            for record in seller:
                if request_json.get(record) is None:
                    return '', 400

        password_hash = generate_password_hash(account['password'])

        # Работа с БД
        con = db.connection
        cur = con.cursor()

        # Включение проверки ссылочной целостности
        cur.execute("PRAGMA foreign_keys = ON;")
        try:
            cur.execute(
                'INSERT INTO account (email, password, first_name, last_name) '
                'VALUES(?, ?, ?, ?) ',
                (account['email'], password_hash, account['first_name'], account['last_name']),
            )
            if account['is_seller']:
                account_id = cur.lastrowid
                cur.execute(
                    'INSERT INTO seller (phone, zip_code, street, home, account_id) '
                    'VALUES(?, ?, ?, ?, ?)',
                    (seller['phone'], seller['zip_code'], seller['street'], seller['home'], account_id),
                )
            con.commit()
        except sqlite.IntegrityError as e:
            print(e)
            con.rollback()
            return account, 409
        return account, 201
        # return jsonify([dict(row) for row in rows]) TODO


bp.add_url_rule('', view_func=UsersView.as_view('users'))
