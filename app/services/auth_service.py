from db.postgres import db, Session
from sqlalchemy.exc import SQLAlchemyError
from exceptions import *


def set_session(session_id: str):
    try:
        db.session.add(Session(session_id=session_id))
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise DatabaseAddError


def is_session_exist(session_id: str) -> bool:
    return db.session.get(Session, session_id) is not None
