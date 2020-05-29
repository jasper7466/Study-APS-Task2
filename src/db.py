import sqlite3 as sqlite

from flask import (
    g,
    current_app,
)


def get_db():
    if 'db' not in g:
        g.db = sqlite.connect(
            current_app.config['DB_CONNECTION'],
            detect_types=sqlite.PARSE_DECLTYPES | sqlite.PARSE_COLNAMES
        )
        g.db.row_factory = sqlite.Row
    return g.db


def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()
