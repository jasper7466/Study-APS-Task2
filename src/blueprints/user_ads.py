from flask import (
    Blueprint,
    jsonify,
    request,
    session,
)
from flask.views import MethodView

from database import db


bp = Blueprint('user_ads', __name__)


class UserAdsView(MethodView):
    def get(self, seller_id):
        con = db.connection
        cur = con.execute(
            'SELECT * '
            'FROM ad '
            'WHERE seller_id = ?',
            (seller_id,),
        )
        result = cur.fetchall()
        return jsonify([dict(row) for row in result])


bp.add_url_rule('/<int:seller_id>/ads', view_func=UserAdsView.as_view('user_ads'))