"""Точка входа FastAPI-приложения."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.api import auth, bookings, rooms
from app.core.seed import seed_initial_data
from app.db.base import Base
from app.db.session import ENGINE


def create_app(include_lifespan: bool = True) -> FastAPI:
    """Создаёт и настраивает экземпляр FastAPI-приложения."""
    lifespan_func = None
    if include_lifespan:

        @asynccontextmanager
        async def lifespan_func(_app: FastAPI):  # pylint: disable=function-redefined
            """Инициализация БД при старте."""
            Base.metadata.create_all(bind=ENGINE)
            seed_initial_data()
            yield

    application = FastAPI(
        title="Коворкинг: Бронирование переговорных",
        description="Сервис для бронирования переговорных комнат",
        version="1.0.0",
        lifespan=lifespan_func,
    )

    @application.get("/", include_in_schema=False)
    def redirect_to_docs():
        """Перенаправляет корневой URL на Swagger-документацию."""
        return RedirectResponse(url="/docs")

    application.include_router(auth.router, prefix="/auth", tags=["auth"])
    application.include_router(rooms.router, prefix="/rooms", tags=["rooms"])
    application.include_router(bookings.router, prefix="/bookings", tags=["bookings"])

    @application.get("/health", tags=["system"])
    def health_check():
        """Проверка работоспособности сервиса."""
        return {"status": "ok"}

    return application


app = create_app()
