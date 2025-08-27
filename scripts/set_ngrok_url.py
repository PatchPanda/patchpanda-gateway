#!/usr/bin/env python3
"""Set ngrok URL in .env file."""

import os
import sys
from pathlib import Path


def set_ngrok_url():
    """Set ngrok URL in .env file."""
    print("🔗 Setting ngrok URL in .env file...")

    # Get current directory
    current_dir = Path(__file__).parent.parent
    env_file = current_dir / ".env"

    # Check if .env file exists
    if not env_file.exists():
        print("❌ .env file not found")
        print("Please create a .env file first (copy from env.example)")
        return False

    # Read current .env content
    try:
        with open(env_file, 'r') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False

    # Check if NGROK_URL already exists
    ngrok_line_index = None
    for i, line in enumerate(lines):
        if line.startswith('NGROK_URL='):
            ngrok_line_index = i
            break

    # Get ngrok URL from user
    print("\n📝 Enter your ngrok URL (e.g., https://abc123.ngrok-free.app):")
    print("   (Press Enter to skip if you want to keep the current value)")

    ngrok_url = input("NGROK_URL: ").strip()

    if not ngrok_url:
        if ngrok_line_index is not None:
            current_value = lines[ngrok_line_index].split('=', 1)[1].strip()
            print(f"✅ Keeping current value: {current_value}")
        else:
            print("⚠️  No ngrok URL provided and none currently set")
        return True

    # Validate URL format
    if not ngrok_url.startswith('https://') or '.ngrok' not in ngrok_url:
        print("⚠️  Warning: URL doesn't look like a typical ngrok URL")
        print("   Expected format: https://abc123.ngrok-free.app")
        confirm = input("   Continue anyway? (y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ Cancelled")
            return False

    # Update or add NGROK_URL
    new_line = f"NGROK_URL={ngrok_url}\n"

    if ngrok_line_index is not None:
        # Update existing line
        old_value = lines[ngrok_line_index].split('=', 1)[1].strip()
        lines[ngrok_line_index] = new_line
        print(f"✅ Updated NGROK_URL: {old_value} → {ngrok_url}")
    else:
        # Add new line after GitHub App section
        insert_index = None
        for i, line in enumerate(lines):
            if line.startswith('# GitHub App'):
                insert_index = i + 3  # After the 3 GitHub App lines
                break

        if insert_index is None:
            # If GitHub App section not found, add at the end
            insert_index = len(lines)

        lines.insert(insert_index, new_line)
        print(f"✅ Added NGROK_URL: {ngrok_url}")

    # Write back to .env file
    try:
        with open(env_file, 'w') as f:
            f.writelines(lines)
        print(f"💾 Saved to {env_file}")
    except Exception as e:
        print(f"❌ Error writing .env file: {e}")
        return False

    print("\n🎉 ngrok URL configured successfully!")
    print(f"   You can now run: make test-github-integration")

    return True


def main():
    """Main function."""
    try:
        success = set_ngrok_url()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
