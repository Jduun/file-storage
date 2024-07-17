import os
from db.postgres import db
from db.postgres import File
from datetime import datetime
import uuid
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from exceptions import *


class FileStorageService:
    ROOT_FOLDER = os.getenv("ROOT_FOLDER")

    @staticmethod
    def get_file_by_id(file_id):
        return db.session.get(File, file_id)

    @staticmethod
    def get_files_in_folder(path_to_folder="/"):
        if not path_to_folder.endswith("/"):
            path_to_folder += "/"
        search_pattern = f"{path_to_folder}%"
        files = File.query.filter(File.filepath.like(search_pattern)).all()
        return files

    @staticmethod
    def delete_file(file):
        try:
            db.session.delete(file)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            raise DatabaseDeleteError
        try:
            os.remove(FileStorageService.get_abs_path(file))
        except OSError:
            raise FileDeleteError

    @staticmethod
    def update_file(file, new_data):
        if "filepath" in new_data:
            new_filepath = new_data["filepath"]
            if not new_filepath.endswith("/"):
                new_filepath += "/"

            old_path_to_folder = FileStorageService.ROOT_FOLDER + file.filepath
            new_path_to_folder = FileStorageService.ROOT_FOLDER + new_filepath

            os.makedirs(new_path_to_folder, exist_ok=True)

            old_full_filepath = old_path_to_folder + file.filename + file.extension
            new_full_filepath = new_path_to_folder + file.filename + file.extension

            if os.path.exists(new_filepath):
                if os.path.isfile(new_filepath):
                    raise FileExistsError()
            try:
                file.filepath = new_filepath
                file.modified_at = datetime.utcnow()
                db.session.commit()
            except SQLAlchemyError:
                db.session.rollback()
                raise DatabaseUpdateError
            try:
                os.replace(old_full_filepath, new_full_filepath)
            except OSError:
                raise FileMoveError
        if "filename" in new_data:
            new_filename = new_data["filename"]
            filepath = FileStorageService.get_abs_path(file)
            new_filepath = (
                FileStorageService.ROOT_FOLDER
                + file.filepath
                + new_filename
                + file.extension
            )
            if os.path.isfile(new_filepath) and new_filename != file.filename:
                raise FileExistsError
            try:
                file.filename = new_filename
                file.modified_at = datetime.utcnow()
                db.session.commit()
            except SQLAlchemyError:
                db.session.rollback()
                raise DatabaseUpdateError
            try:
                os.rename(filepath, new_filepath)
            except OSError:
                raise FileRenameError
        if "comment" in new_data:
            new_comment = new_data["comment"]
            try:
                file.comment = new_comment
                file.modified_at = datetime.utcnow()
                db.session.commit()
            except SQLAlchemyError:
                db.session.rollback()
                raise DatabaseUpdateError
        return file

    @staticmethod
    def upload_file(uploaded_file, data):
        full_filename = uploaded_file.filename
        if "filepath" not in data:
            data["filepath"] = "/"
        if "comment" not in data:
            data["comment"] = ""
        if not data["filepath"].endswith("/"):
            data["filepath"] += "/"

        path_to_folder = FileStorageService.ROOT_FOLDER + data["filepath"]
        full_filepath = path_to_folder + full_filename

        os.makedirs(path_to_folder, exist_ok=True)
        if os.path.isfile(full_filepath):
            raise FileExistsError

        size = len(uploaded_file.read())
        uploaded_file.seek(0)
        filename, extension = os.path.splitext(full_filename)
        created_at = datetime.utcnow().isoformat()

        new_file = File(
            id=str(uuid.uuid4()),
            filename=filename,
            extension=extension,
            size=size,
            filepath=data["filepath"],
            created_at=created_at,
            modified_at=None,
            comment=data["comment"],
        )

        try:
            db.session.add(new_file)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            raise DatabaseAddError
        try:
            uploaded_file.save(full_filepath)
        except OSError:
            raise FileSaveError

        return new_file

    @staticmethod
    def get_abs_path(file):
        return (
            FileStorageService.ROOT_FOLDER
            + file.filepath
            + file.filename
            + file.extension
        )

    @staticmethod
    def get_rel_path(file):
        return file.filepath + file.filename + file.extension

    @staticmethod
    def sync_storage():
        storage_files = []
        for path, subdirs, files in os.walk(FileStorageService.ROOT_FOLDER):
            for name in files:
                filename, ext = os.path.splitext(name)
                storage_files.append(
                    path.removeprefix(FileStorageService.ROOT_FOLDER)
                    + "/"
                    + filename
                    + ext
                )

        db_files = [
            file.filepath + file.filename + file.extension for file in File.query.all()
        ]

        db_set = set(db_files)
        storage_set = set(storage_files)

        files_to_delete = db_set - storage_set
        files_to_add = storage_set - db_set

        for file_to_delete in files_to_delete:
            file = File.query.filter(
                func.concat(
                    File.filepath,
                    File.filename,
                    File.extension,
                )
                == file_to_delete
            ).first()
            try:
                db.session.delete(file)
                db.session.commit()
            except SQLAlchemyError:
                db.session.rollback()
                raise DatabaseDeleteError

        for file_to_add in files_to_add:
            filepath = os.path.dirname(file_to_add)
            filepath += "/" if filepath != "/" else ""
            filename = os.path.basename(file_to_add)
            filename, ext = os.path.splitext(filename)
            size = os.path.getsize(FileStorageService.ROOT_FOLDER + file_to_add)
            created_at = datetime.fromtimestamp(
                os.path.getctime(FileStorageService.ROOT_FOLDER + file_to_add)
            )

            new_file = File(
                id=str(uuid.uuid4()),
                filename=filename,
                extension=ext,
                size=size,
                filepath=filepath,
                created_at=created_at,
                modified_at=None,
                comment="",
            )
            try:
                db.session.add(new_file)
                db.session.commit()
            except SQLAlchemyError:
                db.session.rollback()
                raise DatabaseAddError

        return files_to_add, files_to_delete
