from typing import Optional
from sqlmodel import SQLModel, Field
from models.models_common import Timestamped  # Cambiado aquí

class WorkBase(SQLModel):
    title: str = Field(min_length=2, max_length=200)
    author: str = Field(min_length=2, max_length=200)
    category: Optional[str] = None
    cover_url: Optional[str] = None
    max_slots: int = Field(default=1, ge=1)
    visible: bool = True

class WorkCreate(WorkBase):
    pass

class Work(WorkBase, Timestamped, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class WorkPublic(SQLModel):
    id: int
    title: str
    author: str
    category: Optional[str] = None
    cover_url: Optional[str] = None
    max_slots: int
    visible: bool
