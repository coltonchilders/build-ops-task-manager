from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from backend.constants import PriorityEnum


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    assigned_to_email: str
    due_date: datetime
    priority: PriorityEnum
    completed: bool
    created_at: datetime

    class Config:
        orm_mode = True

