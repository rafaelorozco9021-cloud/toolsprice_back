from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    password_confirm: str


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    created_at: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    name: Optional[str] = None
    email: Optional[str] = None
