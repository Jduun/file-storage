from src.injectors.connections import get_pg_session
from src.services import FileService


def file_service() -> FileService:
    return FileService(pg_connection=get_pg_session())
