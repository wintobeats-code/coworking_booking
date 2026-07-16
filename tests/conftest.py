import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.security import hash_password
from app.db.base import Base
from app.db.models import Room, Slot, User, UserRole
from app.db.session import get_db
from app.main import app

# ---------- Фикстуры БД ----------

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def prepare_db():
    """Создаёт таблицы перед каждым тестом и дропает после."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# ---------- Фикстуры данных ----------


@pytest.fixture
def db_session():
    """Сессия БД для прямых проверок в тестах."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def user_employee(db_session) -> User:
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
def sample_room(db_session) -> Room:
    room = Room(name="Переговорка А")
    db_session.add(room)
    db_session.commit()
    db_session.refresh(room)
    return room


@pytest.fixture
def sample_slot(db_session, sample_room) -> Slot:
    from datetime import time

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
    from datetime import time

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
    room = Room(name="Переговорка Б")
    db_session.add(room)
    db_session.commit()
    db_session.refresh(room)
    return room


# ---------- Клиент и авторизация ----------


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def employee_token(client, user_employee) -> str:
    response = client.post(
        "/auth/login",
        json={"login": "employee", "password": "emp123"},
    )
    return response.json()["access_token"]


@pytest.fixture
def admin_token(client, user_admin) -> str:
    response = client.post(
        "/auth/login",
        json={"login": "admin", "password": "admin123"},
    )
    return response.json()["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
