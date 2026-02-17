"""
FaxTriage AI — FastAPI Application

Main entry point for the backend server.

Run with:
    python -m uvicorn src.backend.main:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

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


# Serve frontend static files in production
if settings.frontend_dist.exists():
    # Serve static assets (JS, CSS, images)
    app.mount("/assets", StaticFiles(directory=settings.frontend_dist / "assets"), name="static_assets")

    # Serve other static files at root level (favicon, etc.)
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve the React SPA for any non-API route."""
        # Try to serve the exact file first
        file_path = settings.frontend_dist / full_path
        if full_path and file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        # Fall back to index.html for SPA routing
        return FileResponse(settings.frontend_dist / "index.html")
