"""Утилиты хеширования паролей и работы с JWT-токенами."""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Возвращает bcrypt-хеш пароля."""
    return PWD_CONTEXT.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет, соответствует ли пароль хешу."""
    return PWD_CONTEXT.verify(plain_password, hashed_password)


def create_access_token(login: str) -> str:
    """Создаёт JWT с ограниченным сроком действия."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode = {"sub": login, "exp": expire}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> str | None:
    """Возвращает login из токена или None, если токен недействителен."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        login: str | None = payload.get("sub")
        return login
    except JWTError:
        return None
