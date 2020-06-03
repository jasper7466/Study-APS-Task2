from flask import (
    Blueprint,
    request,
    jsonify
)
from flask.views import MethodView
from database import db
from auth import seller_required

from services.colors import ColorsService

bp = Blueprint('colors', __name__)


class ColorsView(MethodView):
    @seller_required
    def post(self, account=None):
        """
        Обработчик метода POST для запроса на добавление нового цвета в БД.
        Из тела запроса в JSON-формате извлекает параметры:
        "name" - название цвета и "hex" - код цвета.

        Возвращает ответ в JSON-формате в виде объекта с параметрами цвета.
        Если цвет с заданным названием уже существует в БД - будут возвращены
        параметры из БД.

        :param account: {"account_id": account_id, "seller_id": seller_id}
        :return: {"id": color_id, "name": color_name, "hex": color_hex}
        """
        request_json = request.json
        color_name = request_json.get('name')
        color_hex = request_json.get('hex')
        with db.connection as con:
            service = ColorsService(con)
            color = service.add_color(color_name, color_hex)
        return jsonify(color), 200, {'Content-Type': 'application/json'}

    @seller_required
    def get(self, account=None):
        """
        Обработчик метода GET для запроса на получение списка цветов из БД.
        Параметры из тела запроса не используются.

        Возвращает ответ в JSON-формате в виде массива объектов
        с параметрами цветов.

        :param account: {"account_id": account_id, "seller_id": seller_id}
        :return: [{"id": color_id, "name": color_name, "hex": color_hex}, ... ]
        """
        with db.connection as con:
            service = ColorsService(con)
            colors = service.get_colors()
        return jsonify(colors), 200, {'Content-Type': 'application/json'}


bp.add_url_rule('', view_func=ColorsView.as_view('colors'))
