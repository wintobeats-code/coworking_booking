"""Настройки приложения."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки, загружаемые из переменных окружения или .env."""

    SECRET_KEY: str = "super-secret-key-change-in-prod"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DATABASE_URL: str = "postgresql://coworking:coworking123@localhost:5432/coworking"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
