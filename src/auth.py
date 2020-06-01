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
                'SELECT id '
                'FROM account '
                'WHERE id = ?',
                (account_id,),
            )
            account = cur.fetchone()
        if not account:
            return '', 403
        return view_func(*args, **kwargs, account=account)
    return wrapper


def seller_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        account_id = session.get('account_id')
        seller_id = session.get('seller_id')
        if not account_id or not seller_id:
            return '', 403
        with db.connection as con:
            cur = con.execute(
                'SELECT account.id, seller.id '
                'FROM account, seller '
                'WHERE account.id = ? AND seller.id = ?',
                (account_id, seller_id),
            )
            account = cur.fetchone()
        if not account:
            return '', 403
        return view_func(*args, **kwargs, account=account)
    return wrapper
