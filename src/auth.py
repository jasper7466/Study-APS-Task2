from functools import wraps
from flask import session
from database import db


def auth_required(view_func):
    """
    Декоратор, применяется к функциям/методам для вызова которых
    требуется авторизация в роли пользователя или продавца.
    """
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
    """
    Декоратор, применяется к функциям/методам для вызова которых
    требуется авторизация в роли продавца.
    """
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        account_id = session.get('account_id')
        seller_id = session.get('seller_id')
        if not account_id or not seller_id:
            return '', 403
        with db.connection as con:
            cur = con.execute(f'''
                SELECT account.id as account_id, seller.id as seller_id
                FROM account
                    JOIN seller ON seller.id = account.id
                WHERE account.id = {account_id} AND seller.id = {seller_id}
            ''')
            account = cur.fetchone()
        if not account:
            return '', 403
        return view_func(*args, **kwargs, account=dict(account))
    return wrapper
