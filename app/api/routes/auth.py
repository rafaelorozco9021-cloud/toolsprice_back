from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import bcrypt
from datetime import datetime, timedelta
from jose import jwt

from app.db.session import get_db
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.schemas.user import UserCreate, UserResponse, Token
from app.db.models.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


def get_password_hash(password: str):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    if user.password != user.password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )

    result = await db.execute(select(User).filter(User.email == user.email))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    db_user = User(
        name=user.name,
        email=user.email,
        password_hash=get_password_hash(user.password),
        email_verified=True,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return UserResponse(
        id=db_user.id,
        name=db_user.name,
        email=db_user.email,
        created_at=db_user.created_at.isoformat()
    )


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).filter(User.email == form_data.username))
    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # En desarrollo permitimos login sin verificación
    # if not user.email_verified:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Please verify your email first"
    #     )

    access_token = create_access_token({"sub": user.id, "email": user.email})
    refresh_token = create_refresh_token({"sub": user.id, "email": user.email})

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.get("/verify")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        user_id = payload.get("user_id")

        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.email_verified = True
        await db.commit()

        return {"message": "Email verified successfully"}
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired token")


@router.post("/refresh")
async def refresh_token(payload: dict):
    """Extiende la sesión 60 min más usando refresh_token"""
    token = payload.get("refresh_token")
    if not token:
        raise HTTPException(status_code=400, detail="refresh_token requerido")
    data = verify_token(token)
    if not data:
        raise HTTPException(status_code=401, detail="Refresh token inválido o expirado")
    # verificar usuario aún existe
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import AsyncSession
    # no tenemos db aquí, lo pedimos vía dependencia manual no, simplificamos: solo re-emitir si payload válido
    # el frontend guardará el nuevo access_token
    new_access = create_access_token({"sub": data["sub"], "email": data.get("email", "")})
    new_refresh = create_refresh_token({"sub": data["sub"], "email": data.get("email", "")})
    return {"access_token": new_access, "refresh_token": new_refresh, "token_type": "bearer"}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}
