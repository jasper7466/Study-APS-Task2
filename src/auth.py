from functools import wraps
from flask import session
from database import db


def auth_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        account_id = session.get('account_id')
        if not account_id:
            return '', 403
        with db.connection as con:
            cur = con.execute(
                'SELECT id, first_name '
                'FROM account '
                'WHERE id = ?',
                (account_id,),
            )
            account = cur.fetchone()
        if not account:
            return '', 403
        return view_func(*args, **kwargs, account=account)
    return wrapper
