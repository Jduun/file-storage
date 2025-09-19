import json
from http import HTTPStatus

import flask
from flask import jsonify, send_file, request
from werkzeug.datastructures import FileStorage

from src.models import FileUploadDTO, FileUpdateDTO
from src.injectors import services

files_routers = flask.Blueprint(
    "files",
    __name__,
    url_prefix="/api/files/",
)


@files_routers.route("/", methods=["POST"])
def upload_file():
    if "file" not in flask.request.files:
        return jsonify({"error": "No part file"}), HTTPStatus.BAD_REQUEST
    if "json" not in flask.request.form:
        return (
            jsonify({"error": "No part metadata"}),
            HTTPStatus.BAD_REQUEST,
        )

    file: FileStorage = flask.request.files["file"]
    file_bytes: bytes = file.stream.read()
    json_data = json.loads(flask.request.form["json"])
    file_data = FileUploadDTO(
        file_bytes=file_bytes,
        filename=file.filename,
        filepath=json_data.get("filepath", "/"),
        comment=json_data.get("comment", ""),
    )

    fs = services.file_service()
    res = fs.upload(file_data)
    return jsonify(res)


@files_routers.route("/", methods=["GET"])
def get_files():
    fs = services.file_service()
    res = fs.get_all()
    return jsonify(res)


@files_routers.route("/<int:file_id>", methods=["GET"])
def get_file(file_id):
    fs = services.file_service()
    res = fs.get(file_id)
    return jsonify(res)


@files_routers.route("/<int:file_id>", methods=["PUT"])
def update_file(file_id):
    fs = services.file_service()
    json_data = request.get_json()
    file_data = FileUpdateDTO(**json_data)
    res = fs.update(file_id, file_data)
    return jsonify(res)


@files_routers.route("/<int:file_id>", methods=["DELETE"])
def delete_file(file_id):
    fs = services.file_service()
    res = fs.delete(file_id)
    return jsonify(res)


@files_routers.route("/<int:file_id>/download", methods=["GET"])
def download_file(file_id):
    fs = services.file_service()
    file = fs.get(file_id)
    return (
        send_file(fs.get_abs_path(file), as_attachment=True),
        HTTPStatus.OK,
    )
