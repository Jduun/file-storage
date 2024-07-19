import pytest
from app.app import create_app
from db.postgres import db
from config import TestConfig
import shutil
from . import ROOT_FOLDER, test_files
import os
import requests


@pytest.fixture
def app():
    app = create_app(TestConfig)
    init_data(app)
    auto_auth()
    yield app
    clear_data(app)


@pytest.fixture()
def client(app):
    return app.test_client()


def init_data(app):
    with app.app_context():
        db.create_all()
        db.session.bulk_save_objects(test_files)
        db.session.commit()
        for i in range(len(test_files)):
            path_to_folder = ROOT_FOLDER + test_files[i].filepath
            os.makedirs(path_to_folder, exist_ok=True)
            full_filepath = (
                path_to_folder + test_files[i].filename + test_files[i].extension
            )
            with open(full_filepath, "w"):
                pass


def clear_data(app):
    with app.app_context():
        db.drop_all()
    if os.path.exists(ROOT_FOLDER):
        shutil.rmtree(ROOT_FOLDER)


def auto_auth():
    response = requests.post(
        "http://localhost:5000/login",
        json={"login": os.getenv("USER_LOGIN"), "password": os.getenv("USER_PASSWORD")},
    )
