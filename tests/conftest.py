"""Конфигурация pytest: движок БД, фикстуры приложения и данных."""

from datetime import time

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.core.security import hash_password
from app.db.base import Base
from app.db.models import Room, Slot, User, UserRole
from app.db.session import get_db
from app.main import create_app

SQLALCHEMY_DATABASE_URL = "sqlite:///file::memory:?cache=shared&uri=true"

ENGINE = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)


@event.listens_for(ENGINE, "connect")
def set_sqlite_pragma(dbapi_connection, _connection_record):
    """Включает foreign keys в SQLite."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TESTING_SESSION_LOCAL = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)

Base.metadata.create_all(bind=ENGINE)

TEST_APP = create_app(include_lifespan=False)


def override_get_db():
    """Подменяет get_db на тестовую сессию."""
    db = TESTING_SESSION_LOCAL()
    try:
        yield db
    finally:
        db.close()


TEST_APP.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def _clean_tables():
    """Очищает все таблицы перед каждым тестом, сохраняя схему."""
    with ENGINE.connect() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
        conn.commit()
    yield


@pytest.fixture
def db_session():
    """Сессия БД для создания тестовых данных и прямых проверок."""
    db = TESTING_SESSION_LOCAL()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def user_employee(db_session) -> User:
    """Создаёт тестового сотрудника."""
    user = User(
        login="employee",
        hashed_password=hash_password("emp123"),
        role=UserRole.EMPLOYEE,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def user_admin(db_session) -> User:
    """Создаёт тестового администратора."""
    user = User(
        login="admin",
        hashed_password=hash_password("admin123"),
        role=UserRole.ADMIN,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def user_employee_2(db_session) -> User:
    """Создаёт второго тестового сотрудника."""
    user = User(
        login="employee2",
        hashed_password=hash_password("emp223"),
        role=UserRole.EMPLOYEE,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_room(db_session) -> Room:
    """Создаёт тестовую комнату «Переговорка А»."""
    room = Room(name="Переговорка А")
    db_session.add(room)
    db_session.commit()
    db_session.refresh(room)
    return room


@pytest.fixture
def sample_slot(db_session, sample_room) -> Slot:
    """Создаёт тестовый слот 09:00–11:00."""
    slot = Slot(
        room_id=sample_room.id,
        start_time=time(9, 0),
        end_time=time(11, 0),
    )
    db_session.add(slot)
    db_session.commit()
    db_session.refresh(slot)
    return slot


@pytest.fixture
def sample_slot_2(db_session, sample_room) -> Slot:
    """Создаёт тестовый слот 11:00–13:00."""
    slot = Slot(
        room_id=sample_room.id,
        start_time=time(11, 0),
        end_time=time(13, 0),
    )
    db_session.add(slot)
    db_session.commit()
    db_session.refresh(slot)
    return slot


@pytest.fixture
def second_room(db_session) -> Room:
    """Создаёт тестовую комнату «Переговорка Б»."""
    room = Room(name="Переговорка Б")
    db_session.add(room)
    db_session.commit()
    db_session.refresh(room)
    return room


@pytest.fixture
def client() -> TestClient:
    """HTTP-клиент для тестов API."""
    return TestClient(TEST_APP, raise_server_exceptions=True)


@pytest.fixture
def employee_token(client, user_employee) -> str:  # pylint: disable=unused-argument
    """JWT-токен сотрудника (зависит от user_employee для создания пользователя)."""
    response = client.post(
        "/auth/login",
        json={"login": "employee", "password": "emp123"},
    )
    return response.json()["access_token"]


@pytest.fixture
def admin_token(client, user_admin) -> str:  # pylint: disable=unused-argument
    """JWT-токен администратора (зависит от user_admin для создания пользователя)."""
    response = client.post(
        "/auth/login",
        json={"login": "admin", "password": "admin123"},
    )
    return response.json()["access_token"]


@pytest.fixture
def employee_2_token(client, user_employee_2) -> str:  # pylint: disable=unused-argument
    """JWT-токен второго сотрудника (зависит от user_employee_2 для создания пользователя)."""
    response = client.post(
        "/auth/login",
        json={"login": "employee2", "password": "emp223"},
    )
    return response.json()["access_token"]
