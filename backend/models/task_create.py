from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, validator

from backend.constants import PriorityEnum


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    assigned_to_email: EmailStr
    due_date: datetime
    priority: PriorityEnum = PriorityEnum.MEDIUM

    @validator('due_date', pre=True)
    def parse_due_date(cls, v):
        """Handle datetime strings from frontend"""
        if isinstance(v, str):
            # Remove timezone info and microseconds
            clean_v = v.replace('Z', '').split('+')[0].split('.')[0]
            return datetime.fromisoformat(clean_v)
        return v

    @validator('due_date')
    def due_date_must_be_future(cls, v):
        if v <= datetime.now():
            raise ValueError('Due date must be in the future')
        return v

