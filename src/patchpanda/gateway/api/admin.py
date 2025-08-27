"""Admin API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from ..services.authz import AuthService
from ..db.base import get_db_session
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/billing/projects")
async def list_billing_projects(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
) -> List[dict]:
    """List billing projects (admin only)."""
    # TODO: Implement billing projects listing
    # - Verify admin permissions
    # - Fetch billing projects from database
    # - Return project summaries
    return []


@router.get("/billing/projects/{project_id}")
async def get_billing_project(
    project_id: str,
) -> dict:
    """Get billing project details (admin only)."""
    # TODO: Implement billing project retrieval
    # - Verify admin permissions
    # - Fetch project details from database
    # - Return full project information
    raise HTTPException(status_code=404, detail="Project not found")


@router.get("/keys")
async def list_api_keys(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
) -> List[dict]:
    """List API keys (admin only)."""
    # TODO: Implement API keys listing
    # - Verify admin permissions
    # - Fetch API keys from database
    # - Return key summaries (without actual key values)
    return []


@router.post("/keys")
async def create_api_key(
    key_data: dict,
) -> JSONResponse:
    """Create a new API key (admin only)."""
    # TODO: Implement API key creation
    # - Verify admin permissions
    # - Generate secure API key
    # - Store in database
    # - Return key ID and generated key
    return JSONResponse(content={"status": "key_created", "id": "temp_key_id"})
