import os
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator, Field, ConfigDict


class FileUpdateDTO(BaseModel):
    filename: Optional[str] = Field(default=None)
    filepath: Optional[str] = Field(default=None)
    comment: Optional[str] = Field(default=None)

    @field_validator("filepath")
    @classmethod
    def ensure_trailing_slash(cls, v: str) -> str:
        v = v.strip()
        if not v:
            v = "/"
        v = os.path.normpath(v).replace("\\", "/")
        if not v.endswith("/"):
            v += "/"
        if not v.startswith("/"):
            v = "/" + v
        return v

    @field_validator("comment")
    @classmethod
    def validate_comment(cls, v: str) -> str:
        return v.strip()


class FileDTO(FileUpdateDTO):
    id: int = Field()
    extension: str = Field()
    size_bytes: int = Field()
    created_at: datetime = Field()
    updated_at: datetime = Field()

    model_config = ConfigDict(from_attributes=True)


class FileUploadDTO(FileUpdateDTO):
    file_bytes: bytes = Field()
