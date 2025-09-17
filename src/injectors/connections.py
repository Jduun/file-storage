from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from src.config import config

pg_engine = create_engine(
    f"postgresql+psycopg2://{config.postgres.user}:"
    f"{config.postgres.password}@"
    f"{config.postgres.host}/"
    f"{config.postgres.db}",
    echo=config.debug,
)
pg_session_maker = sessionmaker(bind=pg_engine)
Base = declarative_base()


def get_pg_session() -> Session:
    return pg_session_maker()


def setup_pg():
    Base.metadata.create_all(pg_engine)
