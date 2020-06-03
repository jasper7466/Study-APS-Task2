from flask import (
    Blueprint,
    request,
    session
)
from database import db
from services.auth import (
    AuthService,
    AuthorizationFailedError,
    SellerDoesNotExistError
)

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['POST'])
def login():
    """
    Обработчик POST-запроса на авторизацию пользователя.
    :return: response
    """
    request_json = request.json
    email = request_json.get('email')
    password = request_json.get('password')
    with db.connection as con:
        service = AuthService(con)
        # Попытка авторизации в роли пользователя
        try:
            account_id = service.login(email, password)
        except AuthorizationFailedError:
            return '', 401
        else:
            session['account_id'] = account_id
            # Попытка авторизации в роли продавца
            try:
                seller_id = service.get_seller(account_id)
            except SellerDoesNotExistError:
                pass
            else:
                session['seller_id'] = seller_id
            return '', 200


@bp.route('/logout', methods=['POST'])
def logout():
    """
    Обработчик POST-запроса на завершение сессии.
    :return:
    """
    session.pop('account_id', None)
    session.pop('seller_id', None)
    return '', 200
