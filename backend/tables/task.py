from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean

from backend.constants import PriorityEnum
from backend.db.db import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    assigned_to_email = Column(String, nullable=False)
    due_date = Column(DateTime, nullable=False)
    priority = Column(Enum(PriorityEnum), default=PriorityEnum.MEDIUM)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

