# BuildOps Task Management System

A full-stack task management application built with FastAPI (Python) backend and React frontend, featuring bulk CSV import capabilities and real-time notifications.

## Features

### Backend (FastAPI)
- **RESTful API** for task management
- **Bulk CSV Import** with asynchronous processing
- **Token-based Authentication** (hardcoded for demo)
- **SQLite Database** with SQLAlchemy ORM
- **Data Validation** using Pydantic models
- **Notification Integration** with external Node.js service
- **Comprehensive Error Handling**

### Frontend (React)
- **Task Dashboard** with create, list, and complete functionality
- **CSV File Upload** with drag-and-drop support
- **Real-time Import Status** with progress tracking
- **Responsive Design** optimized for desktop and mobile
- **Error Handling** with user-friendly feedback

## Architecture & Design Decisions

### Backend Framework Choice
I chose **FastAPI** over Flask for this project because:
- **Automatic API documentation** with Swagger/OpenAPI
- **Built-in data validation** with Pydantic models
- **Async/await support** for better performance with I/O operations
- **Type hints** for better code maintainability
- **Modern Python features** and excellent developer experience

### Key Design Patterns
- **Separation of Concerns**: Clear separation between API routes, database models, and business logic
- **Asynchronous Processing**: Bulk imports run in background tasks to avoid blocking the API
- **Graceful Error Handling**: Comprehensive validation and error messages
- **RESTful Design**: Standard HTTP methods and status codes
- **Database Abstraction**: SQLAlchemy ORM for database independence

## Setup Instructions

### Prerequisites
- Python 3.8+ 
- Node.js 16+
- npm or yarn

### Backend Setup

1. **Create and activate virtual environment**
   ```bash
   python -m venv buildops-env
   source buildops-env/bin/activate  # On Windows: buildops-env\Scripts\activate
   ```

2. **Install Python dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Run the FastAPI server**
   ```bash
   python main.py
   ```
   
   The API will be available at `http://localhost:8000`
   - Swagger documentation: `http://localhost:8000/docs`
   - ReDoc documentation: `http://localhost:8000/redoc`

### Frontend Setup

1. **Install Node.js dependencies**
   ```bash
   npm install
   ```

2. **Start the React development server**
   ```bash
   npm start
   ```
   
   The frontend will be available at `http://localhost:3000`

### Testing

**Run backend tests:**
```bash
pytest test_main.py -v
```

**Run frontend tests:**
```bash
npm test
```

## API Documentation

### Authentication
All endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer buildops-secret-token-2025
```

### Endpoints

#### Tasks
- `GET /tasks` - List all tasks (with optional `completed` filter)
- `POST /tasks` - Create a new task
- `PATCH /tasks/{id}/complete` - Mark task as completed

#### Bulk Import
- `POST /tasks/bulk-import` - Upload CSV file for bulk import
- `GET /import-jobs/{job_id}` - Get import job status

#### Health Check
- `GET /health` - API health status

### Task Model
```json
{
  "title": "string (required)",
  "description": "string (optional)",
  "assigned_to_email": "string (required, valid email)",
  "due_date": "datetime (required, must be in future)",
  "priority": "enum: low|medium|high (default: medium)"
}
```

### CSV Format
```csv
title,description,assigned_to_email,due_date,priority
"Task Title","Task Description","user@example.com","2024-12-01T10:00:00","high"
```

## Usage Examples

### Creating a Task via API
```bash
curl -X POST "http://localhost:8000/tasks" \
  -H "Authorization: Bearer buildops-secret-token-2024" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Review Code",
    "description": "Review pull request #123",
    "assigned_to_email": "developer@example.com",
    "due_date": "2024-12-01T15:30:00",
    "priority": "medium"
  }'
```

### Bulk Import via CSV
1. Prepare CSV file with required columns
2. Use the web interface to upload the file
3. Monitor import progress in real-time
4. View any validation errors for individual rows

## Trade-offs & Limitations

### Current Limitations
1. **Hardcoded Authentication**: Uses a single static token for simplicity
2. **No User Management**: No user registration/login system
3. **Basic Notification Integration**: Assumes external notification service exists
4. **SQLite Database**: Not suitable for high-concurrency production use
5. **No Task Updates**: Can only mark tasks as complete, not edit details

### Production Considerations
1. **Database**: Switch to PostgreSQL or MySQL for production
2. **Authentication**: Implement JWT with proper user management
3. **Rate Limiting**: Add API rate limiting and request throttling
4. **Caching**: Add Redis caching for frequently accessed data
5. **Monitoring**: Add logging, metrics, and health checks
6. **Security**: Implement CORS properly, input sanitization, and HTTPS
7. **Scalability**: Consider microservices architecture for larger scale

### Scaling Strategy
1. **Horizontal Scaling**: Load balancer with multiple API instances
2. **Database Optimization**: Connection pooling, read replicas
3. **Background Jobs**: Use Celery/Redis for better task queue management
4. **CDN**: Serve static React assets via CDN
5. **Caching Layer**: Redis for session management and API response caching

## Error Handling

### Backend
- **Validation Errors**: Pydantic models provide detailed validation messages
- **Database Errors**: Graceful handling of constraint violations
- **File Processing**: Robust CSV parsing with row-level error reporting
- **External Service**: Graceful degradation when notification service is unavailable

### Frontend
- **API Errors**: User-friendly error messages with retry options
- **File Upload**: Validation for file type and size
- **Network Issues**: Loading states and error recovery
- **Form Validation**: Client-side validation with server-side verification

## Development Notes

### Code Quality
- **Type Hints**: Extensive use of Python type hints
- **Docstrings**: Comprehensive documentation for all functions
- **Error Handling**: Consistent error handling patterns
- **Testing**: Unit tests cover core functionality
- **Code Style**: Follows PEP 8 and modern React patterns

### Performance Optimizations
- **Async Processing**: Non-blocking bulk import operations
- **Database Indexing**: Appropriate indexes on frequently queried columns
- **Efficient Queries**: SQLAlchemy query optimization
- **React Optimization**: Proper state management and re-render control

## Future Enhancements

1. **User Management**: Full authentication and authorization system
2. **Task Collaboration**: Comments, attachments, and task assignments
3. **Notifications**: Email/SMS notifications with customizable preferences
4. **Advanced Filtering**: Search, sorting, and filtering capabilities
5. **Dashboard Analytics**: Task completion metrics and team performance
6. **Mobile App**: React Native mobile application
7. **Integration APIs**: Slack, email, calendar integrations
8. **Workflow Automation**: Task dependencies and automated workflows