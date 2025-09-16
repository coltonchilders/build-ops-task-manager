from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session

from backend.db.db import get_db
from backend.models.import_job_response import ImportJobResponse
from backend.tables import BulkImportJob
from backend.utility.verify_token import verify_token

router = APIRouter()

@router.get("/{job_id}", response_model=ImportJobResponse)
async def get_import_job_status(
        job_id: str,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    """Get the status of a bulk import job"""
    job = db.query(BulkImportJob).filter(BulkImportJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Import job not found")
    return job
