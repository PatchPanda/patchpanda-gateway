#!/usr/bin/env python3
"""
AWS to GCP Migration Script for PatchPanda Gateway

This script helps migrate secrets from AWS to GCP.
"""

import os
import sys
import json
import asyncio
import boto3
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from patchpanda.gateway.settings import get_settings
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


def check_aws_config() -> bool:
    """Check if AWS configuration is available."""
    print_section("AWS Configuration Check")

    aws_vars = [
        "AWS_REGION",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY"
    ]

    aws_configured = True
    for var in aws_vars:
        value = os.getenv(var)
        status = "✓" if value else "✗"
        print(f"{status} {var}: {value or 'NOT SET'}")
        if not value:
            aws_configured = False

    return aws_configured


def check_gcp_config() -> bool:
    """Check if GCP configuration is available."""
    print_section("GCP Configuration Check")

    gcp_vars = [
        "GCP_PROJECT_ID",
        "GCP_REGION",
        "GCP_LOCATION"
    ]

    gcp_configured = True
    for var in gcp_vars:
        value = os.getenv(var)
        status = "✓" if value else "✗"
        print(f"{status} {var}: {value or 'NOT SET'}")
        if not value:
            gcp_configured = False

    return gcp_configured


def get_aws_secrets() -> Dict[str, str]:
    """Retrieve secrets from AWS Secrets Manager."""
    print_section("Retrieving AWS Secrets")

    try:
        # Initialize AWS clients
        session = boto3.Session(
            region_name=os.getenv("AWS_REGION"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )

        secrets_client = session.client('secretsmanager')

        # List all secrets
        response = secrets_client.list_secrets()
        secrets = {}

        for secret in response['SecretList']:
            secret_name = secret['Name']
            try:
                # Get secret value
                secret_response = secrets_client.get_secret_value(SecretId=secret_name)
                if 'SecretString' in secret_response:
                    secrets[secret_name] = secret_response['SecretString']
                    print(f"✓ Retrieved: {secret_name}")
                else:
                    print(f"⚠ Binary secret (skipping): {secret_name}")
            except Exception as e:
                print(f"✗ Failed to retrieve {secret_name}: {e}")

        return secrets

    except Exception as e:
        print(f"✗ Error connecting to AWS: {e}")
        return {}


def create_gcp_secrets(secrets: Dict[str, str]) -> bool:
    """Create secrets in GCP Secret Manager."""
    print_section("Creating GCP Secrets")

    try:
        from google.cloud import secretmanager

        # Initialize GCP client
        client = secretmanager.SecretManagerServiceClient()
        project_id = os.getenv("GCP_PROJECT_ID")

        if not project_id:
            print("✗ GCP_PROJECT_ID not set")
            return False

        created_count = 0
        for secret_name, secret_value in secrets.items():
            try:
                # Create secret
                parent = f"projects/{project_id}"
                secret_id = secret_name

                # Check if secret already exists
                try:
                    secret_path = client.secret_path(project_id, secret_id)
                    client.get_secret(request={"name": secret_path})
                    print(f"⚠ Secret already exists: {secret_id}")
                    continue
                except Exception:
                    # Secret doesn't exist, create it
                    pass

                secret = client.create_secret(
                    request={
                        "parent": parent,
                        "secret_id": secret_id,
                        "secret": {"replication": {"automatic": {}}}
                    }
                )

                # Add secret version
                client.add_secret_version(
                    request={
                        "parent": secret.name,
                        "payload": {"data": secret_value.encode("UTF-8")}
                    }
                )

                print(f"✓ Created: {secret_id}")
                created_count += 1

            except Exception as e:
                print(f"✗ Failed to create {secret_name}: {e}")

        print(f"\nCreated {created_count} out of {len(secrets)} secrets")
        return created_count > 0

    except ImportError:
        print("✗ Google Cloud Secret Manager not available")
        print("  Install: pip install google-cloud-secret-manager")
        return False
    except Exception as e:
        print(f"✗ Error creating GCP secrets: {e}")
        return False


def update_env_file():
    """Update .env file to use GCP instead of AWS."""
    print_section("Updating Environment Configuration")

    env_file = Path(".env")
    if not env_file.exists():
        print("✗ .env file not found")
        print("  Run: cp env.example .env first")
        return False

    try:
        # Read current content
        content = env_file.read_text()

        # Comment out AWS variables
        aws_vars = [
            "AWS_REGION",
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY"
        ]

        for var in aws_vars:
            content = content.replace(f"{var}=", f"# {var}=")

        # Ensure GCP variables are uncommented
        gcp_vars = [
            "GCP_PROJECT_ID",
            "GCP_REGION",
            "GCP_LOCATION",
            "GCP_KEY_RING",
            "GCP_CRYPTO_KEY",
            "GCP_SECRETS_PREFIX",
            "GCP_USE_DEFAULT_CREDENTIALS",
            "GCP_SERVICE_ACCOUNT_KEY_PATH"
        ]

        for var in gcp_vars:
            if f"# {var}=" in content:
                content = content.replace(f"# {var}=", f"{var}=")

        # Write updated content
        env_file.write_text(content)
        print("✓ Updated .env file to use GCP configuration")
        print("  AWS variables have been commented out")

        return True

    except Exception as e:
        print(f"✗ Error updating .env file: {e}")
        return False


def print_migration_summary(secrets: Dict[str, str], gcp_created: bool):
    """Print migration summary."""
    print_section("Migration Summary")

    print(f"Secrets found in AWS: {len(secrets)}")
    if secrets:
        for name in secrets.keys():
            print(f"  - {name}")

    if gcp_created:
        print(f"\n✅ Migration completed successfully!")
        print("  Your secrets are now stored in GCP Secret Manager")
        print("  AWS configuration has been commented out in .env")
    else:
        print(f"\n❌ Migration failed or incomplete")
        print("  Check the errors above and try again")

    print("\nNext steps:")
    print("1. Verify secrets in GCP Secret Manager")
    print("2. Test your application with GCP configuration")
    print("3. Remove AWS credentials when no longer needed")


async def main():
    """Main migration function."""
    print_header("AWS to GCP Migration Script")

    # Check configurations
    aws_ok = check_aws_config()
    gcp_ok = check_gcp_config()

    if not aws_ok:
        print("\n❌ AWS configuration incomplete")
        print("  Please set AWS_REGION, AWS_ACCESS_KEY_ID, and AWS_SECRET_ACCESS_KEY")
        return

    if not gcp_ok:
        print("\n❌ GCP configuration incomplete")
        print("  Please set GCP_PROJECT_ID, GCP_REGION, and GCP_LOCATION")
        print("  See: docs/gcp-setup.md")
        return

    # Retrieve AWS secrets
    secrets = get_aws_secrets()
    if not secrets:
        print("\n❌ No secrets found in AWS or failed to retrieve them")
        return

    # Create GCP secrets
    gcp_created = create_gcp_secrets(secrets)

    # Update environment configuration
    env_updated = update_env_file()

    # Print summary
    print_migration_summary(secrets, gcp_created and env_updated)


if __name__ == "__main__":
    asyncio.run(main())
