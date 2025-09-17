import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from db import SessionLocal
from models.models_loans import Loan, QueueItem

async def _promote_queue(session: AsyncSession, work_id: int):
    rs = await session.execute(
        select(QueueItem).where(QueueItem.work_id == work_id).order_by(QueueItem.priority.asc(), QueueItem.created_at.asc())
    )
    nxt = rs.scalars().first()
    if nxt:
        new_loan = Loan(user_id=nxt.user_id, work_id=nxt.work_id, status="active")
        session.add(new_loan)
        await session.delete(nxt)
        await session.commit()

async def expire_overdue_loans_once():
    async with SessionLocal() as session:
        now_str = datetime.utcnow().strftime("%Y-%m-%d")
        rs = await session.execute(select(Loan).where(Loan.status=="active", Loan.end != None, Loan.end < now_str))
        overdue = rs.scalars().all()
        for l in overdue:
            l.status = "expired"
            session.add(l)
            await session.commit()
            await _promote_queue(session, l.work_id)

async def scheduler_loop(interval_seconds: int = 60):
    while True:
        try:
            await expire_overdue_loans_once()
        except Exception:
            pass
        await asyncio.sleep(interval_seconds)

def start_scheduler():
    return asyncio.create_task(scheduler_loop(60))

def stop_scheduler(task):
    if task:
        task.cancel()
