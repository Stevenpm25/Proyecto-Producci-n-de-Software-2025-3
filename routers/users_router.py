from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db import SessionLocal
from operations.operations_users import (
    read_all_users, read_user, create_user, update_user, cancel_user, delete_user
)
from models.models_users import UserCreate, UserUpdate, UserPublic
from services.security import require_admin


router = APIRouter()

async def get_session():
    async with SessionLocal() as s:
        yield s

@router.get("/", response_model=List[UserPublic], dependencies=[Depends(require_admin)])
async def list_users(session: AsyncSession = Depends(get_session)):
    return await read_all_users(session)

@router.get("/{user_id}", response_model=UserPublic, dependencies=[Depends(require_admin)])
async def get_user(user_id: int, session: AsyncSession = Depends(get_session)):
    u = await read_user(session, user_id)
    if not u: raise HTTPException(404, "User not found")
    return u

@router.post("/", response_model=UserPublic, status_code=201, dependencies=[Depends(require_admin)])
async def add_user(payload: UserCreate, session: AsyncSession = Depends(get_session)):
    return await create_user(session, payload)

@router.patch("/{user_id}", response_model=UserPublic, dependencies=[Depends(require_admin)])
async def patch_user(user_id: int, payload: UserUpdate, session: AsyncSession = Depends(get_session)):
    u = await update_user(session, user_id, payload)
    if not u: raise HTTPException(404, "User not found")
    return u

@router.post("/{user_id}/cancel", response_model=UserPublic, dependencies=[Depends(require_admin)])
async def cancel(user_id: int, session: AsyncSession = Depends(get_session)):
    u = await cancel_user(session, user_id)
    if not u: raise HTTPException(404, "User not found")
    return u

@router.delete("/{user_id}", response_model=UserPublic, dependencies=[Depends(require_admin)])
async def remove(user_id: int, session: AsyncSession = Depends(get_session)):
    u = await delete_user(session, user_id)
    if not u: raise HTTPException(404, "User not found")
    return u
