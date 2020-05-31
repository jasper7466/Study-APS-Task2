from flask import (
    Blueprint,
    request,
    jsonify
)
from flask.views import MethodView
from database import db
from auth import auth_required
from services.users import (
    UserService,
    RegistrationFailedError,
    UserDoesNotExistError
)

bp = Blueprint('users', __name__)


# Регистрация
class UsersRegisterView(MethodView):
    def post(self, account=None):
        # Получение данных запроса
        request_json = request.json

        with db.connection as con:
            service = UserService(con)
            try:
                new_user = service.create_user(request_json)
            except RegistrationFailedError:
                return '', 409
            else:
                return new_user, 201, {'Content-Type': 'application/json'}


# Взаимодействие (просмотр или частичное редактирование)
class UsersInteractView(MethodView):
    # Получение пользователя
    @auth_required
    def get(self, user_id, account_id):
        with db.connection as con:
            service = UserService(con)
            try:
                user = service.get_user(user_id)
            except UserDoesNotExistError:
                return '', 404
        return jsonify(dict(user)), 200, {'Content-Type': 'application/json'}

    # Частичное редактирование пользователя
    @auth_required
    def patch(self, user_id, account):
        if user_id != account['id']:
            return '', 403

        request_json = request.json
        first_name = request_json.get('first_name')
        if not first_name:
            return '', 400

        with db.connection as con:
            con.execute(
                'UPDATE account '
                'SET first_name = ? '
                'WHERE id = ?',
                (first_name, user_id),
            )
            con.commit()
        return '', 200


bp.add_url_rule('', view_func=UsersRegisterView.as_view('users'))
bp.add_url_rule('/<int:user_id>', view_func=UsersInteractView.as_view('user'))
