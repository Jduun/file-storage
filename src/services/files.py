import os
from datetime import datetime
from http import HTTPStatus

from sqlalchemy.orm import Session

from src.config import config
from src.dtos import FileUploadDTO, FileUpdateDTO, FileDTO
from src.exceptions import ModuleException
from src.models import File


class FileService:
    def __init__(self, pg_connection: Session):
        self._pg = pg_connection

    def upload(self, data: FileUploadDTO) -> FileDTO:
        if not self.is_valid_path(data.filepath):
            raise ModuleException(
                "Invalid path error",
                code=HTTPStatus.BAD_REQUEST,
            )

        path_to_folder = config.root_folder + data.filepath
        full_filepath = path_to_folder + data.filename

        os.makedirs(path_to_folder, exist_ok=True)
        if os.path.isfile(full_filepath):
            raise ModuleException(
                "File already exist", code=HTTPStatus.BAD_REQUEST
            )

        filename, extension = os.path.splitext(data.filename)
        created_at = datetime.now().isoformat()

        new_file = File(
            filename=filename,
            extension=extension,
            size_bytes=len(data.file_bytes),
            filepath=data.filepath,
            comment=data.comment,
            created_at=created_at,
            updated_at=None,
        )

        with self._pg.begin():
            self._pg.add(new_file)
            with open(full_filepath, "wb") as f:
                f.write(data.file_bytes)

        return FileDTO.model_validate(new_file)

    def get(self, file_id: int) -> FileDTO:
        with self._pg.begin():
            file = self._pg.get(File, file_id)
            if file:
                return FileDTO.model_validate(file)
        raise ModuleException("File not found", code=HTTPStatus.NOT_FOUND)

    def get_all(self) -> list[FileDTO]:
        with self._pg.begin():
            files = self._pg.query(File).all()
            return list(map(FileDTO.model_validate, files))

    def update(self, file_id: int, data: FileUpdateDTO) -> FileDTO:
        with self._pg.begin():
            file = self._pg.get(File, file_id)
            if not file:
                raise ModuleException(
                    "File not found",
                    code=HTTPStatus.NOT_FOUND,
                )
            abs_path = self.get_abs_path(file)

            if data.filename and data.filename != file.filename:
                new_abs_path = (
                    config.root_folder
                    + file.filepath
                    + data.filename
                    + file.extension
                )
                if os.path.exists(new_abs_path):
                    raise ModuleException(
                        "File with new name already exists",
                        code=HTTPStatus.BAD_REQUEST,
                    )
                try:
                    os.rename(abs_path, new_abs_path)
                except OSError as e:
                    raise ModuleException(
                        f"File rename error: {e}",
                        code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    )
                file.filename = data.filename
                abs_path = new_abs_path

            if data.filepath and data.filepath != file.filepath:
                if not self.is_valid_path(data.filepath):
                    raise ModuleException(
                        "Invalid path error",
                        code=HTTPStatus.BAD_REQUEST,
                    )
                new_path_to_folder = config.root_folder + data.filepath
                os.makedirs(new_path_to_folder, exist_ok=True)
                new_abs_path = (
                    new_path_to_folder + file.filename + file.extension
                )
                if os.path.exists(new_abs_path):
                    raise ModuleException(
                        "File already exists in target path",
                        code=HTTPStatus.BAD_REQUEST,
                    )
                try:
                    os.replace(abs_path, new_abs_path)
                except OSError as e:
                    raise ModuleException(
                        f"File move error: {e}",
                        code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    )
                file.filepath = data.filepath

            if data.comment and data.comment != file.comment:
                file.comment = data.comment

            return FileDTO.model_validate(file)

    def delete(self, file_id: int) -> FileDTO:
        with self._pg.begin():
            file = self._pg.get(File, file_id)
            if file is None:
                raise ModuleException(
                    "File not found",
                    code=HTTPStatus.BAD_REQUEST,
                )
            try:
                os.remove(self.get_abs_path(file))
            except OSError:
                raise ModuleException(
                    f"Failed to delete file",
                    code=HTTPStatus.INTERNAL_SERVER_ERROR,
                )
            self._pg.delete(file)
            return FileDTO.model_validate(file)

    @staticmethod
    def get_abs_path(file: File) -> str:
        return (
            config.root_folder + file.filepath + file.filename + file.extension
        )

    @staticmethod
    def is_valid_path(path: str) -> bool:
        items = path.split("/")
        for item in items:
            if set(item) == set(".") or item == "~":
                return False
        return True
