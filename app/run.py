from flask import Flask
from config import Config
from blueprints import storage
from db.postgres import db
from app import create_app

app = create_app(Config)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
