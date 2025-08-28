#!/usr/bin/env python3
"""
GCP Setup Script for PatchPanda Gateway

This script helps set up and test Google Cloud Platform integration.
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from patchpanda.gateway.settings import get_settings
    from patchpanda.gateway.security.secrets import SecretsManager
except ImportError as e:
    print(f"Error importing PatchPanda modules: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)


def print_header(title: str):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_section(title: str):
    """Print a formatted section."""
    print(f"\n{'-'*40}")
    print(f" {title}")
    print(f"{'-'*40}")


def check_gcp_config() -> Dict[str, Any]:
    """Check GCP configuration from environment."""
    print_section("GCP Configuration Check")

    config = {}
    required_vars = [
        "GCP_PROJECT_ID",
        "GCP_REGION",
        "GCP_LOCATION",
        "GCP_KEY_RING",
        "GCP_CRYPTO_KEY",
        "GCP_SECRETS_PREFIX"
    ]

    for var in required_vars:
        value = os.getenv(var)
        config[var] = value
        status = "✓" if value else "✗"
        print(f"{status} {var}: {value or 'NOT SET'}")

    # Check credentials
    use_default = os.getenv("GCP_USE_DEFAULT_CREDENTIALS", "true").lower() == "true"
    sa_key_path = os.getenv("GCP_SERVICE_ACCOUNT_KEY_PATH")

    config["GCP_USE_DEFAULT_CREDENTIALS"] = use_default
    config["GCP_SERVICE_ACCOUNT_KEY_PATH"] = sa_key_path

    print(f"{'✓' if use_default else '✗'} GCP_USE_DEFAULT_CREDENTIALS: {use_default}")
    print(f"{'✓' if sa_key_path else '✗'} GCP_SERVICE_ACCOUNT_KEY_PATH: {sa_key_path or 'NOT SET'}")

    return config


def check_environment_file():
    """Check if .env file exists and has GCP configuration."""
    print_section("Environment File Check")

    env_file = Path(".env")
    if not env_file.exists():
        print("✗ .env file not found")
        print("  Run: cp env.example .env")
        return False

    env_content = env_file.read_text()
    gcp_vars = [line for line in env_content.split('\n') if line.startswith('GCP_')]

    if not gcp_vars:
        print("✗ No GCP configuration found in .env file")
        print("  Add GCP configuration variables to your .env file")
        return False

    print(f"✓ .env file found with {len(gcp_vars)} GCP variables")
    return True


async def test_gcp_connectivity():
    """Test GCP connectivity and secrets access."""
    print_section("GCP Connectivity Test")

    try:
        settings = get_settings()
        secrets = SecretsManager()

        # Test GCP clients
        if secrets.gcp_secrets_client:
            print("✓ GCP Secret Manager client created successfully")
        else:
            print("✗ Failed to create GCP Secret Manager client")
            return False

        if secrets.gcp_kms_client:
            print("✓ GCP KMS client created successfully")
        else:
            print("✗ Failed to create GCP KMS client")
            return False

        # Test secret access
        print("\nTesting secret access...")

        # Test GitHub private key
        private_key = await secrets.get_github_private_key()
        if private_key:
            print("✓ GitHub private key loaded successfully")
        else:
            print("✗ Failed to load GitHub private key")
            print("  Make sure the secret 'patchpanda-github-private-key' exists in GCP Secret Manager")

        # Test webhook secret
        webhook_secret = await secrets.get_webhook_secret()
        if webhook_secret:
            print("✓ Webhook secret loaded successfully")
        else:
            print("✗ Failed to load webhook secret")
            print("  Make sure the secret 'patchpanda-webhook-secret' exists in GCP Secret Manager")

        return True

    except Exception as e:
        print(f"✗ Error testing GCP connectivity: {e}")
        return False


def generate_env_template():
    """Generate a template .env file with GCP configuration."""
    print_section("Environment File Template")

    template = """# Application Settings
DEBUG=false
APP_NAME=PatchPanda Gateway
HOST=0.0.0.0
PORT=8000

# CORS
ALLOWED_ORIGINS=["*"]

# Database
DATABASE_URL=postgresql://user:password@localhost/patchpanda_gateway
DATABASE_ECHO=false

# Redis
REDIS_URL=redis://localhost:6379

# AWS (can be commented out when using GCP)
# AWS_REGION=us-east-1
# AWS_ACCESS_KEY_ID=your_access_key_here
# AWS_SECRET_ACCESS_KEY=your_secret_key_here

# Google Cloud Platform
GCP_PROJECT_ID=patchpanda-1
GCP_REGION=us-central1
GCP_LOCATION=us-central1
GCP_KEY_RING=patchpanda-keys
GCP_CRYPTO_KEY=patchpanda-crypto-key
GCP_SECRETS_PREFIX=patchpanda
GCP_USE_DEFAULT_CREDENTIALS=false
GCP_SERVICE_ACCOUNT_KEY_PATH=/path/to/service-account-key.json

# GitHub App
GITHUB_APP_ID=your_github_app_id
GITHUB_APP_PRIVATE_KEY=your_private_key_here
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here

# Development
NGROK_URL=https://your-ngrok-url.ngrok-free.app

# Queue
QUEUE_BACKEND=redis
SQS_QUEUE_URL=your_sqs_queue_url_here

# Security
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OIDC
OIDC_ISSUER_URL=https://your-oidc-provider.com
OIDC_CLIENT_ID=your_oidc_client_id
OIDC_CLIENT_SECRET=your_oidc_client_secret
"""

    env_file = Path(".env")
    if env_file.exists():
        print("✓ .env file already exists")
        print("  Update it with the GCP configuration above")
    else:
        env_file.write_text(template)
        print("✓ Created .env file with GCP configuration template")
        print("  Update the GCP_PROJECT_ID and other values as needed")


def print_next_steps():
    """Print next steps for the user."""
    print_section("Next Steps")

    print("1. Set up your GCP project and enable required APIs")
    print("   See: docs/gcp-setup.md")

    print("\n2. Create a service account and download the key")
    print("   gcloud iam service-accounts create patchpanda-gateway-sa")
    print("   gcloud iam service-accounts keys create ~/key.json --iam-account=...")

    print("\n3. Create KMS keyring and crypto key")
    print("   gcloud kms keyrings create patchpanda-keys --location=us-central1")
    print("   gcloud kms keys create patchpanda-crypto-key --keyring=patchpanda-keys --location=us-central1")

    print("\n4. Create secrets in Secret Manager")
    print("   gcloud secrets create patchpanda-github-private-key")
    print("   gcloud secrets create patchpanda-webhook-secret")

    print("\n5. Update your .env file with the correct values")

    print("\n6. Test the setup:")
    print("   python scripts/setup_gcp.py")


async def main():
    """Main function."""
    print_header("PatchPanda Gateway - GCP Setup Script")

    # Check environment file
    env_ok = check_environment_file()

    # Check GCP configuration
    config = check_gcp_config()

    # Generate env template if needed
    if not env_ok:
        generate_env_template()

    # Test connectivity if GCP is configured
    if config.get("GCP_PROJECT_ID"):
        print("\nTesting GCP connectivity...")
        connectivity_ok = await test_gcp_connectivity()

        if connectivity_ok:
            print("\n🎉 GCP setup is working correctly!")
        else:
            print("\n❌ GCP setup has issues. Check the errors above.")
    else:
        print("\n⚠️  GCP_PROJECT_ID not set. Please configure GCP settings first.")

    # Print next steps
    print_next_steps()


if __name__ == "__main__":
    asyncio.run(main())
