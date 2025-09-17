from datetime import datetime

from sqlalchemy import String, func
from sqlalchemy.orm import mapped_column, Mapped

from src.injectors.connections import Base


class File(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(nullable=False)
    extension: Mapped[str] = mapped_column(String(255))
    size_bytes: Mapped[int] = mapped_column(nullable=False)
    filepath: Mapped[str] = mapped_column(nullable=False)
    comment: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.current_timestamp(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
