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
    AdPermissionError,
    AdExecuteError
)


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
        :return: response
        """
        seller_id = account['seller_id']
        request_json = request.json
        if not request_json:
            return '', 400

        with db.connection as con:
            service = AdsService(con)
            try:
                ad = service.publish(request_json, seller_id)
            except AdExecuteError:
                con.rollback()
                return '', 409
            else:
                return jsonify(dict(ad)), 201


class AdView(MethodView):
    def get(self, ad_id):
        """
        Обработчик GET-запроса на получение объявления по его id
        :param ad_id: идентификатор объявления
        """
        with db.connection as con:
            service = AdsService(con)
            try:
                ad = service.get_formatted_ad(ad_id)
            except AdDoesNotExistError:
                return '', 404
            else:
                return jsonify(dict(ad))

    @seller_required
    def patch(self, account, ad_id):
        """
        Обработчик PATCH-запроса на частичное редактирование объявления.
        :param account: параметры авторизации
        :param ad_id: идентификатор объявления
        :return: response
        """
        seller_id = account['seller_id']
        request_json = request.json
        if not request_json:
            return '', 400

        with db.connection as con:
            service = AdsService(con)
            try:
                service.edit_ad(ad_id, seller_id, request_json)
            except AdPermissionError:
                return '', 403
            except AdDoesNotExistError:
                return '', 404
            except AdExecuteError:
                con.rollback()
                return '', 409
            else:
                return '', 200

    @seller_required
    def delete(self, account, ad_id):
        """
        Обраюотчик DELETE-запроса на удаление объявления.
        :param account: параметры авторизации
        :param ad_id: идентификатор
        :return: response
        """
        seller_id = account['seller_id']

        with db.connection as con:
            service = AdsService(con)
            try:
                service.delete_ad(ad_id, seller_id)
            except AdPermissionError:
                return '', 403
            except AdDoesNotExistError:
                return '', 404
            except AdExecuteError:
                con.rollback()
                return '', 409
            else:
                return '', 200


bp.add_url_rule('', view_func=AdsView.as_view('ads'))
bp.add_url_rule('/<int:ad_id>', view_func=AdView.as_view('ad'))
