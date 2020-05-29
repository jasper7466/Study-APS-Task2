import sqlite3 as sqlite
from flask import (
    Flask,
    jsonify,
    request,
    session #, render_template, make_response
)
from flask.views import MethodView
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)
from database import db


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    db.init_app(app)

    @app.route('/ads')
    def get_ads():
        account_id = session.get('account_id')
        if account_id is None:
            return '', 403
        con = db.connection
        cur = con.execute(
            'SELECT * '
            'FROM ad '
            'WHERE seller_id = ?',
            (account_id,),
        )
        result = cur.fetchall()
        return jsonify([dict(row) for row in result]), 200, {'Content-Type': 'application/json'}

    # Авторизация
    @app.route('/auth/login', methods=['POST'])
    def login():
        valid = True

        request_json = request.json
        user = {
            'email': None,
            'password': None
        }
        for key in user:
            user[key] = request_json.get(key)
            if user[key] is None:
                valid = False
        if not valid:
            return '', 400

        con = db.connection
        cur = con.execute(
            'SELECT * '
            'FROM account '
            'WHERE email = ?',
            (user['email'],),
        )
        account = cur.fetchone()

        if account is None:
            return '', 403

        if not check_password_hash(account['password'], user['password']):
            return '', 403

        session['account_id'] = account['id']
        return '', 200

    # Выход
    @app.route('/auth/logout', methods=['POST'])
    def logout():
        session.pop('account_id', None)
        return '', 200

    # Регистрация
    @app.route('/users', methods=['POST'])
    def register():     # TODO: доделать response, возвращать id пользователя
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
    return app

