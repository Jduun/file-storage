import json
from flask import Blueprint, jsonify, request, send_file
from http import HTTPStatus
from db.postgres import models, connection
import uuid
from datetime import datetime
import os
from sqlalchemy import func


storage = Blueprint('storage', __name__)
root_folder = os.getenv("ROOT_FOLDER")


@storage.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@storage.route("/files", methods=['GET'])
def get_files():
    files = models.File.query.all()
    return jsonify([file.to_dict() for file in files]), HTTPStatus.OK


@storage.route("/files/<string:file_id>", methods=['GET'])
def get_file(file_id):
    file = models.File.query.get(file_id)
    if file is None:
        return jsonify({"error": "File not found"}), HTTPStatus.NOT_FOUND
    return jsonify({"file info": file.to_dict()}), HTTPStatus.OK


@storage.route("/files/<string:file_id>", methods=['DELETE'])
def delete_file(file_id):
    file = models.File.query.get(file_id)
    if file is None:
        return "", HTTPStatus.NOT_FOUND
    try:
        connection.db.session.delete(file)
        connection.db.session.commit()
    except Exception as e:
        connection.db.session.rollback()
        return "", HTTPStatus.INTERNAL_SERVER_ERROR
    filepath = root_folder + file.filepath + file.filename + file.extension
    os.remove(filepath)
    return "", HTTPStatus.NO_CONTENT


@storage.route("/files", methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No part file"}), HTTPStatus.BAD_REQUEST

    uploaded_file = request.files['file']
    data = json.loads(request.form['json'])
    full_filename = uploaded_file.filename
    if not data['filepath'].endswith("/"):
        data['filepath'] += "/"
    path_to_folder = root_folder + data['filepath']
    full_filepath = path_to_folder + full_filename

    os.makedirs(path_to_folder, exist_ok=True)
    # if not os.path.exists(path_to_folder):
    #   return jsonify({"error": "Folder doesn't exists"}), HTTPStatus.CONFLICT
    if os.path.isfile(full_filepath):
        return jsonify({"error": "File already exists"}), HTTPStatus.CONFLICT

    size = len(uploaded_file.read())
    uploaded_file.seek(0)

    filename, extension = os.path.splitext(full_filename)
    created_at = datetime.utcnow().isoformat()

    try:
        new_file = models.File(id=str(uuid.uuid4()),
                               filename=filename,
                               extension=extension,
                               size=size,
                               filepath=data["filepath"],
                               created_at=created_at,
                               modified_at=None,
                               comment=data["comment"])
        connection.db.session.add(new_file)
        connection.db.session.commit()
    except Exception as e:
        connection.db.session.rollback()
        return jsonify({"error": "Error writing file information to the DB"}), HTTPStatus.INTERNAL_SERVER_ERROR

    try:
        uploaded_file.save(full_filepath)
    except Exception as e:
        return jsonify({"error": "File saving error"}), HTTPStatus.BAD_REQUEST

    return jsonify(new_file.to_dict()), HTTPStatus.CREATED


@storage.route("/files/download/<string:file_id>", methods=['GET'])
def download_file(file_id):
    file = models.File.query.get(file_id)
    if file is None:
        return "", HTTPStatus.NOT_FOUND
    filepath = root_folder + file.filepath + file.filename + file.extension
    return send_file(filepath, as_attachment=True)


@storage.route("/files/search", methods=['GET'])
def search_files():
    path = request.args.get("path", "/")
    if not path.endswith("/"):
        path += "/"
    search_pattern = f"{path}%"
    files = models.File.query.filter(models.File.filepath.like(search_pattern)).all()
    return jsonify([file.to_dict() for file in files]), HTTPStatus.OK


@storage.route("/files/<string:file_id>/filename", methods=['PATCH'])
def update_filename(file_id):
    new_filename = request.args.get("filename")
    if new_filename is None:
        return jsonify({'error': 'Parameter not provided'}), HTTPStatus.BAD_REQUEST

    file = models.File.query.get(file_id)
    if file is None:
        return "", HTTPStatus.NOT_FOUND

    filepath = root_folder + file.filepath + file.filename + file.extension
    new_filepath = root_folder + file.filepath + new_filename + file.extension

    if os.path.exists(new_filepath):
        if os.path.isfile(new_filepath):
            return jsonify({"error": "File with same name already exists"}), HTTPStatus.CONFLICT

    file.filename = new_filename
    file.modified_at = datetime.utcnow()
    connection.db.session.commit()
    os.rename(filepath, new_filepath)

    return jsonify(file.to_dict()), HTTPStatus.OK


@storage.route("/files/<string:file_id>/filepath", methods=['PATCH'])
def update_filepath(file_id):
    new_filepath = request.args.get("filepath")
    if new_filepath is None:
        return jsonify({'error': 'Parameter not provided'}), HTTPStatus.BAD_REQUEST

    if not new_filepath.endswith("/"):
        new_filepath += "/"

    file = models.File.query.get(file_id)
    if file is None:
        return "", HTTPStatus.NOT_FOUND

    # Does the new path to folder exist?
    old_path_to_folder = root_folder + file.filepath
    new_path_to_folder = root_folder + new_filepath

    os.makedirs(new_path_to_folder, exist_ok=True)
    # if not os.path.exists(new_path_to_folder):
    #    return jsonify({"error": "Folder doesn't exists"}), HTTPStatus.CONFLICT

    # Does the file with the same name exist in folder?
    old_full_filepath = old_path_to_folder + file.filename + file.extension
    new_full_filepath = new_path_to_folder + file.filename + file.extension

    if os.path.exists(new_full_filepath):
        return jsonify({"error": "File with same name already exists"}), HTTPStatus.CONFLICT

    os.replace(old_full_filepath, new_full_filepath)
    file.filepath = new_filepath
    file.modified_at = datetime.utcnow()
    connection.db.session.commit()

    return jsonify(file.to_dict()), HTTPStatus.OK


@storage.route("/files/<string:file_id>/comment", methods=['PATCH'])
def update_file_comment(file_id):
    new_comment = request.args.get("comment")
    if new_comment is None:
        return jsonify({'error': 'Parameter not provided'}), HTTPStatus.BAD_REQUEST

    file = models.File.query.get(file_id)
    if file is None:
        return "", HTTPStatus.NOT_FOUND

    file.comment = new_comment
    file.modified_at = datetime.utcnow()
    connection.db.session.commit()
    return jsonify(file.to_dict()), HTTPStatus.OK


@storage.route("/files/sync", methods=['POST'])
def sync_storage():
    storage_files = []
    for path, subdirs, files in os.walk(root_folder):
        for name in files:
            filename, ext = os.path.splitext(name)
            storage_files.append(path.removeprefix(root_folder) + "/" + filename + ext)

    db_files = [file.filepath + file.filename + file.extension for file in models.File.query.all()]

    db_set = set(db_files)
    storage_set = set(storage_files)

    files_to_delete = db_set - storage_set
    files_to_add = storage_set - db_set

    for file_to_delete in files_to_delete:
        file = models.File.query.filter(func.concat(models.File.filepath, models.File.filename, models.File.extension)
                                        == file_to_delete).first()
        connection.db.session.delete(file)
        connection.db.session.commit()

    for file_to_add in files_to_add:
        filepath = os.path.dirname(file_to_add)
        filepath += ("/" if filepath != "/" else "")
        filename = os.path.basename(file_to_add)
        filename, ext = os.path.splitext(filename)
        size = os.path.getsize(root_folder + file_to_add)
        created_at = datetime.fromtimestamp(os.path.getctime(root_folder + file_to_add))

        new_file = models.File(id=str(uuid.uuid4()),
                               filename=filename,
                               extension=ext,
                               size=size,
                               filepath=filepath,
                               created_at=created_at,
                               modified_at=None,
                               comment="")
        connection.db.session.add(new_file)
        connection.db.session.commit()

    return {"files_to_add": list(files_to_add), "files_to_delete": list(files_to_delete)}, HTTPStatus.OK
