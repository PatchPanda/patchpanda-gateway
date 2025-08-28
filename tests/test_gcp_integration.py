"""Tests for GCP integration."""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from google.cloud import secretmanager, kms_v1

from patchpanda.gateway.security.secrets import SecretsManager
from patchpanda.gateway.settings import get_settings


@pytest.fixture
def mock_gcp_clients():
    """Mock GCP clients for testing."""
    with patch('patchpanda.gateway.security.secrets.secretmanager.SecretManagerServiceClient') as mock_secrets, \
         patch('patchpanda.gateway.security.secrets.kms_v1.KeyManagementServiceClient') as mock_kms:

        # Mock Secret Manager client
        mock_secrets_instance = Mock()
        mock_secrets.return_value = mock_secrets_instance

        # Mock KMS client
        mock_kms_instance = Mock()
        mock_kms.return_value = mock_kms_instance

        yield mock_secrets_instance, mock_kms_instance


@pytest.fixture
def gcp_settings():
    """Settings with GCP configuration."""
    with patch.dict(os.environ, {
        'GCP_PROJECT_ID': 'test-project',
        'GCP_REGION': 'us-central1',
        'GCP_LOCATION': 'us-central1',
        'GCP_KEY_RING': 'test-keys',
        'GCP_CRYPTO_KEY': 'test-crypto-key',
        'GCP_SECRETS_PREFIX': 'test',
        'GCP_USE_DEFAULT_CREDENTIALS': 'true'
    }):
        yield


class TestGCPSecretsManager:
    """Test GCP secrets management functionality."""

    @patch('patchpanda.gateway.security.secrets.secretmanager.SecretManagerServiceClient')
    def test_gcp_secrets_client_creation(self, mock_secrets_client, gcp_settings):
        """Test GCP Secret Manager client creation."""
        # Mock the client creation
        mock_instance = Mock()
        mock_secrets_client.return_value = mock_instance

        # Mock the settings to return GCP config
        with patch('patchpanda.gateway.security.secrets.get_settings') as mock_get_settings:
            mock_settings = Mock()
            mock_settings.gcp_project_id = 'test-project'
            mock_settings.gcp_use_default_credentials = True
            mock_get_settings.return_value = mock_settings

            secrets = SecretsManager()
            # Force recreation of the client
            secrets._gcp_secrets_client = None
            client = secrets.gcp_secrets_client

            assert client is not None
            mock_secrets_client.assert_called_once()

    @patch('patchpanda.gateway.security.secrets.kms_v1.KeyManagementServiceClient')
    def test_gcp_kms_client_creation(self, mock_kms_client, gcp_settings):
        """Test GCP KMS client creation."""
        # Mock the client creation
        mock_instance = Mock()
        mock_kms_client.return_value = mock_instance

        # Mock the settings to return GCP config
        with patch('patchpanda.gateway.security.secrets.get_settings') as mock_get_settings:
            mock_settings = Mock()
            mock_settings.gcp_project_id = 'test-project'
            mock_settings.gcp_use_default_credentials = True
            mock_get_settings.return_value = mock_settings

            secrets = SecretsManager()
            # Force recreation of the client
            secrets._gcp_kms_client = None
            client = secrets.gcp_kms_client

            assert client is not None
            mock_kms_client.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_gcp_secret_success(self, gcp_settings, mock_gcp_clients):
        """Test successful secret retrieval from GCP."""
        mock_secrets, _ = mock_gcp_clients

        # Mock successful response
        mock_response = Mock()
        mock_response.payload.data = b"test-secret-value"
        mock_secrets.access_secret_version.return_value = mock_response

        secrets = SecretsManager()
        # Force recreation of the client
        secrets._gcp_secrets_client = mock_secrets

        result = await secrets.get_gcp_secret("test-secret")

        assert result == "test-secret-value"
        mock_secrets.access_secret_version.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_gcp_secret_failure(self, gcp_settings, mock_gcp_clients):
        """Test secret retrieval failure from GCP."""
        mock_secrets, _ = mock_gcp_clients

        # Mock failure
        mock_secrets.access_secret_version.side_effect = Exception("Access denied")

        secrets = SecretsManager()
        # Force recreation of the client
        secrets._gcp_secrets_client = mock_secrets

        result = await secrets.get_gcp_secret("test-secret")

        assert result is None

    @pytest.mark.asyncio
    async def test_encrypt_gcp_kms_success(self, gcp_settings, mock_gcp_clients):
        """Test successful encryption with GCP KMS."""
        _, mock_kms = mock_gcp_clients

        # Mock successful response
        mock_response = Mock()
        mock_response.ciphertext = b"encrypted-data"
        mock_kms.encrypt.return_value = mock_response

        # Mock crypto key path
        mock_kms.crypto_key_path.return_value = "projects/test/locations/us-central1/keyRings/test-keys/cryptoKeys/test-crypto-key"

        secrets = SecretsManager()
        # Force recreation of the client
        secrets._gcp_kms_client = mock_kms

        result = await secrets.encrypt_gcp_kms(b"plaintext-data")

        assert result == b"encrypted-data"
        mock_kms.encrypt.assert_called_once()

    @pytest.mark.asyncio
    async def test_decrypt_gcp_kms_success(self, gcp_settings, mock_gcp_clients):
        """Test successful decryption with GCP KMS."""
        _, mock_kms = mock_gcp_clients

        # Mock successful response
        mock_response = Mock()
        mock_response.plaintext = b"decrypted-data"
        mock_kms.decrypt.return_value = mock_response

        # Mock crypto key path
        mock_kms.crypto_key_path.return_value = "projects/test/locations/us-central1/keyRings/test-keys/cryptoKeys/test-crypto-key"

        secrets = SecretsManager()
        # Force recreation of the client
        secrets._gcp_kms_client = mock_kms

        result = await secrets.decrypt_gcp_kms(b"encrypted-data")

        assert result == b"decrypted-data"
        mock_kms.decrypt.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_github_private_key_gcp_fallback(self, gcp_settings, mock_gcp_clients):
        """Test GitHub private key retrieval with GCP fallback."""
        mock_secrets, _ = mock_gcp_clients

        # Mock successful GCP response
        mock_response = Mock()
        mock_response.payload.data = b"-----BEGIN RSA PRIVATE KEY-----\ntest-key\n-----END RSA PRIVATE KEY-----"
        mock_secrets.access_secret_version.return_value = mock_response

        secrets = SecretsManager()
        # Force recreation of the client
        secrets._gcp_secrets_client = mock_secrets

        result = await secrets.get_github_private_key()

        assert result == "-----BEGIN RSA PRIVATE KEY-----\ntest-key\n-----END RSA PRIVATE KEY-----"

    @pytest.mark.asyncio
    async def test_get_webhook_secret_gcp_fallback(self, gcp_settings, mock_gcp_clients):
        """Test webhook secret retrieval with GCP fallback."""
        mock_secrets, _ = mock_gcp_clients

        # Mock successful GCP response
        mock_response = Mock()
        mock_response.payload.data = b"webhook-secret-value"
        mock_secrets.access_secret_version.return_value = mock_response

        secrets = SecretsManager()
        # Force recreation of the client
        secrets._gcp_secrets_client = mock_secrets

        result = await secrets.get_webhook_secret()

        assert result == "webhook-secret-value"

    def test_no_gcp_project_id(self):
        """Test behavior when GCP_PROJECT_ID is not set."""
        with patch.dict(os.environ, {}, clear=True):
            # Mock the settings to return empty GCP config
            with patch('patchpanda.gateway.security.secrets.get_settings') as mock_get_settings:
                mock_settings = Mock()
                mock_settings.gcp_project_id = ''  # No GCP config
                mock_get_settings.return_value = mock_settings

                secrets = SecretsManager()

                # Should not create GCP clients
                assert secrets.gcp_secrets_client is None
                assert secrets.gcp_kms_client is None

    @pytest.mark.asyncio
    async def test_unified_secret_retrieval_gcp_first(self, gcp_settings, mock_gcp_clients):
        """Test unified secret retrieval preferring GCP."""
        mock_secrets, _ = mock_gcp_clients

        # Mock successful GCP response
        mock_response = Mock()
        mock_response.payload.data = b"gcp-secret-value"
        mock_secrets.access_secret_version.return_value = mock_response

        secrets = SecretsManager()
        # Force recreation of the client
        secrets._gcp_secrets_client = mock_secrets

        result = await secrets.get_secret("test-secret", use_gcp=True)

        assert result == "gcp-secret-value"

    @pytest.mark.asyncio
    async def test_unified_kms_encryption_gcp_first(self, gcp_settings, mock_gcp_clients):
        """Test unified KMS encryption preferring GCP."""
        _, mock_kms = mock_gcp_clients

        # Mock successful GCP response
        mock_response = Mock()
        mock_response.ciphertext = b"gcp-encrypted-data"
        mock_kms.encrypt.return_value = mock_response

        # Mock crypto key path
        mock_kms.crypto_key_path.return_value = "projects/test/locations/us-central1/keyRings/test-keys/cryptoKeys/test-crypto-key"

        secrets = SecretsManager()
        # Force recreation of the client
        secrets._gcp_kms_client = mock_kms

        result = await secrets.encrypt_kms(b"plaintext-data", use_gcp=True)

        assert result == b"gcp-encrypted-data"


class TestGCPFallback:
    """Test fallback behavior when GCP is not available."""

    @pytest.mark.asyncio
    async def test_fallback_to_environment_variables(self):
        """Test fallback to environment variables when GCP is not available."""
        with patch.dict(os.environ, {
            'GITHUB_APP_PRIVATE_KEY': 'env-private-key',
            'GITHUB_WEBHOOK_SECRET': 'env-webhook-secret'
        }):
            # Clear the settings cache to force reload
            get_settings.cache_clear()

            # Mock the settings to return our test values
            with patch('patchpanda.gateway.security.secrets.get_settings') as mock_get_settings:
                mock_settings = Mock()
                mock_settings.github_app_private_key = 'env-private-key'
                mock_settings.github_webhook_secret = 'env-webhook-secret'
                mock_settings.gcp_project_id = ''  # No GCP config
                mock_settings.aws_access_key_id = ''  # No AWS config
                mock_get_settings.return_value = mock_settings

                secrets = SecretsManager()

                # Should fall back to environment variables
                private_key = await secrets.get_github_private_key()
                webhook_secret = await secrets.get_webhook_secret()

                assert private_key == 'env-private-key'
                assert webhook_secret == 'env-webhook-secret'

    def test_hybrid_aws_gcp_support(self):
        """Test that both AWS and GCP can be configured simultaneously."""
        with patch.dict(os.environ, {
            'GCP_PROJECT_ID': 'gcp-project',
            'AWS_REGION': 'us-east-1',
            'AWS_ACCESS_KEY_ID': 'aws-key',
            'AWS_SECRET_ACCESS_KEY': 'aws-secret'
        }):
            secrets = SecretsManager()

            # Both should be available
            assert secrets.gcp_secrets_client is not None
            assert secrets.aws_secrets_client is not None
