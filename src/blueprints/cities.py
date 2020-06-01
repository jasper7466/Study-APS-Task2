from flask import (
    Blueprint,
    request,
    jsonify
)
from flask.views import MethodView
from database import db
from auth import auth_required

from services.cities import CitiesService

bp = Blueprint('cities', __name__)


class CitiesView(MethodView):
    @auth_required
    def post(self, account=None):
        """
        Обработчик метода POST для запроса на добавление нового города в БД.
        Из тела запроса в JSON-формате извлекает параметр "name" - название города.

        Возвращает ответ в JSON-формате в виде объекта с параметрами города.
        Если город с заданным названием уже существует в БД - будут возвращены
        параметры из БД.

        :param account: {"account_id": account_id, "seller_id": seller_id}
        :return: {"id": city_id, "name": city_name}
        """
        request_json = request.json
        city_name = request_json.get('name')
        with db.connection as con:
            service = CitiesService(con)
            city = service.add_city(city_name)
        return jsonify(city), 200, {'Content-Type': 'application/json'}

    @auth_required
    def get(self, account=None):
        """
        Обработчик метода GET для запроса на получение списка городов из БД.
        Параметры из тела запроса не используются.

        Возвращает ответ в JSON-формате в виде массива объектов
        с параметрами городов.

        :param account: {"account_id": account_id, "seller_id": seller_id}
        :return: [{"id": city_id, "name": city_name}, ... ]
        """
        with db.connection as con:
            service = CitiesService(con)
            colors = service.get_cities()
        return jsonify(colors), 200, {'Content-Type': 'application/json'}


bp.add_url_rule('', view_func=CitiesView.as_view('cities'))
