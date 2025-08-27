#!/usr/bin/env python3
"""Test webhook signature verification."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from patchpanda.gateway.security.signature import verify_webhook_signature, generate_webhook_signature


def test_webhook_signature():
    """Test webhook signature verification."""
    print("🔐 Testing Webhook Signature Verification...")

    # Get the actual webhook secret from environment
    from patchpanda.gateway.settings import get_settings
    settings = get_settings()

    if not settings.github_webhook_secret:
        print("❌ No webhook secret found in environment variables")
        print("Please set GITHUB_WEBHOOK_SECRET in your .env file")
        return False

    # Test data
    payload = b'{"test": "data"}'
    secret = settings.github_webhook_secret

    # Generate signature
    signature = generate_webhook_signature(payload, secret)

    print(f"  Payload: {payload}")
    print(f"  Secret: {secret}")
    print(f"  Generated signature: {signature}")

    # Test valid signature
    print("\n  Testing valid signature...")
    if verify_webhook_signature(payload, signature):
        print("  ✅ Valid signature accepted")
    else:
        print("  ❌ Valid signature rejected")
        return False

    # Test invalid signature
    print("\n  Testing invalid signature...")
    invalid_signature = "sha256=invalid_signature"
    if not verify_webhook_signature(payload, invalid_signature):
        print("  ✅ Invalid signature rejected")
    else:
        print("  ❌ Invalid signature accepted")
        return False

    # Test tampered payload
    print("\n  Testing tampered payload...")
    tampered_payload = b'{"test": "tampered"}'
    if not verify_webhook_signature(tampered_payload, signature):
        print("  ✅ Tampered payload rejected")
    else:
        print("  ❌ Tampered payload accepted")
        return False

    print("\n✅ All webhook signature tests passed!")
    return True


def main():
    """Main function."""
    try:
        success = test_webhook_signature()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
