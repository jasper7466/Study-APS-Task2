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
    UserDoesNotExistError,
    UserUpdateFailedError
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
    def get(self, user_id, account):
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

        with db.connection as con:
            service = UserService(con)
            try:
                user = service.edit_user(user_id, request_json)
            except UserUpdateFailedError:
                return '', 400
        return jsonify(dict(user)), 200, {'Content-Type': 'application/json'}


bp.add_url_rule('', view_func=UsersRegisterView.as_view('users'))
bp.add_url_rule('/<int:user_id>', view_func=UsersInteractView.as_view('user'))
