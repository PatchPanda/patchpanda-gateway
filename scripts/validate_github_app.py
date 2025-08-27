#!/usr/bin/env python3
"""Validate GitHub App configuration and test basic functionality."""

import os
import sys
import asyncio
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from patchpanda.gateway.services.github_app import GitHubAppService
from patchpanda.gateway.settings import get_settings


async def validate_github_app():
    """Validate GitHub App configuration."""
    print("🔍 Validating GitHub App Configuration...")

    # Check environment variables
    settings = get_settings()

    print("\n📋 Environment Variables:")
    print(f"  GITHUB_APP_ID: {'✅ Set' if settings.github_app_id else '❌ Missing'}")
    print(f"  GITHUB_APP_PRIVATE_KEY: {'✅ Set' if settings.github_app_private_key else '❌ Missing'}")
    print(f"  GITHUB_WEBHOOK_SECRET: {'✅ Set' if settings.github_webhook_secret else '❌ Missing'}")

    if not all([settings.github_app_id, settings.github_app_private_key, settings.github_webhook_secret]):
        print("\n❌ Missing required environment variables!")
        print("Please set the missing variables in your .env file.")
        return False

    # Test GitHub App service
    print("\n🔧 Testing GitHub App Service:")
    try:
        github_service = GitHubAppService()

        # Test JWT generation
        print("  Testing JWT generation...")
        jwt_token = github_service.generate_jwt()
        if jwt_token:
            print("  ✅ JWT generation successful")
        else:
            print("  ❌ JWT generation failed")
            return False

        # Test private key format
        print("  Testing private key format...")
        private_key = github_service.private_key
        if private_key.startswith("-----BEGIN RSA PRIVATE KEY-----"):
            print("  ✅ Private key format correct")
        else:
            print("  ❌ Private key format incorrect")
            return False

    except Exception as e:
        print(f"  ❌ GitHub App service error: {e}")
        return False

    print("\n✅ GitHub App configuration is valid!")
    print("\n📝 Next steps:")
    print("  1. Create the GitHub App in GitHub Developer Settings")
    print("  2. Configure the required permissions and webhook events")
    print("  3. Install the app on your target repository")
    print("  4. Test webhook delivery")

    return True


def main():
    """Main function."""
    try:
        success = asyncio.run(validate_github_app())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
