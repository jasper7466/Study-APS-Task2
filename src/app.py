from flask import Flask

from blueprints.ads import bp as ads_bp
from blueprints.auth import bp as auth_bp
from database import db


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    app.register_blueprint(auth_bp)
    app.register_blueprint(ads_bp)
    db.init_app(app)
    return app

