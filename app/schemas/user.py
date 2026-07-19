"""Pydantic-схемы для аутентификации и пользователей."""

from pydantic import BaseModel, Field


class UserLogin(BaseModel):
    """Схема входа: логин и пароль."""

    login: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=4, max_length=100)


class Token(BaseModel):
    """JWT-токен ответа при успешном входе."""

    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    """Информация о пользователе для ответов API."""

    id: int
    login: str
    role: str

    model_config = {"from_attributes": True}
