"""PatchPanda Gateway main application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import admin, coverage, jobs, webhooks
from .settings import get_settings


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="PatchPanda Gateway",
        description="GitHub App and public API for PatchPanda",
        version="0.1.0",
        docs_url="/docs",  # Always enable docs for development
        redoc_url="/redoc",  # Always enable redoc for development
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount API routers
    app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
    app.include_router(coverage.router, prefix="/api/coverage", tags=["coverage"])
    app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
    app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy"}

    return app


app = create_app()
