from flask import Flask
from blueprints import storage, image
from db.postgres import db


def create_app(config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.register_blueprint(storage)
    app.register_blueprint(image)
    return app
