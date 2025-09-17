
from typing import Optional
from enum import Enum
from sqlmodel import SQLModel, Field
from .models_common import Timestamped

class LoanStatus(str, Enum):
    ACTIVE = "active"
    RETURNED = "returned"
    EXPIRED = "expired"
    QUEUED = "queued"

class LoanBase(SQLModel):
    user_id: int = Field(index=True)
    work_id: int = Field(index=True)
    status: LoanStatus = LoanStatus.ACTIVE
    start: Optional[str] = None   # ISO YYYY-MM-DD
    end: Optional[str] = None

class Loan(LoanBase, Timestamped, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class LoanPublic(SQLModel):
    id: int
    user_id: int
    work_id: int
    status: LoanStatus
    start: Optional[str] = None
    end: Optional[str] = None

# Cola simple por obra (prioridad por plan la manejamos con un int)
class QueueItemBase(SQLModel):
    user_id: int = Field(index=True)
    work_id: int = Field(index=True)
    priority: int = 2  # 1 premium, 2 free

class QueueItem(QueueItemBase, Timestamped, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

# Modelo público para la cola
class QueuePublic(SQLModel):
    id: int
    user_id: int
    work_id: int
    priority: int