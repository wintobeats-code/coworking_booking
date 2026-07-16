from pydantic import BaseModel, Field


class UserLogin(BaseModel):
    login: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=4, max_length=100)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    login: str
    role: str

    model_config = {"from_attributes": True}