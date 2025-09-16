# main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import health, tasks, import_jobs
from backend.db import db
from backend.tables import *  # this is needed to set up tables

# FastAPI app
app = FastAPI(title="BuildOps Task Management API", version="1.0.0")


# Create tables at startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs at startup
    # db.Base.metadata.drop_all(bind=db.engine)  # clears tables if needed
    db.Base.metadata.create_all(bind=db.engine)  # create tables
    yield
    # Runs at shutdown (if you want cleanup, e.g., close DB connections)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers with prefixes and tags
app.include_router(
    health.router,
    tags=["health"]
)

app.include_router(
    tasks.router,
    prefix="/tasks",
    tags=["tasks"]
)

app.include_router(
    import_jobs.router,
    prefix="/import-jobs",
    tags=["import"]
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)