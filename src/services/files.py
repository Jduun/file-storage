import logging
import os
from datetime import datetime
from http import HTTPStatus
from typing import Optional

from sqlalchemy.orm import Session

from src.config import config
from src.exceptions import ModuleException
from src.models import File, FileUploadDTO, FileUpdateDTO, FileDTO
from src.logger import get_logger


class FileService:
    def __init__(self, pg_connection: Session):
        self._pg = pg_connection
        self._logger = get_logger()

    def upload(self, data: FileUploadDTO) -> FileDTO:
        self._logger.info(
            "Загрузка файла",
            extra={"filename": data.filename, "filepath": data.filepath},
        )
        if not self.is_valid_path(data.filepath):
            self._logger.warning(
                f"Некорректный путь",
                extra={"filepath": data.filepath},
            )
            raise ModuleException(
                "Некорректный путь",
                code=HTTPStatus.BAD_REQUEST,
            )

        path_to_folder = config.root_folder + data.filepath
        full_filepath = path_to_folder + data.filename

        self._logger.debug(
            "Пути для сохранения",
            extra={
                "path_to_folder": path_to_folder,
                "full_filepath": full_filepath,
            },
        )

        os.makedirs(path_to_folder, exist_ok=True)
        if os.path.isfile(full_filepath):
            self._logger.warning(
                "Файл уже существует",
                extra={"full_filepath": full_filepath},
            )
            raise ModuleException(
                "Файл уже существует", code=HTTPStatus.BAD_REQUEST
            )

        filename, extension = os.path.splitext(data.filename)
        created_at = datetime.now().isoformat()

        self._logger.debug(
            "Парсинг названия файла",
            extra={"filename": filename, "extension": extension},
        )

        new_file = File(
            filename=filename,
            extension=extension,
            size_bytes=len(data.file_bytes),
            filepath=data.filepath,
            comment=data.comment,
            created_at=created_at,
            updated_at=None,
        )

        with open(full_filepath, "wb") as f:
            f.write(data.file_bytes)
        self._logger.info(
            "Файл сохранен на диск",
            extra={"filename": data.filename, "full_filepath": full_filepath},
        )

        with self._pg.begin():
            self._pg.add(new_file)
        self._logger.info(
            "Файл добавлен в БД",
            extra={"filename": data.filename},
        )

        return FileDTO.model_validate(new_file)

    def get(self, file_id: int) -> FileDTO:
        self._logger.info(
            "Получение файла из БД",
            extra={"file_id": file_id},
        )
        with self._pg.begin():
            file: Optional[File] = self._pg.get(File, file_id)
            if file:
                self._logger.info(
                    "Файл найден",
                    extra={"file_id": file_id, "filename": file.filename},
                )
                return FileDTO.model_validate(file)
        self._logger.warning("Файл не найден", extra={"file_id": file_id})
        raise ModuleException("Файл не найден", code=HTTPStatus.NOT_FOUND)

    def get_all(self) -> list[FileDTO]:
        self._logger.info(f"Получение всех файлов из БД")
        with self._pg.begin():
            files = self._pg.query(File).all()
            self._logger.info(
                "Все файлы из БД получены", extra={"count": len(files)}
            )
            return list(map(FileDTO.model_validate, files))

    def update(self, file_id: int, data: FileUpdateDTO) -> FileDTO:
        self._logger.info(
            "Обновление файла",
            extra={"file_id": file_id, "update_data": data.model_dump()},
        )
        with self._pg.begin():
            file: Optional[File] = self._pg.get(File, file_id)
            self._logger.debug(
                "Результат выборки",
                extra={"file_id": file_id, "exists": file is not None},
            )

            if not file:
                raise ModuleException(
                    "Файл не найден",
                    code=HTTPStatus.NOT_FOUND,
                )
            self._logger.debug(
                "Текущие данные файла",
                extra=FileDTO.model_validate(file).model_dump(),
            )

        abs_path = self.get_abs_path(file)
        self._logger.debug(
            "Абсолютный путь",
            extra={"abs_path": abs_path},
        )

        file_values = {}

        if data.filename and data.filename != file.filename:
            new_abs_path = (
                config.root_folder
                + file.filepath
                + data.filename
                + file.extension
            )
            if os.path.exists(new_abs_path):
                self._logger.warning(
                    "Файл с таким именем уже существует",
                    extra={"new_abs_path": new_abs_path},
                )
                raise ModuleException(
                    "Файл с таким именем уже существует",
                    code=HTTPStatus.BAD_REQUEST,
                )
            try:
                os.rename(abs_path, new_abs_path)
                self._logger.info(
                    "Файл переименован",
                    extra={"old_path": abs_path, "new_path": new_abs_path},
                )
            except OSError as e:
                self._logger.error(
                    "Ошибка при переименовании файла",
                    exc_info=True,
                )
                raise ModuleException("Ошибка при переименовании файла") from e
            file_values[File.filename] = data.filename
            abs_path = new_abs_path
        else:
            data.filename = file.filename

        if data.filepath and data.filepath != file.filepath:
            if not self.is_valid_path(data.filepath):
                self._logger.warning(
                    "Некорректный путь", extra={"filepath": data.filepath}
                )
                raise ModuleException(
                    "Некорректный путь",
                    code=HTTPStatus.BAD_REQUEST,
                )
            new_path_to_folder = config.root_folder + data.filepath
            os.makedirs(new_path_to_folder, exist_ok=True)

            new_abs_path = new_path_to_folder + data.filename + file.extension
            if os.path.exists(new_abs_path):
                self._logger.warning(
                    "Файл уже существует в этой директории",
                    extra={"new_abs_path": new_abs_path},
                )
                raise ModuleException(
                    "Файл уже существует в этой директории",
                    code=HTTPStatus.BAD_REQUEST,
                )
            try:
                os.replace(abs_path, new_abs_path)
                self._logger.info(
                    "Файл перемещен",
                    extra={"old_path": abs_path, "new_path": new_abs_path},
                )
            except OSError as e:
                self._logger.error(
                    "Ошибка при перемещении файла",
                    exc_info=True,
                )
                raise ModuleException("Ошибка при перемещении файла") from e
            file_values[File.filepath] = data.filepath

        if data.comment and data.comment != file.comment:
            file_values[File.comment] = data.comment

        with self._pg.begin():
            self._logger.debug(
                "Начинается обновление данных в БД",
                extra={"file_id": file_id, "updates": file_values},
            )
            self._pg.query(File).filter(File.id == file_id).update(file_values)
        self._logger.info("Файл обновлен", extra={"file_id": file_id})

        return FileDTO.model_validate(file)

    def delete(self, file_id: int) -> FileDTO:
        self._logger.info("Удаление файла", extra={"file_id": file_id})
        with self._pg.begin():
            file: Optional[File] = self._pg.get(File, file_id)
            if file is None:
                self._logger.warning(
                    "Файл не найден", extra={"file_id": file_id}
                )
                raise ModuleException(
                    "Файл не найден",
                    code=HTTPStatus.BAD_REQUEST,
                )

        try:
            abs_path = self.get_abs_path(file)
            os.remove(abs_path)
            self._logger.info(
                "Файл удален с диска",
                extra={"file_id": file_id, "abs_path": abs_path},
            )
        except OSError as e:
            self._logger.error(
                "Ошибка при удалении файла",
                exc_info=True,
                extra={"file_id": file_id},
            )
            raise ModuleException(f"Ошибка при удалении файла") from e

        with self._pg.begin():
            self._pg.delete(file)

        self._logger.info("Файл удален из БД", extra={"file_id": file_id})
        return FileDTO.model_validate(file)

    @staticmethod
    def get_abs_path(file: FileDTO) -> str:
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
