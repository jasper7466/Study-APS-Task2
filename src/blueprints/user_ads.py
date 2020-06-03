from flask import (
    Blueprint,
    jsonify,
    request
)
from flask.views import MethodView
from database import db
from services.ads import (
    AdsService,
    AdExecuteError,
    SellerDoesNotExistError
)
from auth import seller_required


bp = Blueprint('user_ads', __name__)


class UserAdsView(MethodView):
    def get(self, account_id):
        """
        Обработчик GET-запроса на получение списка объявлений
        с опциональными query string параметрами через id пользователя.
        :param account_id:
        :return:
        """
        qs = dict(request.args)
        with db.connection as con:
            service = AdsService(con)
            try:
                ads = service.get_ads(account_id=account_id, qs=qs)
            except SellerDoesNotExistError:
                return '', 404
            else:
                return jsonify(ads), 200, {'Content-Type': 'application/json'}

    @seller_required
    def post(self, account, account_id):
        # Проверка соответствия id авторизованного пользователя и запрошенного id
        if account_id != account['account_id']:
            return 403

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


bp.add_url_rule('/<int:account_id>/ads', view_func=UserAdsView.as_view('user_ads'))
