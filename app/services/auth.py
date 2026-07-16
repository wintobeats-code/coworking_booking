from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import User
from app.core.security import verify_password, create_access_token


def authenticate_user(db: Session, login: str, password: str) -> str:
    """Проверяет логин/пароль и возвращает JWT-токен."""
    user = db.query(User).filter(User.login == login).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
        )
    return create_access_token(user.login)
