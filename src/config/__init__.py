import os

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings


class PostgresConfig(BaseSettings):
    user: str = Field(default="postgres")
    password: str = Field(default="postgres")
    host: str = Field(default="file-storage-db")
    db: str = Field(default="db")


class AppConfig(BaseSettings):
    root_folder: str = Field(default="/root_folder")
    postgres: PostgresConfig = Field(default_factory=PostgresConfig)
    debug: bool = Field(default=False)


def load_config(path: str) -> AppConfig:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return AppConfig(**data)


config = load_config(os.getenv("YAML_PATH"))
