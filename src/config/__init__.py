from pydantic import Field
from pydantic_settings import BaseSettings


class PostgresConfig(BaseSettings):
    user: str = Field(default="postgres")
    password: str = Field(default="postgres")
    host: str = Field(default="localhost")
    db: str = Field(default="db")
    folder: str = Field(default="/postgres_data")
    port: int = Field(default=5432)


class AppConfig(BaseSettings):
    root_folder: str = Field(default="/root_folder")
    postgres: PostgresConfig = Field(default_factory=PostgresConfig)
    app_port: int = Field(default=5000)
    debug: bool = Field(default=False)

    class Config:
        env_nested_delimiter = "_"


config = AppConfig()
