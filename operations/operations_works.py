from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from models.models_works import Work, WorkCreate, WorkPublic
from fastapi import UploadFile
from services.storage_service import upload_image

async def read_all_works(session: AsyncSession) -> List[WorkPublic]:
    rs = await session.execute(select(Work))
    return [WorkPublic.model_validate(w) for w in rs.scalars().all()]

async def create_work(session: AsyncSession, data: WorkCreate, cover: Optional[UploadFile]=None) -> WorkPublic:
    payload = data.model_dump()
    if cover:
        url = await upload_image(cover)
        if url: payload["cover_url"] = url
    w = Work(**payload)
    session.add(w); await session.commit(); await session.refresh(w)
    return WorkPublic.model_validate(w)
