from flask import (
    Blueprint,
    jsonify,
    request
)
from flask.views import MethodView
from database import db
from auth import auth_required
from services.ads import (
    AdsService,
    AdDoesNotExistError
)


bp = Blueprint('ads', __name__)


class AdsView(MethodView):
    def get(self):
        """
        Обработчик запроса на получение всех объявлений.
        """
        qs = dict(request.args)
        with db.connection as con:
            service = AdsService(con)
            ads = service.get_ads(qs=qs)
        return jsonify(ads), 200, {'Content-Type': 'application/json'}

    @auth_required
    def post(self, account):
        seller_id = account['id']
        date = 'test'                          # TODO убрать заглушки, доделать
        car_id = 'test'

        request_json = request.json
        title = request_json.get('title')

        if not title:
            return '', 400

        con = db.connection
        cur = con.execute(
            'INSERT INTO ad (title, date, seller_id, car_id) '
            'VALUES (?, ?, ?, ?)',
            (title, date, seller_id, car_id),
        )
        con.commit()
        ad_id = cur.lastrowid
        cur = con.execute(
            'SELECT * '
            'FROM ad '
            'WHERE id = ?',
            (ad_id,),
        )
        ad = cur.fetchone()
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
