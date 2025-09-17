
from typing import Optional
from enum import Enum
from sqlmodel import SQLModel, Field
from .models_common import Timestamped

class PlanName(str, Enum):
    FREE = "free"
    PREMIUM = "premium"

class SubStatus(str, Enum):
    ACTIVE = "active"
    CANCELED = "canceled"
    EXPIRED = "expired"

class SubscriptionBase(SQLModel):
    user_id: int = Field(index=True)
    plan: PlanName = PlanName.FREE
    status: SubStatus = SubStatus.ACTIVE
    cancel_at_period_end: bool = False

class SubscriptionCreate(SubscriptionBase):
    period_start: Optional[str] = None  # ISO string YYYY-MM-DD
    period_end: Optional[str] = None

class Subscription(SubscriptionBase, Timestamped, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    period_start: Optional[str] = None
    period_end: Optional[str] = None

class SubscriptionPublic(SQLModel):
    id: int
    user_id: int
    plan: PlanName
    status: SubStatus
    cancel_at_period_end: bool
    period_start: Optional[str] = None
    period_end: Optional[str] = None