import csv
import io
from datetime import datetime

from backend.constants import PriorityEnum
from backend.db.db import SessionLocal
from backend.tables import BulkImportJob, Task
from backend.utility.logger import logger
from backend.utility.send_notification import send_notification


async def process_csv_import(job_id: str, csv_content: str):
    """Process CSV import asynchronously"""
    db = SessionLocal()
    job = None
    try:
        job = db.query(BulkImportJob).filter(BulkImportJob.id == job_id).first()
        if not job:
            return

        job.status = "processing"
        db.commit()

        reader = csv.DictReader(io.StringIO(csv_content))
        errors = []
        processed = 0

        for row_num, row in enumerate(reader, 1):
            try:
                # Validate and create task
                task_data = {
                    "title": row.get("title", "").strip(),
                    "description": row.get("description", "").strip() or None,
                    "assigned_to_email": row.get("assigned_to_email", "").strip(),
                    "due_date": datetime.fromisoformat(row.get("due_date", "").strip()),
                    "priority": PriorityEnum(row.get("priority", "medium").lower())
                }

                # Basic validation
                if not task_data["title"]:
                    raise ValueError("Title is required")
                if not task_data["assigned_to_email"]:
                    raise ValueError("Email is required")
                if task_data["due_date"] <= datetime.now():
                    raise ValueError("Due date must be in the future")

                # Create task
                db_task = Task(**task_data)
                db.add(db_task)
                processed += 1

                # Send notification for each task
                notification_data = {
                    "title": task_data["title"],
                    "assigned_to_email": task_data["assigned_to_email"],
                    "due_date": task_data["due_date"].isoformat(),
                    "priority": task_data["priority"].value
                }
                await send_notification(notification_data)

            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
                logger.error(f"Error processing row {row_num}: {str(e)}")

        db.commit()

        # Update job status
        job.processed_rows = processed
        job.status = "completed" if not errors else "completed_with_errors"
        job.errors = "; ".join(errors) if errors else ""
        db.commit()

        logger.info(f"Import job {job_id} completed. Processed: {processed}, Errors: {len(errors)}")

    except Exception as e:
        logger.error(f"Import job {job_id} failed: {str(e)}")

        # Only update job if it was successfully retrieved
        if job is not None:
            try:
                job.status = "failed"
                job.errors = str(e)
                db.commit()
            except Exception as commit_error:
                logger.error(f"Failed to update job status: {commit_error}")
        else:
            logger.error(f"Could not update job status - job {job_id} not found")
    finally:
        db.close()

