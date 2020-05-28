from flask import Flask, jsonify #, request, render_template, make_response
from flask.views import MethodView
from db import get_db, close_db

app = Flask(__name__)
app.teardown_appcontext(close_db)


@app.route('/ads')
def get_ads():
    con = get_db()
    cur = con.execute("""
        SELECT *
        FROM ad
    """)
    result = cur.fetchall()
    return jsonify([dict(row) for row in result]), 200, {'Content-Type': 'application/json'}


@app.route('/login', methods=['POST'])
def login():
    pass


@app.route('/logout', methods=['POST'])
def logout():
    pass


@app.route('/register', methods=['POST'])
def register():
    pass
