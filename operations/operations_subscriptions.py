from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from models.models_subscriptions import (
    Subscription, SubscriptionCreate, SubscriptionPublic
)
from patterns.factory import PlanFactory

async def read_user_subscription(session: AsyncSession, user_id: int) -> Optional[SubscriptionPublic]:
    rs = await session.execute(select(Subscription).where(Subscription.user_id == user_id,
                                                         Subscription.status == "active"))
    sub = rs.scalars().first()
    return SubscriptionPublic.model_validate(sub) if sub else None

async def create_or_replace_subscription(session: AsyncSession, data: SubscriptionCreate) -> SubscriptionPublic:
    # Cancelar suscripciones activas previas del usuario
    rs = await session.execute(select(Subscription).where(Subscription.user_id == data.user_id,
                                                         Subscription.status == "active"))
    current = rs.scalars().all()
    for s in current:
        s.status = "canceled"
        session.add(s)

    # Validar plan con Factory (por si agregas más adelante límites por plan)
    PlanFactory.create(data.plan)  # solo asegura que existe el plan

    new_sub = Subscription(**data.model_dump())
    session.add(new_sub)
    await session.commit()
    await session.refresh(new_sub)
    return SubscriptionPublic.model_validate(new_sub)

async def cancel_subscription(session: AsyncSession, user_id: int, at_period_end: bool = True) -> Optional[SubscriptionPublic]:
    rs = await session.execute(select(Subscription).where(Subscription.user_id == user_id,
                                                         Subscription.status == "active"))
    sub = rs.scalars().first()
    if not sub:
        return None
    if at_period_end:
        sub.cancel_at_period_end = True
    else:
        sub.status = "canceled"
    session.add(sub)
    await session.commit()
    await session.refresh(sub)
    return SubscriptionPublic.model_validate(sub)

async def list_subscriptions(session: AsyncSession) -> List[SubscriptionPublic]:
    rs = await session.execute(select(Subscription))
    return [SubscriptionPublic.model_validate(s) for s in rs.scalars().all()]
