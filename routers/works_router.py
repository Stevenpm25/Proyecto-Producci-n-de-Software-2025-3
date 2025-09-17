from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from db import SessionLocal
from models.models_works import WorkCreate, WorkPublic
from operations.operations_works import read_all_works, create_work

router = APIRouter()

async def get_session():
    async with SessionLocal() as s:
        yield s

@router.get("/", response_model=List[WorkPublic])
async def list_works(session: AsyncSession = Depends(get_session)):
    return await read_all_works(session)

@router.post("/", response_model=WorkPublic, status_code=201)
async def add_work(
    payload: WorkCreate,
    session: AsyncSession = Depends(get_session),
    cover: Optional[UploadFile] = File(default=None)
):
    return await create_work(session, payload, cover)
