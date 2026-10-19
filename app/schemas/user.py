from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    password_confirm: str
    # Empresa (opcional): si tiene, el PDF usa la empresa como marca
    # y el nombre del dueño/representante en la firma
    has_company: bool = False
    company_name: Optional[str] = None
    owner_name: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    created_at: str
    has_company: bool = False
    company_name: Optional[str] = None
    owner_name: Optional[str] = None


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    name: Optional[str] = None
    email: Optional[str] = None
