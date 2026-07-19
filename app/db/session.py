"""Подключение к базе данных и сессия SQLAlchemy."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

ENGINE = create_engine(settings.DATABASE_URL)
SESSION_LOCAL = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)


def get_db():
    """Генератор сессии БД для FastAPI Depends."""
    db = SESSION_LOCAL()
    try:
        yield db
    finally:
        db.close()
