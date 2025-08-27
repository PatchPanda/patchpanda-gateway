"""GitHub webhook endpoints."""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from fastapi.responses import JSONResponse

from ..services.github_app import GitHubAppService
from ..services.authz import AuthService
from ..services.config_loader import ConfigLoaderService
from ..services.queue import QueueService
from ..services.checks import ChecksService
from ..security.signature import verify_webhook_signature
from ..models.config import TestbotConfig

router = APIRouter()


@router.post("/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(None),
    x_github_event: str = Header(None),
    x_github_delivery: str = Header(None),
):
    """Handle GitHub webhook events."""

    # Verify webhook signature
    if not x_hub_signature_256:
        raise HTTPException(status_code=401, detail="Missing signature header")

    body = await request.body()
    if not verify_webhook_signature(body, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse webhook payload
    payload = await request.json()

    # Handle different event types
    if x_github_event == "issue_comment":
        return await handle_issue_comment(
            payload, github_app_service, auth_service, config_loader, queue_service, checks_service
        )
    elif x_github_event == "pull_request":
        return await handle_pull_request(
            payload, github_app_service, auth_service, config_loader, queue_service, checks_service
        )
    else:
        # Acknowledge other events
        return JSONResponse(content={"status": "acknowledged"})


async def handle_issue_comment(
    payload: Dict[str, Any],
    github_app_service: GitHubAppService,
    auth_service: AuthService,
    config_loader: ConfigLoaderService,
    queue_service: QueueService,
    checks_service: ChecksService,
) -> JSONResponse:
    """Handle issue comment events."""
    # TODO: Implement issue comment handling
    # - Check if comment contains test generation command
    # - Verify user permissions
    # - Load configuration
    # - Enqueue test generation job
    return JSONResponse(content={"status": "comment_processed"})


async def handle_pull_request(
    payload: Dict[str, Any],
    github_app_service: GitHubAppService,
    auth_service: AuthService,
    config_loader: ConfigLoaderService,
    queue_service: QueueService,
    checks_service: ChecksService,
) -> JSONResponse:
    """Handle pull request events."""
    # TODO: Implement PR event handling
    # - Check PR state changes
    # - Update status checks
    # - Handle configuration changes
    return JSONResponse(content={"status": "pr_processed"})
