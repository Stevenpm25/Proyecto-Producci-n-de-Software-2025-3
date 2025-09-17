from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func
from models.models_loans import Loan, LoanPublic, QueueItem, QueuePublic
from models.models_works import Work
from models.models_users import User
from patterns.factory import PlanFactory

# --- Helpers ---
async def _active_loans_count(session: AsyncSession, work_id: int) -> int:
    stmt = select(func.count(Loan.id)).where(Loan.work_id == work_id, Loan.status == "active")
    return (await session.execute(stmt)).scalar() or 0

async def _available_slots(session: AsyncSession, work_id: int) -> int:
    work = await session.get(Work, work_id)
    if not work:
        return 0
    return max(0, work.max_slots - await _active_loans_count(session, work_id))

async def _user_priority(session: AsyncSession, user_id: int) -> int:
    user = await session.get(User, user_id)
    if not user:
        return 2
    # premium -> prioridad 1, free -> 2
    plan = "premium" if user.role == "premium" else "free"
    return 1 if plan == "premium" else 2

# --- API de operaciones ---
async def list_loans(session: AsyncSession) -> List[LoanPublic]:
    rs = await session.execute(select(Loan))
    return [LoanPublic.model_validate(l) for l in rs.scalars().all()]

async def borrow_work(session: AsyncSession, user_id: int, work_id: int) -> Tuple[str, Optional[LoanPublic] | QueuePublic]:
    # Reglas por plan (puedes extender con límites mensuales si quieres)
    PlanFactory.create("premium" if (await session.get(User, user_id)).role == "premium" else "free")

    # Si hay cupo, crear préstamo activo
    if await _available_slots(session, work_id) > 0:
        loan = Loan(user_id=user_id, work_id=work_id, status="active")
        session.add(loan)
        await session.commit()
        await session.refresh(loan)
        return ("loan_created", LoanPublic.model_validate(loan))

    # Si no hay cupo, encolar con prioridad (1 premium, 2 free)
    prio = await _user_priority(session, user_id)
    qi = QueueItem(user_id=user_id, work_id=work_id, priority=prio)
    session.add(qi)
    await session.commit()
    await session.refresh(qi)
    return ("queued", QueuePublic.model_validate(qi))

async def return_loan(session: AsyncSession, loan_id: int) -> Optional[LoanPublic]:
    loan = await session.get(Loan, loan_id)
    if not loan or loan.status != "active":
        return None
    loan.status = "returned"
    session.add(loan)
    await session.commit()
    await session.refresh(loan)

    # Liberado un cupo: si hay cola, atender al siguiente (menor priority primero y FIFO)
    rs = await session.execute(
        select(QueueItem).where(QueueItem.work_id == loan.work_id).order_by(QueueItem.priority.asc(),
                                                                            QueueItem.created_at.asc())
    )
    nxt = rs.scalars().first()
    if nxt:
        # Crear préstamo para el siguiente y eliminar de cola
        new_loan = Loan(user_id=nxt.user_id, work_id=nxt.work_id, status="active")
        session.add(new_loan)
        await session.delete(nxt)
        await session.commit()

    return LoanPublic.model_validate(loan)

async def list_queue(session: AsyncSession, work_id: int) -> List[QueuePublic]:
    rs = await session.execute(select(QueueItem).where(QueueItem.work_id == work_id)
                               .order_by(QueueItem.priority.asc(), QueueItem.created_at.asc()))
    return [QueuePublic.model_validate(q) for q in rs.scalars().all()]
