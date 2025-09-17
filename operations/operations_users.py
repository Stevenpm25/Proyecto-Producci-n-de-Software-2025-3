
import os, csv
from typing import Optional, List, Iterable
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from passlib.hash import bcrypt
from models.models_users import User, UserCreate, UserPublic, UserUpdate
from patterns.memento import UserMementoCaretaker, snapshot_user

DELETED_CSV = "seeds/deleted_users.csv"

# ---- CSV utils ----
def _as_public_dict(u: User) -> dict:
    return {
        "id": u.id, "name": u.name, "email": u.email,
        "role": u.role, "status": u.status
    }

class _csv_utils:
    @staticmethod
    def append_or_replace(path: str, u: User):
        exists = os.path.exists(path)
        rows = []
        if exists:
            with open(path, "r", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            rows = [r for r in rows if str(r.get("id")) != str(u.id)]
        rows.append(_as_public_dict(u))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["id","name","email","role","status"])
            w.writeheader(); w.writerows(rows)

# ---- Operations ----
async def read_all_users(session: AsyncSession) -> List[UserPublic]:
    rs = await session.execute(select(User))
    return [UserPublic.model_validate(u) for u in rs.scalars().all()]

async def read_user(session: AsyncSession, user_id: int) -> Optional[UserPublic]:
    u = await session.get(User, user_id)
    return UserPublic.model_validate(u) if u else None

async def create_user(session: AsyncSession, data: UserCreate) -> UserPublic:
    hashed = bcrypt.hash(data.password)
    u = User(name=data.name, email=data.email, pass_hash=hashed)
    session.add(u)
    await session.commit()
    await session.refresh(u)
    return UserPublic.model_validate(u)

async def update_user(session: AsyncSession, user_id: int, data: UserUpdate) -> Optional[UserPublic]:
    u = await session.get(User, user_id)
    if not u: return None
    UserMementoCaretaker.save(snapshot_user(u))
    patch = data.model_dump(exclude_unset=True)
    for k, v in patch.items():
        setattr(u, k, v)
    session.add(u); await session.commit(); await session.refresh(u)
    return UserPublic.model_validate(u)

async def cancel_user(session: AsyncSession, user_id: int) -> Optional[UserPublic]:
    u = await session.get(User, user_id)
    if not u: return None
    UserMementoCaretaker.save(snapshot_user(u))
    u.status = "canceled"
    session.add(u); await session.commit(); await session.refresh(u)
    _csv_utils.append_or_replace(DELETED_CSV, u)
    return UserPublic.model_validate(u)

async def delete_user(session: AsyncSession, user_id: int) -> Optional[UserPublic]:
    u = await session.get(User, user_id)
    if not u: return None
    UserMementoCaretaker.save(snapshot_user(u))
    _csv_utils.append_or_replace(DELETED_CSV, u)
    out = UserPublic.model_validate(u)
    await session.delete(u); await session.commit()
    return out