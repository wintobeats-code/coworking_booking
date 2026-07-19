"""Зависимости FastAPI для аутентификации и авторизации."""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.models import User
from app.db.session import get_db

OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(OAUTH2_SCHEME),
    db: Session = Depends(get_db),
) -> User:
    """Извлекает текущего пользователя из JWT-токена."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Недействительный или просроченный токен",
        headers={"WWW-Authenticate": "Bearer"},
    )
    login = decode_access_token(token)
    if login is None:
        raise credentials_exception
    user = db.query(User).filter(User.login == login).first()
    if user is None:
        raise credentials_exception
    return user
