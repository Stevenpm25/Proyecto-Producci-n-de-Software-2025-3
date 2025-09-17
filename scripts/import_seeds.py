import asyncio, csv, os
from sqlalchemy.ext.asyncio import AsyncSession
from db import SessionLocal, init_db
from models.models_users import User
from services.auth_service import hash_password
from models.models_works import Work
from models.models_subscriptions import Subscription
from models.models_loans import Loan, QueueItem

BASE = "seeds"

async def import_users(session: AsyncSession):
    path = os.path.join(BASE, "users.csv")
    if not os.path.exists(path): return
    with open(path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if await session.get(User, int(row["id"])): continue
            u = User(
                id=int(row["id"]),
                name=row["name"],
                email=row["email"],
                role=row.get("role","free"),
                status=row.get("status","active"),
                pass_hash=hash_password("changeme")
            )
            session.add(u)
    await session.commit()

async def import_works(session: AsyncSession):
    path = os.path.join(BASE, "works.csv")
    if not os.path.exists(path): return
    with open(path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if await session.get(Work, int(row["id"])): continue
            w = Work(
                id=int(row["id"]),
                title=row["title"],
                author=row["author"],
                category=row.get("category") or None,
                cover_url=row.get("cover_url") or None,
                max_slots=int(row.get("max_slots",1)),
                visible=row.get("visible","True") == "True"
            )
            session.add(w)
    await session.commit()

async def import_subscriptions(session: AsyncSession):
    path = os.path.join(BASE, "subscriptions.csv")
    if not os.path.exists(path): return
    with open(path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if await session.get(Subscription, int(row["id"])): continue
            s = Subscription(
                id=int(row["id"]),
                user_id=int(row["user_id"]),
                plan=row.get("plan","free"),
                status=row.get("status","active"),
                cancel_at_period_end=row.get("cancel_at_period_end","False") == "True",
                period_start=row.get("period_start") or None,
                period_end=row.get("period_end") or None
            )
            session.add(s)
    await session.commit()

async def import_loans(session: AsyncSession):
    path = os.path.join(BASE, "loans.csv")
    if not os.path.exists(path): return
    with open(path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if await session.get(Loan, int(row["id"])): continue
            l = Loan(
                id=int(row["id"]),
                user_id=int(row["user_id"]),
                work_id=int(row["work_id"]),
                status=row.get("status","active"),
                start=row.get("start") or None,
                end=row.get("end") or None
            )
            session.add(l)
    await session.commit()

async def import_queue(session: AsyncSession):
    path = os.path.join(BASE, "queue.csv")
    if not os.path.exists(path): return
    with open(path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if await session.get(QueueItem, int(row["id"])): continue
            q = QueueItem(
                id=int(row["id"]),
                user_id=int(row["user_id"]),
                work_id=int(row["work_id"]),
                priority=int(row.get("priority",2))
            )
            session.add(q)
    await session.commit()

async def main():
    await init_db()
    async with SessionLocal() as session:
        await import_users(session)
        await import_works(session)
        await import_subscriptions(session)
        await import_loans(session)
        await import_queue(session)

if __name__ == "__main__":
    asyncio.run(main())
