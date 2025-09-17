from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from db import SessionLocal
from services.auth_service import create_access_token, verify_password, hash_password
from models.models_users import User, UserCreate, UserPublic

router = APIRouter()

async def get_session():
    async with SessionLocal() as s:
        yield s

@router.post("/signup", response_model=UserPublic, status_code=201)
async def signup(payload: UserCreate, session: AsyncSession = Depends(get_session)):
    # ¿Existe email?
    rs = await session.execute(select(User).where(User.email == payload.email))
    if rs.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Crear usuario con pass hash
    u = User(name=payload.name, email=payload.email, pass_hash=hash_password(payload.password))
    session.add(u)
    await session.commit()
    await session.refresh(u)
    return UserPublic.model_validate(u)

@router.post("/login")
async def login(email: str, password: str, session: AsyncSession = Depends(get_session)):
    rs = await session.execute(select(User).where(User.email == email))
    u = rs.scalars().first()
    if not u or not verify_password(password, u.pass_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(sub=u.email, expires_minutes=120)
    return {"access_token": token, "token_type": "bearer"}
