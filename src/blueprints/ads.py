from flask import (
    Blueprint,
    session,
    jsonify,
    request
)
from flask.views import MethodView
from database import db


bp = Blueprint('ads', __name__)


class AdsView(MethodView):
    def get(self):
        con = db.connection
        cur = con.execute(
            'SELECT * '
            'FROM ad '
        )
        result = cur.fetchall()
        return jsonify([dict(row) for row in result]), 200, {'Content-Type': 'application/json'}

    def post(self):
        seller_id = session.get('account_id')  # TODO заменить на seller_id
        date = 'test'
        car_id = 'test'

        if seller_id is None:
            return '', 403

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




bp.add_url_rule('', view_func=AdsView.as_view('ads'))

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