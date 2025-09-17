from typing import Optional
from enum import Enum
from sqlmodel import SQLModel, Field
from models.models_common import Timestamped

class UserRole(str, Enum):
    FREE = "free"
    PREMIUM = "premium"
    ADMIN = "admin"

class UserStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELED = "canceled"
    DELETED = "deleted"

class UserBase(SQLModel):
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(regex=r"[^@]+@[^@]+\.[^@]+")
    role: UserRole = UserRole.FREE
    status: UserStatus = UserStatus.ACTIVE

class UserCreate(UserBase):
    password: str = Field(min_length=6)

class User(UserBase, Timestamped, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pass_hash: str

class UserPublic(SQLModel):
    id: int
    name: str
    email: str
    role: UserRole
    status: UserStatus

class UserUpdate(SQLModel):
    name: Optional[str] = None
    email: Optional[str] = None