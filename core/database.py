from sqlmodel import create_engine, SQLModel, Session
from .models import *

DATABASE_URL = "sqlite:///db.sqlite3"
engine = create_engine(DATABASE_URL, echo=True)

def initialize_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    session = Session(engine)
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()