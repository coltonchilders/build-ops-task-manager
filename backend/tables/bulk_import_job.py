from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime

from backend.db.db import Base

print("Importing ImportJob model", __name__)

class BulkImportJob(Base):
    __tablename__ = "import_jobs"

    id = Column(String, primary_key=True)
    status = Column(String, default="pending")  # pending, processing, completed, failed
    total_rows = Column(Integer, default=0)
    processed_rows = Column(Integer, default=0)
    errors = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

