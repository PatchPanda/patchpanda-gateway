"""Test webhook endpoints."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from patchpanda.gateway.api.webhooks import router, handle_issue_comment, handle_pull_request


@pytest.fixture
def app():
    """Create FastAPI app with webhook router."""
    app = FastAPI()
    app.include_router(router, prefix="/webhooks")
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_services():
    """Mock service dependencies."""
    return {
        'github_app_service': Mock(),
        'auth_service': Mock(),
        'config_loader': Mock(),
        'queue_service': Mock(),
        'checks_service': Mock(),
    }


class TestWebhookEndpoints:
    """Test webhook endpoint functionality."""

    def test_github_webhook_missing_signature(self, client):
        """Test webhook without signature header."""
        response = client.post("/webhooks/github", json={"test": "data"})
        assert response.status_code == 401
        assert "Missing signature header" in response.json()["detail"]

    def test_github_webhook_invalid_signature(self, client):
        """Test webhook with invalid signature."""
        headers = {"x-hub-signature-256": "sha256=invalid"}
        response = client.post("/webhooks/github", json={"test": "data"}, headers=headers)
        assert response.status_code == 401
        assert "Invalid signature" in response.json()["detail"]

    @patch('patchpanda.gateway.api.webhooks.verify_webhook_signature')
    def test_github_webhook_issue_comment(self, mock_verify, client, mock_services):
        """Test webhook handling for issue comment events."""
        mock_verify.return_value = True

        headers = {
            "x-hub-signature-256": "sha256=valid",
            "x-github-event": "issue_comment",
            "x-github-delivery": "test-delivery"
        }

        payload = {
            "action": "created",
            "issue": {"number": 42},
            "comment": {"body": "test comment"}
        }

        with patch('patchpanda.gateway.api.webhooks.handle_issue_comment', new_callable=AsyncMock) as mock_handler:
            mock_handler.return_value = {"status": "comment_processed"}

            response = client.post("/webhooks/github", json=payload, headers=headers)

            assert response.status_code == 200
            mock_handler.assert_called_once()

    @patch('patchpanda.gateway.api.webhooks.verify_webhook_signature')
    def test_github_webhook_pull_request(self, mock_verify, client, mock_services):
        """Test webhook handling for pull request events."""
        mock_verify.return_value = True

        headers = {
            "x-hub-signature-256": "sha256=valid",
            "x-github-event": "pull_request",
            "x-github-delivery": "test-delivery"
        }

        payload = {
            "action": "opened",
            "pull_request": {"number": 42, "title": "Test PR"}
        }

        with patch('patchpanda.gateway.api.webhooks.handle_pull_request', new_callable=AsyncMock) as mock_handler:
            mock_handler.return_value = {"status": "pr_processed"}

            response = client.post("/webhooks/github", json=payload, headers=headers)

            assert response.status_code == 200
            mock_handler.assert_called_once()

    @patch('patchpanda.gateway.api.webhooks.verify_webhook_signature')
    def test_github_webhook_other_event(self, mock_verify, client):
        """Test webhook handling for other event types."""
        mock_verify.return_value = True

        headers = {
            "x-hub-signature-256": "sha256=valid",
            "x-github-event": "push",
            "x-github-delivery": "test-delivery"
        }

        payload = {"ref": "refs/heads/main"}

        response = client.post("/webhooks/github", json=payload, headers=headers)

        assert response.status_code == 200
        assert response.json() == {"status": "acknowledged"}


class TestWebhookHandlers:
    """Test webhook event handlers."""

    @pytest.mark.asyncio
    async def test_handle_issue_comment(self, mock_services):
        """Test issue comment handler."""
        payload = {
            "action": "created",
            "issue": {"number": 42},
            "comment": {"body": "test comment"}
        }

        result = await handle_issue_comment(
            payload,
            mock_services['github_app_service'],
            mock_services['auth_service'],
            mock_services['config_loader'],
            mock_services['queue_service'],
            mock_services['checks_service']
        )

        # JSONResponse doesn't have .json() method, check the content directly
        # Handle potential whitespace differences in JSON formatting
        result_content = result.body.decode()
        assert '"status":"comment_processed"' in result_content.replace(' ', '')

    @pytest.mark.asyncio
    async def test_handle_pull_request(self, mock_services):
        """Test pull request handler."""
        payload = {
            "action": "opened",
            "pull_request": {"number": 42, "title": "Test PR"}
        }

        result = await handle_pull_request(
            payload,
            mock_services['github_app_service'],
            mock_services['auth_service'],
            mock_services['config_loader'],
            mock_services['queue_service'],
            mock_services['checks_service']
        )

        # JSONResponse doesn't have .json() method, check the content directly
        # Handle potential whitespace differences in JSON formatting
        result_content = result.body.decode()
        assert '"status":"pr_processed"' in result_content.replace(' ', '')


class TestWebhookSecurity:
    """Test webhook security features."""

    def test_webhook_signature_verification(self, client):
        """Test that webhook signatures are properly verified."""
        # Test with missing signature
        response = client.post("/webhooks/github", json={"test": "data"})
        assert response.status_code == 401

        # Test with invalid signature format
        headers = {"x-hub-signature-256": "invalid-format"}
        response = client.post("/webhooks/github", json={"test": "data"}, headers=headers)
        assert response.status_code == 401

    def test_webhook_event_headers(self, client):
        """Test that webhook event headers are properly handled."""
        # Test with valid signature but missing event header
        with patch('patchpanda.gateway.api.webhooks.verify_webhook_signature', return_value=True):
            headers = {"x-hub-signature-256": "sha256=valid"}
            response = client.post("/webhooks/github", json={"test": "data"}, headers=headers)
            # Should still work but acknowledge the event
            assert response.status_code == 200


class TestWebhookPayloadHandling:
    """Test webhook payload processing."""

    @patch('patchpanda.gateway.api.webhooks.verify_webhook_signature')
    def test_webhook_payload_parsing(self, mock_verify, client):
        """Test that webhook payloads are properly parsed."""
        mock_verify.return_value = True

        headers = {
            "x-hub-signature-256": "sha256=valid",
            "x-github-event": "issue_comment",
            "x-github-delivery": "test-delivery"
        }

        # Test with valid JSON payload
        payload = {"test": "data", "number": 42}
        response = client.post("/webhooks/github", json=payload, headers=headers)
        assert response.status_code == 200

        # Test with invalid JSON (should fail)
        response = client.post("/webhooks/github", data="invalid json", headers=headers)
        assert response.status_code == 422  # Unprocessable Entity
