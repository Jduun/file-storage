from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.config import config
from src.models import Base

pg_engine = create_engine(
    f"postgresql+psycopg2://{config.postgres.user}:"
    f"{config.postgres.password}@"
    f"{config.postgres.host}/"
    f"{config.postgres.db}",
    echo=config.debug,
)
pg_session_maker = sessionmaker(bind=pg_engine, expire_on_commit=False)


def get_pg_session() -> Session:
    return pg_session_maker()


def setup_pg():
    Base.metadata.create_all(pg_engine)
