"""
FaxTriage AI — FastAPI Application

Main entry point for the backend server.

Run with:
    python -m uvicorn src.backend.main:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .database import init_database
from .routers import documents, upload, stats

# Initialize the FastAPI app
app = FastAPI(
    title="FaxTriage AI",
    description="AI-powered fax classification for healthcare practices",
    version="0.1.0"
)

# Configure CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router)
app.include_router(upload.router)
app.include_router(stats.router)


@app.on_event("startup")
def startup_event():
    """Initialize database and directories on startup."""
    settings.ensure_directories()
    init_database()


@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "FaxTriage AI",
        "version": "0.1.0"
    }


# Mount static files for uploaded PDFs (optional, for direct access)
# The /api/documents/{id}/pdf endpoint is preferred for controlled access
@app.on_event("startup")
def mount_static_files():
    """Mount uploads directory for static file serving."""
    settings.ensure_directories()
    app.mount(
        "/uploads",
        StaticFiles(directory=str(settings.upload_dir)),
        name="uploads"
    )
