import os
from db.postgres import connection as conn
from db.postgres.models import File
from datetime import datetime
import uuid
from sqlalchemy import func


class FileService:
    ROOT_FOLDER = os.getenv("ROOT_FOLDER")

    @staticmethod
    def get_file_by_id(file_id):
        file = File.query.get(file_id)
        return file

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
            conn.db.session.delete(file)
            conn.db.session.commit()
        except Exception as e:
            conn.db.session.rollback()
            raise e
        try:
            os.remove(FileService.get_filepath(file))
        except OSError as e:
            raise e

    @staticmethod
    def update_file(file, new_data):
        if "filepath" in new_data:
            new_filepath = new_data["filepath"]
            if not new_filepath.endswith("/"):
                new_filepath += "/"
            # Does the new path to folder exist?
            old_path_to_folder = FileService.ROOT_FOLDER + file.filepath
            new_path_to_folder = FileService.ROOT_FOLDER + new_filepath

            os.makedirs(new_path_to_folder, exist_ok=True)

            # Does the file with the same name exist in folder?
            old_full_filepath = old_path_to_folder + file.filename + file.extension
            new_full_filepath = new_path_to_folder + file.filename + file.extension

            # ERROR HERE
            if os.path.exists(new_filepath):
                if os.path.isfile(new_filepath):
                    raise FileExistsError()
            try:
                file.filepath = new_filepath
                file.modified_at = datetime.utcnow()
                conn.db.session.commit()
            except Exception as e:
                conn.db.session.rollback()
                raise e
            try:
                os.replace(old_full_filepath, new_full_filepath)
            except OSError as e:
                raise e
        if "filename" in new_data:
            new_filename = new_data["filename"]
            filepath = FileService.get_filepath(file)
            new_filepath = (
                FileService.ROOT_FOLDER + file.filepath + new_filename + file.extension
            )
            if os.path.isfile(new_filepath) and new_filename != file.filename:
                raise FileExistsError()
            try:
                file.filename = new_filename
                file.modified_at = datetime.utcnow()
                conn.db.session.commit()
            except Exception as e:
                conn.db.session.rollback()
                raise e
            try:
                os.rename(filepath, new_filepath)
            except OSError as e:
                raise e
        if "comment" in new_data:
            new_comment = new_data["comment"]
            try:
                file.comment = new_comment
                file.modified_at = datetime.utcnow()
                conn.db.session.commit()
            except Exception as e:
                conn.db.session.rollback()
                raise e
        return file

    @staticmethod
    def upload_file(uploaded_file, data):
        full_filename = uploaded_file.filename
        if not data["filepath"].endswith("/"):
            data["filepath"] += "/"
        path_to_folder = FileService.ROOT_FOLDER + data["filepath"]
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
            conn.db.session.add(new_file)
            conn.db.session.commit()
        except Exception as e:
            conn.db.session.rollback()
            raise e
        try:
            uploaded_file.save(full_filepath)
        except OSError as e:
            raise e

        return new_file

    @staticmethod
    def get_filepath(file):
        return FileService.ROOT_FOLDER + file.filepath + file.filename + file.extension

    @staticmethod
    def sync_storage():
        storage_files = []
        for path, subdirs, files in os.walk(FileService.ROOT_FOLDER):
            for name in files:
                filename, ext = os.path.splitext(name)
                storage_files.append(
                    path.removeprefix(FileService.ROOT_FOLDER) + "/" + filename + ext
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
                conn.db.session.delete(file)
                conn.db.session.commit()
            except Exception as e:
                conn.db.session.rollback()
                raise e

        for file_to_add in files_to_add:
            filepath = os.path.dirname(file_to_add)
            filepath += "/" if filepath != "/" else ""
            filename = os.path.basename(file_to_add)
            filename, ext = os.path.splitext(filename)
            size = os.path.getsize(FileService.ROOT_FOLDER + file_to_add)
            created_at = datetime.fromtimestamp(
                os.path.getctime(FileService.ROOT_FOLDER + file_to_add)
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
                conn.db.session.add(new_file)
                conn.db.session.commit()
            except Exception as e:
                conn.db.session.rollback()
                raise e

        return files_to_add, files_to_delete
