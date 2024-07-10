from flask import Flask
import blueprints as bp
from db.postgres import db
import os


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
db.init_app(app)
with app.app_context():
    db.create_all()
app.register_blueprint(bp.storage)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
