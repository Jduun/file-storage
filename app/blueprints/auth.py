from flask import Blueprint, jsonify, request, make_response
from http import HTTPStatus
import uuid
from exceptions import *
from services import auth_service
from . import image, storage
import os

auth = Blueprint("auth", __name__)


@image.before_request
@storage.before_request
def check_session():
    if request.endpoint not in ["auth.login"]:
        session_id = request.cookies.get("session_id")
        if not auth_service.is_session_exist(session_id):
            return (
                "Please log into your account",
                HTTPStatus.UNAUTHORIZED,
            )


@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if "login" not in data or "password" not in data:
        return (
            jsonify({"error": "Login and password must be provided"}),
            HTTPStatus.BAD_REQUEST,
        )
    user_login = data["login"]
    user_password = data["password"]

    if user_login != os.getenv("USER_LOGIN") or user_password != os.getenv(
        "USER_PASSWORD"
    ):
        return (
            "Invalid login or password",
            HTTPStatus.UNAUTHORIZED,
        )

    session_id = str(uuid.uuid4())
    try:
        auth_service.set_session(session_id)
    except DatabaseAddError:
        return (
            jsonify({"error": "Error adding file information to DB"}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
    resp = make_response("You have successfully logged in")
    resp.set_cookie("session_id", session_id)

    return resp, HTTPStatus.OK
