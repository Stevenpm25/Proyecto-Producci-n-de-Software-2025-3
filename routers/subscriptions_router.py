from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db import SessionLocal
from models.models_subscriptions import SubscriptionCreate, SubscriptionPublic
from operations.operations_subscriptions import (
    read_user_subscription, create_or_replace_subscription, cancel_subscription, list_subscriptions
)

router = APIRouter()

async def get_session():
    async with SessionLocal() as s:
        yield s

@router.get("/", response_model=List[SubscriptionPublic])
async def list_all(session: AsyncSession = Depends(get_session)):
    return await list_subscriptions(session)

@router.get("/me/{user_id}", response_model=SubscriptionPublic)
async def my_sub(user_id: int, session: AsyncSession = Depends(get_session)):
    sub = await read_user_subscription(session, user_id)
    if not sub: raise HTTPException(404, "No active subscription")
    return sub

@router.post("/", response_model=SubscriptionPublic, status_code=201)
async def create_or_update(payload: SubscriptionCreate, session: AsyncSession = Depends(get_session)):
    return await create_or_replace_subscription(session, payload)

@router.post("/cancel/{user_id}", response_model=SubscriptionPublic)
async def cancel(user_id: int, at_period_end: bool = True, session: AsyncSession = Depends(get_session)):
    sub = await cancel_subscription(session, user_id, at_period_end)
    if not sub: raise HTTPException(404, "No active subscription")
    return sub
