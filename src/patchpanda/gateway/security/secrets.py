"""Secrets management for KMS and Secrets Manager."""

import boto3
from typing import Optional, Union
from google.cloud import secretmanager, kms_v1
from google.auth import default
from google.auth.exceptions import DefaultCredentialsError
import json
import os

from ..settings import get_settings


class SecretsManager:
    """Secrets management service supporting both AWS and GCP."""

    def __init__(self):
        self.settings = get_settings()
        self._aws_kms_client = None
        self._aws_secrets_client = None
        self._gcp_secrets_client = None
        self._gcp_kms_client = None
        self._gcp_credentials = None

    # AWS Clients
    @property
    def aws_kms_client(self):
        """Get AWS KMS client."""
        if not self._aws_kms_client:
            self._aws_kms_client = boto3.client(
                'kms',
                region_name=self.settings.aws_region,
                aws_access_key_id=self.settings.aws_access_key_id,
                aws_secret_access_key=self.settings.aws_secret_access_key
            )
        return self._aws_kms_client

    @property
    def aws_secrets_client(self):
        """Get AWS Secrets Manager client."""
        if not self._aws_secrets_client:
            self._aws_secrets_client = boto3.client(
                'secretsmanager',
                region_name=self.settings.aws_region,
                aws_access_key_id=self.settings.aws_access_key_id,
                aws_secret_access_key=self.settings.aws_secret_access_key
            )
        return self._aws_secrets_client

    # GCP Clients
    @property
    def gcp_secrets_client(self):
        """Get GCP Secret Manager client."""
        if not self._gcp_secrets_client and self.settings.gcp_project_id:
            try:
                if self.settings.gcp_use_default_credentials:
                    self._gcp_secrets_client = secretmanager.SecretManagerServiceClient()
                elif self.settings.gcp_service_account_key_path:
                    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.settings.gcp_service_account_key_path
                    self._gcp_secrets_client = secretmanager.SecretManagerServiceClient()
                else:
                    # Try to get default credentials
                    credentials, project = default()
                    self._gcp_secrets_client = secretmanager.SecretManagerServiceClient(credentials=credentials)
            except (DefaultCredentialsError, Exception) as e:
                # TODO: Log error
                self._gcp_secrets_client = None
        return self._gcp_secrets_client

    @property
    def gcp_kms_client(self):
        """Get GCP KMS client."""
        if not self._gcp_kms_client and self.settings.gcp_project_id:
            try:
                if self.settings.gcp_use_default_credentials:
                    self._gcp_kms_client = kms_v1.KeyManagementServiceClient()
                elif self.settings.gcp_service_account_key_path:
                    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.settings.gcp_service_account_key_path
                    self._gcp_kms_client = kms_v1.KeyManagementServiceClient()
                else:
                    # Try to get default credentials
                    credentials, project = default()
                    self._gcp_kms_client = kms_v1.KeyManagementServiceClient(credentials=credentials)
            except (DefaultCredentialsError, Exception) as e:
                # TODO: Log error
                self._gcp_kms_client = None
        return self._gcp_kms_client

    # AWS Methods
    async def get_aws_secret(self, secret_name: str) -> Optional[str]:
        """Get secret from AWS Secrets Manager."""
        try:
            response = self.aws_secrets_client.get_secret_value(SecretId=secret_name)
            if 'SecretString' in response:
                return response['SecretString']
            else:
                # Binary secret
                return response['SecretBinary'].decode('utf-8')
        except Exception as e:
            # TODO: Log error
            return None

    async def decrypt_aws_kms(self, encrypted_data: bytes) -> Optional[bytes]:
        """Decrypt data using AWS KMS."""
        try:
            response = self.aws_kms_client.decrypt(CiphertextBlob=encrypted_data)
            return response['Plaintext']
        except Exception as e:
            # TODO: Log error
            return None

    async def encrypt_aws_kms(self, plaintext: bytes, key_id: str) -> Optional[bytes]:
        """Encrypt data using AWS KMS."""
        try:
            response = self.aws_kms_client.encrypt(
                KeyId=key_id,
                Plaintext=plaintext
            )
            return response['CiphertextBlob']
        except Exception as e:
            # TODO: Log error
            return None

    # GCP Methods
    async def get_gcp_secret(self, secret_name: str) -> Optional[str]:
        """Get secret from GCP Secret Manager."""
        if not self.gcp_secrets_client:
            return None

        try:
            # Build the resource name of the secret version
            name = f"projects/{self.settings.gcp_project_id}/secrets/{secret_name}/versions/latest"
            response = self.gcp_secrets_client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            # TODO: Log error
            return None

    async def decrypt_gcp_kms(self, encrypted_data: bytes) -> Optional[bytes]:
        """Decrypt data using GCP KMS."""
        if not self.gcp_kms_client:
            return None

        try:
            # Build the resource name of the crypto key
            crypto_key_path = self.gcp_kms_client.crypto_key_path(
                self.settings.gcp_project_id,
                self.settings.gcp_location,
                self.settings.gcp_key_ring,
                self.settings.gcp_crypto_key
            )

            response = self.gcp_kms_client.decrypt(
                request={
                    "name": crypto_key_path,
                    "ciphertext": encrypted_data
                }
            )
            return response.plaintext
        except Exception as e:
            # TODO: Log error
            return None

    async def encrypt_gcp_kms(self, plaintext: bytes) -> Optional[bytes]:
        """Encrypt data using GCP KMS."""
        if not self.gcp_kms_client:
            return None

        try:
            # Build the resource name of the crypto key
            crypto_key_path = self.gcp_kms_client.crypto_key_path(
                self.settings.gcp_project_id,
                self.settings.gcp_location,
                self.settings.gcp_key_ring,
                self.settings.gcp_crypto_key
            )

            response = self.gcp_kms_client.encrypt(
                request={
                    "name": crypto_key_path,
                    "plaintext": plaintext
                }
            )
            return response.ciphertext
        except Exception as e:
            # TODO: Log error
            return None

    # Unified Methods (prefer GCP if available)
    async def get_secret(self, secret_name: str, use_gcp: bool = True) -> Optional[str]:
        """Get secret from either GCP Secret Manager or AWS Secrets Manager."""
        if use_gcp and self.gcp_secrets_client:
            # Try GCP first
            secret = await self.get_gcp_secret(secret_name)
            if secret:
                return secret

        # Fallback to AWS
        if self.settings.aws_access_key_id:
            return await self.get_aws_secret(secret_name)

        return None

    async def decrypt_kms(self, encrypted_data: bytes, use_gcp: bool = True) -> Optional[bytes]:
        """Decrypt data using either GCP KMS or AWS KMS."""
        if use_gcp and self.gcp_kms_client:
            # Try GCP first
            decrypted = await self.decrypt_gcp_kms(encrypted_data)
            if decrypted:
                return decrypted

        # Fallback to AWS
        if self.settings.aws_access_key_id:
            return await self.decrypt_aws_kms(encrypted_data)

        return None

    async def encrypt_kms(self, plaintext: bytes, key_id: str = None, use_gcp: bool = True) -> Optional[bytes]:
        """Encrypt data using either GCP KMS or AWS KMS."""
        if use_gcp and self.gcp_kms_client:
            # Try GCP first
            encrypted = await self.encrypt_gcp_kms(plaintext)
            if encrypted:
                return encrypted

        # Fallback to AWS
        if self.settings.aws_access_key_id and key_id:
            return await self.encrypt_aws_kms(plaintext, key_id)

        return None

    # GitHub-specific methods
    async def get_github_private_key(self) -> Optional[str]:
        """Get GitHub App private key from secrets."""
        # Try GCP first, then AWS
        secret_name = f"{self.settings.gcp_secrets_prefix}-github-private-key"

        # Try GCP
        if self.gcp_secrets_client:
            private_key = await self.get_gcp_secret(secret_name)
            if private_key:
                return private_key

        # Fallback to AWS
        if self.settings.aws_access_key_id:
            return await self.get_aws_secret("github-app-private-key")

        # Fallback to environment variable
        return self.settings.github_app_private_key

    async def get_webhook_secret(self) -> Optional[str]:
        """Get webhook secret from secrets."""
        # Try GCP first, then AWS
        secret_name = f"{self.settings.gcp_secrets_prefix}-webhook-secret"

        # Try GCP
        if self.gcp_secrets_client:
            webhook_secret = await self.get_gcp_secret(secret_name)
            if webhook_secret:
                return webhook_secret

        # Fallback to AWS
        if self.settings.aws_access_key_id:
            return await self.get_aws_secret("github-webhook-secret")

        # Fallback to environment variable
        return self.settings.github_webhook_secret

    async def get_oidc_secret(self) -> Optional[str]:
        """Get OIDC client secret from secrets."""
        # Try GCP first, then AWS
        secret_name = f"{self.settings.gcp_secrets_prefix}-oidc-client-secret"

        # Try GCP
        if self.gcp_secrets_client:
            oidc_secret = await self.get_gcp_secret(secret_name)
            if oidc_secret:
                return oidc_secret

        # Fallback to AWS
        if self.settings.aws_access_key_id:
            return await self.get_aws_secret("oidc-client-secret")

        # Fallback to environment variable
        return self.settings.oidc_client_secret
