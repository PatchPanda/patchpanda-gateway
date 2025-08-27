"""PatchPanda Gateway settings configuration."""

import os
from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Application
    debug: bool = Field(default=False, json_schema_extra={"env": "DEBUG"})
    app_name: str = Field(default="PatchPanda Gateway", json_schema_extra={"env": "APP_NAME"})

    # Server
    host: str = Field(default="0.0.0.0", json_schema_extra={"env": "HOST"})
    port: int = Field(default=8000, json_schema_extra={"env": "PORT"})

    # CORS
    allowed_origins: List[str] = Field(default=["*"], json_schema_extra={"env": "ALLOWED_ORIGINS"})

    # Database
    database_url: str = Field(default="postgresql://user:pass@localhost/patchpanda_gateway", json_schema_extra={"env": "DATABASE_URL"})
    database_echo: bool = Field(default=False, json_schema_extra={"env": "DATABASE_ECHO"})

    # Redis
    redis_url: str = Field(default="redis://localhost:6379", json_schema_extra={"env": "REDIS_URL"})

    # AWS
    aws_region: str = Field(default="us-east-1", json_schema_extra={"env": "AWS_REGION"})
    aws_access_key_id: str = Field(default="", json_schema_extra={"env": "AWS_ACCESS_KEY_ID"})
    aws_secret_access_key: str = Field(default="", json_schema_extra={"env": "AWS_SECRET_ACCESS_KEY"})

    # GitHub App
    github_app_id: str = Field(default="", json_schema_extra={"env": "GITHUB_APP_ID"})
    github_app_private_key: str = Field(default="", json_schema_extra={"env": "GITHUB_APP_PRIVATE_KEY"})
    github_webhook_secret: str = Field(default="", json_schema_extra={"env": "GITHUB_WEBHOOK_SECRET"})

    # Development
    ngrok_url: str = Field(default="", json_schema_extra={"env": "NGROK_URL"})

    # Queue
    queue_backend: str = Field(default="redis", json_schema_extra={"env": "QUEUE_BACKEND"})
    sqs_queue_url: str = Field(default="", json_schema_extra={"env": "SQS_QUEUE_URL"})

    # Security
    secret_key: str = Field(default="dev-secret-key-change-in-production", json_schema_extra={"env": "SECRET_KEY"})
    algorithm: str = Field(default="HS256", json_schema_extra={"env": "ALGORITHM"})
    access_token_expire_minutes: int = Field(default=30, json_schema_extra={"env": "ACCESS_TOKEN_EXPIRE_MINUTES"})

    # OIDC
    oidc_issuer_url: str = Field(default="", json_schema_extra={"env": "OIDC_ISSUER_URL"})
    oidc_client_id: str = Field(default="", json_schema_extra={"env": "OIDC_CLIENT_ID"})
    oidc_client_secret: str = Field(default="", json_schema_extra={"env": "OIDC_CLIENT_SECRET"})

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
