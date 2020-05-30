from flask import (
    Blueprint,
    request,
    session
)
from database import db
from werkzeug.security import check_password_hash

bp = Blueprint('auth', __name__)


# Авторизация
@bp.route('/auth/login', methods=['POST'])
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
@bp.route('/auth/logout', methods=['POST'])
def logout():
    session.pop('account_id', None)
    return '', 200
