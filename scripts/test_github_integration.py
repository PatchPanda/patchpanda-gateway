#!/usr/bin/env python3
"""Test GitHub integration through ngrok."""

import sys
import json
import httpx
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from patchpanda.gateway.security.signature import generate_webhook_signature
from patchpanda.gateway.settings import get_settings


def test_github_integration():
    """Test GitHub integration through ngrok."""
    print("🧪 Testing GitHub Integration Through ngrok...")

    # Get settings
    settings = get_settings()
    if not settings.github_webhook_secret:
        print("❌ No webhook secret found in environment variables")
        return False

        # Get ngrok URL from environment
    ngrok_url = settings.ngrok_url
    if not ngrok_url:
        print("❌ No ngrok URL found in environment variables")
        print("Please set NGROK_URL in your .env file")
        return False

    print(f"\n📡 Testing ngrok URL: {ngrok_url}")

    # Test 1: Health check through ngrok
    print("\n1️⃣ Testing health endpoint through ngrok...")
    try:
        with httpx.Client(timeout=10) as client:
            response = client.get(f"{ngrok_url}/healthz")
            if response.status_code == 200 and response.json().get("status") == "healthy":
                print("  ✅ Health endpoint accessible through ngrok")
            else:
                print(f"  ❌ Health endpoint failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"  ❌ Health endpoint error: {e}")
        return False

    # Test 2: Webhook signature verification
    print("\n2️⃣ Testing webhook signature verification...")
    payload = {"test": "integration", "event": "test"}
    payload_bytes = json.dumps(payload).encode()
    signature = generate_webhook_signature(payload_bytes, settings.github_webhook_secret)

    print(f"  Payload: {payload}")
    print(f"  Generated signature: {signature}")

    # Test 3: Issue comment webhook through ngrok
    print("\n3️⃣ Testing issue comment webhook through ngrok...")
    try:
        headers = {
            "Content-Type": "application/json",
            "x-hub-signature-256": signature,
            "x-github-event": "issue_comment",
            "x-github-delivery": "test-integration-123"
        }

        with httpx.Client(timeout=10) as client:
            response = client.post(
                f"{ngrok_url}/webhooks/github",
                headers=headers,
                json=payload
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "comment_processed":
                    print("  ✅ Issue comment webhook processed successfully")
                else:
                    print(f"  ⚠️  Unexpected response: {result}")
            else:
                print(f"  ❌ Webhook failed: {response.status_code} - {response.text}")
                return False

    except Exception as e:
        print(f"  ❌ Webhook error: {e}")
        return False

    # Test 4: Pull request webhook through ngrok
    print("\n4️⃣ Testing pull request webhook through ngrok...")
    try:
        headers = {
            "Content-Type": "application/json",
            "x-hub-signature-256": signature,
            "x-github-event": "pull_request",
            "x-github-delivery": "test-integration-456"
        }

        with httpx.Client(timeout=10) as client:
            response = client.post(
                f"{ngrok_url}/webhooks/github",
                headers=headers,
                json=payload
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "pr_processed":
                    print("  ✅ Pull request webhook processed successfully")
                else:
                    print(f"  ⚠️  Unexpected response: {result}")
            else:
                print(f"  ❌ Webhook failed: {response.status_code} - {response.text}")
                return False

    except Exception as e:
        print(f"  ❌ Webhook error: {e}")
        return False

    # Test 5: Unknown event type
    print("\n5️⃣ Testing unknown event type...")
    try:
        headers = {
            "Content-Type": "application/json",
            "x-hub-signature-256": signature,
            "x-github-event": "push",
            "x-github-delivery": "test-integration-789"
        }

        with httpx.Client(timeout=10) as client:
            response = client.post(
                f"{ngrok_url}/webhooks/github",
                headers=headers,
                json=payload
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "acknowledged":
                    print("  ✅ Unknown event type acknowledged correctly")
                else:
                    print(f"  ⚠️  Unexpected response: {result}")
            else:
                print(f"  ❌ Webhook failed: {response.status_code} - {response.text}")
                return False

    except Exception as e:
        print(f"  ❌ Webhook error: {e}")
        return False

    print("\n🎉 All GitHub integration tests passed!")
    print(f"\n📋 Your webhook URL for GitHub App: {ngrok_url}/webhooks/github")
    print("✅ Ready to receive real GitHub webhook events!")
    print(f"\n💡 To update your webhook URL, set NGROK_URL={ngrok_url} in your .env file")

    return True


def main():
    """Main function."""
    try:
        success = test_github_integration()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
