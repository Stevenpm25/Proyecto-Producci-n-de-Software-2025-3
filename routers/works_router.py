from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from db import SessionLocal
from models.models_works import WorkCreate, WorkPublic
from operations.operations_works import read_all_works, create_work
from services.security import require_admin
from utils.pagination import get_pagination
from sqlmodel import select
from models.models_works import Work
router = APIRouter()

async def get_session():
    async with SessionLocal() as s:
        yield s

@router.get("/", response_model=List[WorkPublic])
async def list_works(limit: int = 50, offset: int = 0, session: AsyncSession = Depends(get_session)):
    limit, offset = get_pagination(limit, offset)
    rs = await session.execute(select(Work).limit(limit).offset(offset))
    return [WorkPublic.model_validate(w) for w in rs.scalars().all()]


@router.post("/", response_model=WorkPublic, status_code=201, dependencies=[Depends(require_admin)])
async def add_work(
    payload: WorkCreate,
    session: AsyncSession = Depends(get_session),
    cover: Optional[UploadFile] = File(default=None)
):
    return await create_work(session, payload, cover)
