from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from db import SessionLocal
from jose import JWTError
from services.auth_service import decode_token
from models.models_users import User

bearer = HTTPBearer(auto_error=True)

async def get_session():
    async with SessionLocal() as s:
        yield s

async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    session: AsyncSession = Depends(get_session)
) -> User:
    token = creds.credentials
    data = decode_token(token)
    if not data or "sub" not in data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    q = await session.execute(select(User).where(User.email == data["sub"]))
    u = q.scalars().first()
    if not u:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return u

def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return user
