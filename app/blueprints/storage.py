import json
from flask import Blueprint, jsonify, request, send_file
from http import HTTPStatus
from services import FileStorageService
from exceptions import *


storage = Blueprint("storage", __name__)


@storage.route("/files", methods=["GET"])
def get_files():
    path_to_folder = request.args.get("path_to_folder", "/")
    files = FileStorageService.get_files_in_folder(path_to_folder)
    return jsonify([file.to_dict() for file in files]), HTTPStatus.OK


@storage.route("/files/<string:file_id>", methods=["GET"])
def get_file(file_id):
    file = FileStorageService.get_file_by_id(file_id)
    if file is None:
        return (
            jsonify({"error": "File with this id was not found"}),
            HTTPStatus.NOT_FOUND,
        )
    return jsonify(file.to_dict()), HTTPStatus.OK


@storage.route("/files/<string:file_id>", methods=["DELETE"])
def delete_file(file_id):
    file = FileStorageService.get_file_by_id(file_id)
    if file is None:
        return (
            jsonify({"error": "File with this id was not found"}),
            HTTPStatus.NOT_FOUND,
        )
    try:
        FileStorageService.delete_file(file)
    except FileDeleteError:
        return (
            jsonify({"error": "Error deleting file from storage"}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
    except DatabaseDeleteError:
        return (
            jsonify({"error": "Error deleting file from DB"}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
    return jsonify(file.to_dict()), HTTPStatus.OK


@storage.route("/files", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No part file"}), HTTPStatus.BAD_REQUEST
    if "json" not in request.form:
        return jsonify({"error": "No part metadata"}), HTTPStatus.BAD_REQUEST

    uploaded_file = request.files["file"]
    data = json.loads(request.form["json"])

    try:
        new_file = FileStorageService.upload_file(uploaded_file, data)
    except InvalidPathError:
        return (
            jsonify({"error": "Filepath is not valid"}),
            HTTPStatus.CONFLICT,
        )
    except FileExistsError:
        return (
            jsonify({"error": "File with same name already exist"}),
            HTTPStatus.CONFLICT,
        )
    except FileSaveError:
        return jsonify({"error": "File saving error"}), HTTPStatus.INTERNAL_SERVER_ERROR
    except DatabaseAddError:
        return (
            jsonify({"error": "Error adding file information to DB"}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
    return jsonify(new_file.to_dict()), HTTPStatus.CREATED


@storage.route("/files/<string:file_id>/download", methods=["GET"])
def download_file(file_id):
    file = FileStorageService.get_file_by_id(file_id)
    if file is None:
        return (
            jsonify({"error": "File with this id was not found"}),
            HTTPStatus.NOT_FOUND,
        )
    return (
        send_file(FileStorageService.get_abs_path(file), as_attachment=True),
        HTTPStatus.OK,
    )


@storage.route("/files/sync", methods=["POST"])
def sync_storage():
    try:
        files_to_add, files_to_delete = FileStorageService.sync_storage()
    except DatabaseAddError:
        return (
            jsonify({"error": "Error adding file in DB"}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
    except DatabaseDeleteError:
        return (
            jsonify({"error": "Error deleting file in DB"}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
    return (
        jsonify(
            {
                "files_to_add": list(files_to_add),
                "files_to_delete": list(files_to_delete),
            }
        ),
        HTTPStatus.OK,
    )


@storage.route("/files/<string:file_id>", methods=["PUT"])
def update_file(file_id):
    file = FileStorageService.get_file_by_id(file_id)
    if file is None:
        return (
            jsonify({"error": "File with this id was not found"}),
            HTTPStatus.NOT_FOUND,
        )
    new_data = request.get_json()
    try:
        file = FileStorageService.update_file(file, new_data)
    except InvalidPathError:
        return (
            jsonify({"error": "Filepath is not valid"}),
            HTTPStatus.CONFLICT,
        )
    except FileExistsError:
        return (
            jsonify({"error": "File with same name already exist"}),
            HTTPStatus.CONFLICT,
        )
    except DatabaseUpdateError:
        return (
            jsonify({"error": "Error updating file data in DB"}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
    except FileMoveError:
        return (
            jsonify({"error": "Error moving file in storage"}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
    except FileRenameError:
        return (
            jsonify({"error": "Error renaming file in storage"}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
    return jsonify(file.to_dict()), HTTPStatus.OK
