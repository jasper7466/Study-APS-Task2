from flask import (
    Blueprint,
    jsonify
)
from flask.views import MethodView
from database import db
from services.ads import AdsService


bp = Blueprint('user_ads', __name__)


class UserAdsView(MethodView):
    # Получение объявлений пользователя
    def get(self, account_id):
        with db.connection as con:
            service = AdsService(con)
            ads = service.get_ads(account_id=account_id)
        return jsonify(ads) , 200, {'Content-Type': 'application/json'}


bp.add_url_rule('/<int:account_id>/ads', view_func=UserAdsView.as_view('user_ads'))
