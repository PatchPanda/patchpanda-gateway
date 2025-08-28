"""Test GitHub App service functionality."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone, timedelta

from patchpanda.gateway.services.github_app import GitHubAppService
from patchpanda.gateway.settings import Settings
from patchpanda.gateway.security.secrets import SecretsManager


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    settings = Mock(spec=Settings)
    settings.github_app_id = "12345"
    # Use a valid RSA private key for testing
    settings.github_app_private_key = """-----BEGIN RSA PRIVATE KEY-----
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
nGyaP6aD2nB4DVwxrbF/5+6zQ8b8KJDY5aG
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
-----END RSA PRIVATE KEY-----"""
    return settings


@pytest.fixture
def github_service(mock_settings):
    """Create GitHub service with mocked settings."""
    with patch('patchpanda.gateway.services.github_app.get_settings', return_value=mock_settings):
        return GitHubAppService()


class TestGitHubAppService:
    """Test GitHub App service methods."""

    def test_init(self, github_service):
        """Test service initialization."""
        assert github_service.settings is not None
        assert github_service._private_key is None

    @pytest.mark.asyncio
    async def test_private_key_property(self, github_service):
        """Test private key property."""
        # First access should load the key
        key = await github_service.private_key
        assert key.startswith("-----BEGIN RSA PRIVATE KEY-----")
        assert "-----END RSA PRIVATE KEY-----" in key

        # Second access should use cached value
        assert github_service._private_key is not None
        assert await github_service.private_key == key

    @pytest.mark.asyncio
    @patch('patchpanda.gateway.services.github_app.jwt.encode')
    async def test_generate_jwt(self, mock_jwt_encode, github_service):
        """Test JWT generation."""
        mock_jwt_encode.return_value = "mock.jwt.token"

        jwt_token = await github_service.generate_jwt()

        assert jwt_token == "mock.jwt.token"
        mock_jwt_encode.assert_called_once()

        # Verify the call arguments
        call_args = mock_jwt_encode.call_args
        assert call_args[1]["algorithm"] == "RS256"
        assert call_args[0][1] == await github_service.private_key  # private key

    @pytest.mark.asyncio
    async def test_get_installation_token_placeholder(self, github_service):
        """Test installation token method (placeholder implementation)."""
        token = await github_service.get_installation_token(12345)
        assert token == "temp_installation_token"

    @pytest.mark.asyncio
    async def test_make_github_request_placeholder(self, github_service):
        """Test GitHub API request method (placeholder implementation)."""
        response = await github_service.make_github_request("GET", "/test", 12345)
        assert response == {"status": "not_implemented"}

    @pytest.mark.asyncio
    async def test_get_repository_info(self, github_service):
        """Test repository info method."""
        with patch.object(github_service, 'make_github_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"name": "test-repo", "owner": "test-user"}

            result = await github_service.get_repository_info("test-user", "test-repo", 12345)

            mock_request.assert_called_once_with("GET", "/repos/test-user/test-repo", 12345)
            assert result == {"name": "test-repo", "owner": "test-user"}

    @pytest.mark.asyncio
    async def test_get_pull_request(self, github_service):
        """Test pull request method."""
        with patch.object(github_service, 'make_github_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"number": 42, "title": "Test PR"}

            result = await github_service.get_pull_request("test-user", "test-repo", 42, 12345)

            mock_request.assert_called_once_with("GET", "/repos/test-user/test-repo/pulls/42", 12345)
            assert result == {"number": 42, "title": "Test PR"}


class TestGitHubAppServiceIntegration:
    """Integration tests for GitHub App service."""

    @pytest.mark.asyncio
    @patch('patchpanda.gateway.services.github_app.jwt.encode')
    async def test_full_workflow(self, mock_jwt_encode, github_service):
        """Test complete workflow from JWT to API request."""
        mock_jwt_encode.return_value = "mock.jwt.token"

        # Generate JWT
        jwt = await github_service.generate_jwt()
        assert jwt == "mock.jwt.token"

        # Get installation token (placeholder)
        token = await github_service.get_installation_token(12345)
        assert token == "temp_installation_token"

        # Make API request (placeholder)
        response = await github_service.make_github_request("GET", "/test", 12345)
        assert response == {"status": "not_implemented"}


class TestGitHubAppServiceErrorHandling:
    """Test error handling in GitHub App service."""

    @pytest.mark.asyncio
    @patch('patchpanda.gateway.services.github_app.jwt.encode')
    async def test_missing_app_id(self, mock_jwt_encode):
        """Test service with missing app ID."""
        mock_settings = Mock(spec=Settings)
        mock_settings.github_app_id = ""
        mock_settings.github_app_private_key = "test-key"
        mock_jwt_encode.return_value = "mock.jwt.token"

        with patch('patchpanda.gateway.services.github_app.get_settings', return_value=mock_settings):
            service = GitHubAppService()

            # Should still work but with empty app ID
            jwt = await service.generate_jwt()
            assert jwt == "mock.jwt.token"

    @pytest.mark.asyncio
    async def test_missing_private_key(self):
        """Test service with missing private key."""
        mock_settings = Mock(spec=Settings)
        mock_settings.github_app_id = "12345"
        mock_settings.github_app_private_key = ""

        with patch('patchpanda.gateway.services.github_app.get_settings', return_value=mock_settings):
            with patch.object(SecretsManager, 'get_github_private_key', return_value=None):
                service = GitHubAppService()

                # Should raise error when trying to generate JWT
                with pytest.raises(Exception):
                    await service.generate_jwt()
