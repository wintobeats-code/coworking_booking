from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserLogin, Token
from app.services import auth as auth_service

router = APIRouter()


@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    token = auth_service.authenticate_user(db, data.login, data.password)
    return {"access_token": token, "token_type": "bearer"}
