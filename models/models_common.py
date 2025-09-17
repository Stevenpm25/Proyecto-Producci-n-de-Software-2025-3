
from datetime import datetime
from sqlmodel import SQLModel, Field

class Timestamped(SQLModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)