"""Webhook signature verification."""

import hmac
import hashlib
from typing import Union
from ..settings import get_settings


def verify_webhook_signature(
    payload: Union[bytes, str],
    signature_header: str
) -> bool:
    """Verify GitHub webhook signature."""
    settings = get_settings()

    if not signature_header or not signature_header.startswith("sha256="):
        return False

    # Extract signature from header
    expected_signature = signature_header[7:]  # Remove "sha256=" prefix

    # Get webhook secret
    webhook_secret = settings.github_webhook_secret

    if not webhook_secret:
        # TODO: Log warning about missing webhook secret
        return False

    # Convert payload to bytes if it's a string
    if isinstance(payload, str):
        payload_bytes = payload.encode('utf-8')
    else:
        payload_bytes = payload

    # Calculate expected signature
    calculated_signature = hmac.new(
        webhook_secret.encode('utf-8'),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()

    # Compare signatures using constant-time comparison
    return hmac.compare_digest(expected_signature, calculated_signature)


def generate_webhook_signature(payload: Union[bytes, str], secret: str) -> str:
    """Generate webhook signature for testing purposes."""
    if isinstance(payload, str):
        payload_bytes = payload.encode('utf-8')
    else:
        payload_bytes = payload

    signature = hmac.new(
        secret.encode('utf-8'),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()

    return f"sha256={signature}"
