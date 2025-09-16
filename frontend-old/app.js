// App.js
import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE = 'http://localhost:8000';
const API_TOKEN = 'buildops-secret-token-2025';

const api = {
  headers: {
    'Authorization': `Bearer ${API_TOKEN}`,
    'Content-Type': 'application/json'
  },

  async get(endpoint) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      headers: this.headers
    });
    if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
    return response.json();
  },

  async post(endpoint, data) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
    return response.json();
  },

  async patch(endpoint) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'PATCH',
      headers: this.headers
    });
    if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
    return response.json();
  },

  async uploadFile(endpoint, file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${API_TOKEN}`
      },
      body: formData
    });
    if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
    return response.json();
  }
};

function App() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [importStatus, setImportStatus] = useState(null);

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.get('/tasks');
      setTasks(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTaskComplete = async (taskId) => {
    try {
      await api.patch(`/tasks/${taskId}/complete`);
      await loadTasks(); // Refresh tasks
    } catch (err) {
      setError(err.message);
    }
  };

  const handleCreateTask = async (taskData) => {
    try {
      await api.post('/tasks', taskData);
      await loadTasks(); // Refresh tasks
      setShowCreateForm(false);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleFileUpload = async (file) => {
    try {
      setError(null);
      const job = await api.uploadFile('/tasks/bulk-import', file);
      setImportStatus({ jobId: job.id, status: job.status, totalRows: job.total_rows });

      // Poll for import status
      const pollStatus = async () => {
        try {
          const statusData = await api.get(`/import-jobs/${job.id}`);
          setImportStatus(statusData);

          if (statusData.status === 'processing' || statusData.status === 'pending') {
            setTimeout(pollStatus, 2000); // Poll every 2 seconds
          } else {
            // Import completed, refresh tasks
            await loadTasks();
          }
        } catch (err) {
          setError(err.message);
        }
      };

      setTimeout(pollStatus, 1000);
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading && tasks.length === 0) {
    return <div className="app"><div className="loading">Loading tasks...</div></div>;
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>BuildOps Task Dashboard</h1>
        <div className="header-actions">
          <button
            className="btn btn-primary"
            onClick={() => setShowCreateForm(!showCreateForm)}
          >
            {showCreateForm ? 'Cancel' : 'Create Task'}
          </button>
        </div>
      </header>

      {error && (
        <div className="error-banner">
          Error: {error}
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      <main className="main-content">
        <div className="content-grid">
          <div className="tasks-section">
            <h2>Tasks ({tasks.length})</h2>
            <TaskList
              tasks={tasks}
              onTaskComplete={handleTaskComplete}
            />
          </div>

          <div className="sidebar">
            {showCreateForm && (
              <CreateTaskForm
                onSubmit={handleCreateTask}
                onCancel={() => setShowCreateForm(false)}
              />
            )}

            <BulkImportSection
              onFileUpload={handleFileUpload}
              importStatus={importStatus}
            />
          </div>
        </div>
      </main>
    </div>
  );
}

function TaskList({ tasks, onTaskComplete }) {
  const activeTasks = tasks.filter(task => !task.completed);
  const completedTasks = tasks.filter(task => task.completed);

  return (
    <div className="task-list">
      {activeTasks.length > 0 && (
        <div className="task-group">
          <h3>Active Tasks ({activeTasks.length})</h3>
          {activeTasks.map(task => (
            <TaskCard
              key={task.id}
              task={task}
              onComplete={onTaskComplete}
            />
          ))}
        </div>
      )}

      {completedTasks.length > 0 && (
        <div className="task-group">
          <h3>Completed Tasks ({completedTasks.length})</h3>
          {completedTasks.map(task => (
            <TaskCard
              key={task.id}
              task={task}
              onComplete={onTaskComplete}
              disabled={true}
            />
          ))}
        </div>
      )}

      {tasks.length === 0 && (
        <div className="empty-state">
          <p>No tasks found. Create your first task to get started!</p>
        </div>
      )}
    </div>
  );
}

function TaskCard({ task, onComplete, disabled = false }) {
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
  };

  const getPriorityColor = (priority) => {
    switch(priority) {
      case 'high': return '#ff4757';
      case 'medium': return '#ffa502';
      case 'low': return '#2ed573';
      default: return '#747d8c';
    }
  };

  const isOverdue = new Date(task.due_date) < new Date() && !task.completed;

  return (
    <div className={`task-card ${task.completed ? 'completed' : ''} ${isOverdue ? 'overdue' : ''}`}>
      <div className="task-header">
        <h4>{task.title}</h4>
        <div className="task-actions">
          {!task.completed && (
            <button
              className="btn btn-small btn-success"
              onClick={() => onComplete(task.id)}
              disabled={disabled}
            >
              Complete
            </button>
          )}
        </div>
      </div>

      {task.description && (
        <p className="task-description">{task.description}</p>
      )}

      <div className="task-meta">
        <div className="meta-item">
          <strong>Assigned to:</strong> {task.assigned_to_email}
        </div>
        <div className="meta-item">
          <strong>Due:</strong>
          <span className={isOverdue ? 'overdue-text' : ''}>
            {formatDate(task.due_date)}
          </span>
        </div>
        <div className="meta-item">
          <strong>Priority:</strong>
          <span
            className="priority-badge"
            style={{ backgroundColor: getPriorityColor(task.priority) }}
          >
            {task.priority.toUpperCase()}
          </span>
        </div>
      </div>
    </div>
  );
}

function CreateTaskForm({ onSubmit, onCancel }) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    assigned_to_email: '',
    due_date: '',
    priority: 'medium'
  });

  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (submitting) return;

    setSubmitting(true);
    try {
      // Convert due_date to ISO format for API
      const submitData = {
        ...formData,
        due_date: new Date(formData.due_date).toISOString()
      };
      await onSubmit(submitData);
    } finally {
      setSubmitting(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  // Get minimum date (tomorrow)
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  const minDate = tomorrow.toISOString().slice(0, 16);

  return (
    <div className="create-task-form">
      <h3>Create New Task</h3>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="title">Title *</label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title}
            onChange={handleChange}
            required
            placeholder="Enter task title"
          />
        </div>

        <div className="form-group">
          <label htmlFor="description">Description</label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Enter task description"
            rows="3"
          />
        </div>

        <div className="form-group">
          <label htmlFor="assigned_to_email">Assigned To *</label>
          <input
            type="email"
            id="assigned_to_email"
            name="assigned_to_email"
            value={formData.assigned_to_email}
            onChange={handleChange}
            required
            placeholder="email@example.com"
          />
        </div>

        <div className="form-group">
          <label htmlFor="due_date">Due Date *</label>
          <input
            type="datetime-local"
            id="due_date"
            name="due_date"
            value={formData.due_date}
            onChange={handleChange}
            min={minDate}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="priority">Priority</label>
          <select
            id="priority"
            name="priority"
            value={formData.priority}
            onChange={handleChange}
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>

        <div className="form-actions">
          <button
            type="button"
            onClick={onCancel}
            className="btn btn-secondary"
            disabled={submitting}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={submitting}
          >
            {submitting ? 'Creating...' : 'Create Task'}
          </button>
        </div>
      </form>
    </div>
  );
}

function BulkImportSection({ onFileUpload, importStatus }) {
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = React.useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file) => {
    if (file.type !== 'text/csv' && !file.name.endsWith('.csv')) {
      alert('Please select a CSV file');
      return;
    }
    onFileUpload(file);
  };

  const getStatusMessage = () => {
    if (!importStatus) return null;

    switch (importStatus.status) {
      case 'pending':
        return `Import queued (${importStatus.total_rows} rows)`;
      case 'processing':
        return `Processing... (${importStatus.processed_rows}/${importStatus.total_rows})`;
      case 'completed':
        return `✅ Import completed successfully (${importStatus.processed_rows} tasks created)`;
      case 'completed_with_errors':
        return `⚠️ Import completed with errors (${importStatus.processed_rows} tasks created)`;
      case 'failed':
        return `❌ Import failed: ${importStatus.errors}`;
      default:
        return null;
    }
  };

  return (
    <div className="bulk-import-section">
      <h3>Bulk Import</h3>
      <p className="import-help">
        Upload a CSV file with columns: title, description, assigned_to_email, due_date, priority
      </p>

      <div
        className={`file-drop-zone ${dragActive ? 'active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
        <div className="drop-zone-content">
          <div className="upload-icon">📁</div>
          <p>Click to select CSV file or drag and drop</p>
        </div>
      </div>

      {importStatus && (
        <div className={`import-status ${importStatus.status}`}>
          <p>{getStatusMessage()}</p>
          {importStatus.errors && (
            <details>
              <summary>View Errors</summary>
              <pre>{importStatus.errors}</pre>
            </details>
          )}
        </div>
      )}

      <div className="csv-example">
        <details>
          <summary>CSV Format Example</summary>
          <pre>{`title,description,assigned_to_email,due_date,priority
"Setup database","Initialize the database schema","dev@example.com","2024-12-01T10:00:00","high"
"Write tests","Create unit tests for API","qa@example.com","2024-12-02T15:30:00","medium"`}</pre>
        </details>
      </div>
    </div>
  );
}

export default App;