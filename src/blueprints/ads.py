from flask import (
    Blueprint,
    session,
    jsonify
)

from database import db

bp = Blueprint('ads', __name__)


@bp.route('/ads')
def get_ads():
    account_id = session.get('account_id')
    if account_id is None:
        return '', 403
    con = db.connection
    cur = con.execute(
        'SELECT * '
        'FROM ad '
        'WHERE seller_id = ?',
        (account_id,),
    )
    result = cur.fetchall()
    return jsonify([dict(row) for row in result]), 200, {'Content-Type': 'application/json'}