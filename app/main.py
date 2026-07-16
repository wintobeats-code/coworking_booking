from fastapi import FastAPI

from app.db.base import Base
from app.db.session import engine
from app.db import models  # noqa: F401 — регистрация моделей в Base
from app.core.seed import seed_initial_data
from app.api import auth, rooms, bookings

app = FastAPI(
    title="Коворкинг: Бронирование переговорных",
    description="Сервис для бронирования переговорных комнат",
    version="1.0.0",
)

# Подключаем роутеры
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(rooms.router, prefix="/rooms", tags=["rooms"])
app.include_router(bookings.router, prefix="/bookings", tags=["bookings"])


@app.on_event("startup")
def on_startup() -> None:
    """Создаёт таблицы и заполняет БД начальными данными."""
    Base.metadata.create_all(bind=engine)
    seed_initial_data()


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok"}
