# test_main.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import os
import io

from backend.db.db import get_db, Base
from backend.main import app

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)

# Test headers with valid token
headers = {"Authorization": "Bearer buildops-secret-token-2025"}


@pytest.fixture(scope="function")
def setup_database():
    """Set up test database before each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestTaskAPI:
    def test_health_check(self):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_unauthorized_access(self):
        """Test that endpoints require authentication"""
        response = client.get("/tasks")
        assert response.status_code == 403

        response = client.get("/tasks", headers={"Authorization": "Bearer invalid-token"})
        assert response.status_code == 401

    def test_create_task(self, setup_database):
        """Test task creation"""
        task_data = {
            "title": "Test Task",
            "description": "Test Description",
            "assigned_to_email": "test@example.com",
            "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "priority": "high"
        }

        response = client.post("/tasks", json=task_data, headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["assigned_to_email"] == task_data["assigned_to_email"]
        assert data["priority"] == "high"
        assert data["completed"] is False

    def test_create_task_validation_errors(self, setup_database):
        """Test task creation with invalid data"""
        # Test with past due date
        task_data = {
            "title": "Test Task",
            "assigned_to_email": "test@example.com",
            "due_date": (datetime.now() - timedelta(days=1)).isoformat(),
            "priority": "high"
        }

        response = client.post("/tasks", json=task_data, headers=headers)
        assert response.status_code == 422

        # Test with invalid email
        task_data["due_date"] = (datetime.now() + timedelta(days=1)).isoformat()
        task_data["assigned_to_email"] = "invalid-email"

        response = client.post("/tasks", json=task_data, headers=headers)
        assert response.status_code == 422

    def test_get_tasks(self, setup_database):
        """Test getting tasks list"""
        # Create test tasks
        task_data = {
            "title": "Test Task 1",
            "assigned_to_email": "test1@example.com",
            "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "priority": "medium"
        }

        client.post("/tasks", json=task_data, headers=headers)

        task_data["title"] = "Test Task 2"
        task_data["assigned_to_email"] = "test2@example.com"
        client.post("/tasks", json=task_data, headers=headers)

        # Get all tasks
        response = client.get("/tasks", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] in ["Test Task 1", "Test Task 2"]

    def test_mark_task_complete(self, setup_database):
        """Test marking task as complete"""
        # Create a task first
        task_data = {
            "title": "Complete Me",
            "assigned_to_email": "test@example.com",
            "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "priority": "low"
        }

        create_response = client.post("/tasks", json=task_data, headers=headers)
        task_id = create_response.json()["id"]

        # Mark as complete
        response = client.patch(f"/tasks/{task_id}/complete", headers=headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Task marked as complete"

        # Verify task is marked complete
        tasks_response = client.get("/tasks", headers=headers)
        tasks = tasks_response.json()
        completed_task = next(t for t in tasks if t["id"] == task_id)
        assert completed_task["completed"] is True

    def test_mark_nonexistent_task_complete(self, setup_database):
        """Test marking non-existent task as complete"""
        response = client.patch("/tasks/999/complete", headers=headers)
        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"

    def test_bulk_import_csv(self, setup_database):
        """Test CSV bulk import functionality"""
        # Create test CSV content
        csv_content = """title,description,assigned_to_email,due_date,priority
Task 1,Description 1,user1@example.com,{},high
Task 2,Description 2,user2@example.com,{},medium
Task 3,Description 3,user3@example.com,{},low""".format(
            (datetime.now() + timedelta(days=1)).isoformat(),
            (datetime.now() + timedelta(days=2)).isoformat(),
            (datetime.now() + timedelta(days=3)).isoformat()
        )

        # Create temporary CSV file
        csv_bytes = csv_content.encode('utf-8')
        files = {"file": ("test.csv", io.BytesIO(csv_bytes), "text/csv")}

        response = client.post("/tasks/bulk-import", files=files, headers=headers)
        assert response.status_code == 200

        job_data = response.json()
        assert job_data["status"] == "pending"
        assert job_data["total_rows"] == 3

        # Check import job status
        job_id = job_data["id"]
        status_response = client.get(f"/import-jobs/{job_id}", headers=headers)
        assert status_response.status_code == 200

    def test_bulk_import_invalid_file(self, setup_database):
        """Test bulk import with invalid file type"""
        files = {"file": ("test.txt", io.BytesIO("not a csv".encode('utf-8')), "text/plain")}

        response = client.post("/tasks/bulk-import", files=files, headers=headers)
        assert response.status_code == 400
        assert "File must be a CSV" in response.json()["detail"]

    def test_get_nonexistent_import_job(self, setup_database):
        """Test getting status of non-existent import job"""
        response = client.get("/import-jobs/fake-id", headers=headers)
        assert response.status_code == 404
        assert response.json()["detail"] == "Import job not found"


if __name__ == "__main__":
    # Clean up test database if it exists
    if os.path.exists("test.db"):
        os.remove("test.db")

    pytest.main([__file__, "-v"])