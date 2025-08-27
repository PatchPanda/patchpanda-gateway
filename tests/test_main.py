"""Test main application."""

import pytest
from fastapi.testclient import TestClient

from patchpanda.gateway.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_app_title():
    """Test application title."""
    assert app.title == "PatchPanda Gateway"


def test_app_description():
    """Test application description."""
    assert "GitHub App and public API" in app.description
