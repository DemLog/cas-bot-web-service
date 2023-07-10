from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import DBSettings

engine = create_engine(
    DBSettings.SQLALCHEMY_DATABASE_URL, pool_size=10,
    max_overflow=2,
    pool_recycle=300,
    pool_pre_ping=True,
    pool_use_lifo=True
)
print(DBSettings.SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


@contextmanager
def session_scope() -> SessionLocal:
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
