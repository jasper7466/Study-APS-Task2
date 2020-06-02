from flask import (
    Blueprint,
    jsonify,
    request
)
from flask.views import MethodView
from database import db
from services.ads import AdsService


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
            ads = service.get_ads(account_id=account_id, qs=qs)
        return jsonify(ads), 200, {'Content-Type': 'application/json'}


bp.add_url_rule('/<int:account_id>/ads', view_func=UserAdsView.as_view('user_ads'))
