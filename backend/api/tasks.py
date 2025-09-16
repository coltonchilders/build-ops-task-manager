import csv
import io
import uuid
from typing import List, Optional

from fastapi import Depends, BackgroundTasks, HTTPException, UploadFile, File, APIRouter
from sqlalchemy.orm import Session

from backend.db.db import get_db
from backend.models.import_job_response import ImportJobResponse
from backend.models.task_create import TaskCreate
from backend.models.task_response import TaskResponse
from backend.tables import BulkImportJob, Task
from backend.utility.process_csv import process_csv_import
from backend.utility.send_notification import send_notification
from backend.utility.verify_token import verify_token

router = APIRouter()

@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
        completed: Optional[bool] = None,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    """Get all tasks for a team with optional filtering"""
    query = db.query(Task)
    if completed is not None:
        query = query.filter(Task.completed == completed)
    tasks = query.order_by(Task.due_date.asc()).all()
    return tasks


@router.post("/", response_model=TaskResponse)
async def create_task(
        task: TaskCreate,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    """Create a new task"""
    db_task = Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    # Send notification asynchronously
    task_data = {
        "id": db_task.id,
        "title": db_task.title,
        "assigned_to_email": db_task.assigned_to_email,
        "due_date": db_task.due_date.isoformat(),
        "priority": db_task.priority.value
    }
    background_tasks.add_task(send_notification, task_data)

    return db_task


@router.patch("/{task_id}/complete")
async def mark_task_complete(
        task_id: int,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    """Mark a task as completed"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.completed = True
    db.commit()
    return {"message": "Task marked as complete", "task_id": task_id}


@router.post("/bulk-import", response_model=ImportJobResponse)
async def bulk_import_tasks(
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    """Bulk import tasks from CSV file"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        content = await file.read()
        csv_content = content.decode('utf-8')

        # Count total rows
        reader = csv.DictReader(io.StringIO(csv_content))
        total_rows = sum(1 for _ in reader)

        # Create import job
        job_id = str(uuid.uuid4())
        job = BulkImportJob(id=job_id, total_rows=total_rows)
        db.add(job)
        db.commit()

        # Process asynchronously
        background_tasks.add_task(process_csv_import, job_id, csv_content)

        return job

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")
