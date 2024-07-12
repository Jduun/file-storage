import json
from flask import Blueprint, jsonify, request, send_file
from http import HTTPStatus
from services import FileService

storage = Blueprint("storage", __name__)


@storage.route("/files", methods=["GET"])
def get_files():
    path_to_folder = request.args.get("path_to_folder", "/")
    files = FileService.get_files_in_folder(path_to_folder)
    return jsonify([file.to_dict() for file in files]), HTTPStatus.OK


@storage.route("/files/<string:file_id>", methods=["GET"])
def get_file(file_id):
    file = FileService.get_file_by_id(file_id)
    if file is None:
        return (
            jsonify({"error": "File with this id was not found"}),
            HTTPStatus.NOT_FOUND,
        )
    return jsonify(file.to_dict()), HTTPStatus.OK


@storage.route("/files/<string:file_id>", methods=["DELETE"])
def delete_file(file_id):
    file = FileService.get_file_by_id(file_id)
    if file is None:
        return (
            jsonify({"error": "File with this id was not found"}),
            HTTPStatus.NOT_FOUND,
        )
    try:
        FileService.delete_file(file)
    except OSError as e:
        return (
            jsonify({"error": "Error deleting file in file storage"}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
    except Exception as e:
        return (
            jsonify({"error": "Error deleting file in DB"}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
    return jsonify(file.to_dict()), HTTPStatus.OK


@storage.route("/files", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No part file"}), HTTPStatus.BAD_REQUEST

    uploaded_file = request.files["file"]
    data = json.loads(request.form["json"])

    try:
        new_file = FileService.upload_file(uploaded_file, data)
    except FileExistsError as e:
        return jsonify({"error": "File already exists"}), HTTPStatus.CONFLICT
    except OSError as e:
        return jsonify({"error": "File saving error"}), HTTPStatus.BAD_REQUEST
    except Exception as e:
        return (
            jsonify({"error": "Error writing file information to the DB"}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
    return jsonify(new_file.to_dict()), HTTPStatus.CREATED


@storage.route("/files/<string:file_id>/download", methods=["GET"])
def download_file(file_id):
    file = FileService.get_file_by_id(file_id)
    if file is None:
        return (
            jsonify({"error": "File with this id was not found"}),
            HTTPStatus.NOT_FOUND,
        )
    return send_file(FileService.get_filepath(file), as_attachment=True)


@storage.route("/files/sync", methods=["POST"])
def sync_storage():
    try:
        files_to_add, files_to_delete = FileService.sync_storage()
    except Exception as e:
        return (
            jsonify({"error": "Error adding ot deleting file in DB"}),
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
    file = FileService.get_file_by_id(file_id)
    if file is None:
        return (
            jsonify({"error": "File with this id was not found"}),
            HTTPStatus.NOT_FOUND,
        )
    new_data = request.get_json()
    try:
        file = FileService.update_file(file, new_data)
    except FileExistsError as e:
        return (
            jsonify({"error": "File with same name already exist"}),
            HTTPStatus.CONFLICT,
        )
    except Exception as e:
        return (
            jsonify({"error": "Error updating file data in DB"}),
            HTTPStatus.CONFLICT,
        )
    return jsonify(file.to_dict()), HTTPStatus.OK
