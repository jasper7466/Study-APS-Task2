from flask import (
    Blueprint,
    jsonify,
    request
)
from flask.views import MethodView
from database import db
from auth import auth_required
from services.ads import AdsService


bp = Blueprint('ads', __name__)


class AdsView(MethodView):
    def get(self):
        with db.connection as con:
            service = AdsService(con)
            ads = service.get_ads()
        return jsonify(ads), 200, {'Content-Type': 'application/json'}

    @auth_required      # TODO заменить на seller_required
    def post(self, user):
        seller_id = user['id']
        date = 'test'                          # TODO убрать заглушки
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
        con = db.connection
        cur = con.execute(
            'SELECT * '
            'FROM ad '
            'WHERE id = ?',
            (ad_id,),
        )
        ad = cur.fetchone()
        if ad is None:
            return '', 404
        return jsonify(dict(ad))


bp.add_url_rule('', view_func=AdsView.as_view('ads'))
bp.add_url_rule('/<int:ad_id>', view_func=AdView.as_view('ad'))

# @bp.route('/ads')
# def get_ads():
#     account_id = session.get('account_id')
#     if account_id is None:
#         return '', 403
#     con = db.connection
#     cur = con.execute(
#         'SELECT * '
#         'FROM ad '
#         'WHERE seller_id = ?',
#         (account_id,),
#     )
#     result = cur.fetchall()
#     return jsonify([dict(row) for row in result]), 200, {'Content-Type': 'application/json'}