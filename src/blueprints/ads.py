from flask import (
    Blueprint,
    jsonify,
    request
)
from flask.views import MethodView
from database import db
from auth import seller_required
from services.ads import (
    AdsService,
    AdDoesNotExistError,
    AdPublishError
)
from datetime import datetime


bp = Blueprint('ads', __name__)


class AdsView(MethodView):
    def get(self):
        """
        Обработчик GET-запроса на получение списка объявлений
        с опциональными query string параметрами.
        :return: response
        """
        qs = dict(request.args)
        with db.connection as con:
            service = AdsService(con)
            ads = service.get_ads(qs=qs)
        return jsonify(ads), 200, {'Content-Type': 'application/json'}

    @seller_required
    def post(self, account):
        """
        Обработчик POST-запрса на создание объявления.
        :param account: параметры авторизации
        :return:
        """
        seller_id = account['seller_id']
        request_json = request.json
        if not request_json:
            return '', 400

        # Добавляем в запрос метку времени и id продавца
        request_json.update({'date': int(datetime.now().timestamp())})
        request_json.update({'seller_id': seller_id})
        # Добавляем в кол-во владельцев (если не задано) TODO
        if not request_json.get('num_owners'):
            request_json.update({'num_owners': 0})

        with db.connection as con:
            service = AdsService(con)
            try:
                ad = service.publish(request_json)
            except AdPublishError:
                con.rollback()
                return '', 409
            else:
                return jsonify(dict(ad)), 201


class AdView(MethodView):
    def get(self, ad_id):
        """
        Обработчик запроса на получение объявления по его id
        :param ad_id: id объявления
        """
        with db.connection as con:
            service = AdsService(con)
            try:
                ad = service.get_ad(ad_id)
            except AdDoesNotExistError:
                return '', 404
            else:
                return jsonify(dict(ad))


bp.add_url_rule('', view_func=AdsView.as_view('ads'))
bp.add_url_rule('/<int:ad_id>', view_func=AdView.as_view('ad'))
