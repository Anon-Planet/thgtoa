#!/usr/bin/env python3
"""Setup helper for PDF workflow configuration.

This script helps you configure the necessary GitHub Secrets for the automated
PDF build, signing, and VirusTotal scanning workflows.

Usage:
  python scripts/setup_workflow.py

Requirements:
  - Python 3.8+
  - GPG installed (for key export)
  - Access to GitHub repository settings

What it does:
  1. Validates your GPG key setup
  2. Exports the public key for verification
  3. Provides instructions for adding secrets to GitHub
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def check_gpg_installed() -> bool:
    """Check if GPG is installed and accessible."""
    try:
        result = subprocess.run(
            ["gpg", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def list_gpg_keys() -> list[dict]:
    """List all GPG keys in the keyring."""
    try:
        result = subprocess.run(
            ["gpg", "--list-keys", "--with-colons"],
            capture_output=True,
            text=True,
            check=True,
        )

        keys = []
        current_key = {}

        for line in result.stdout.split('\n'):
            if line.startswith('pub:'):
                if current_key:
                    keys.append(current_key)
                parts = line.split(':')
                current_key = {
                    'type': parts[1],
                    'key_id': parts[4],
                    'fingerprint': parts[9] if len(parts) > 9 else None,
                    'created': parts[5],
                    'expires': parts[6],
                    'uid': None,
                }
            elif line.startswith('uid:'):
                parts = line.split(':')
                current_key['uid'] = parts[9] if len(parts) > 9 else None

        if current_key:
            keys.append(current_key)

        return keys

    except subprocess.CalledProcessError as e:
        print(f"Error listing GPG keys: {e}")
        return []


def export_public_key(key_id: str, output_file: Path | None = None) -> str | None:
    """Export a public key in ASCII armor format."""
    try:
        result = subprocess.run(
            ["gpg", "--armor", "--export", key_id],
            capture_output=True,
            text=True,
            check=True,
        )

        if output_file:
            output_file.write_text(result.stdout)
            print(f"✓ Public key exported to {output_file}")

        return result.stdout

    except subprocess.CalledProcessError as e:
        print(f"Error exporting public key: {e}")
        return None


def export_private_key(key_id: str, output_file: Path | None = None) -> str | None:
    """Export a private key in ASCII armor format (requires passphrase)."""
    try:
        # This will prompt for passphrase interactively
        result = subprocess.run(
            ["gpg", "--armor", "--export-secret-keys", key_id],
            capture_output=True,
            text=True,
            check=True,
        )

        if output_file:
            output_file.write_text(result.stdout)
            print(f"✓ Private key exported to {output_file}")

        return result.stdout

    except subprocess.CalledProcessError as e:
        print(f"Error exporting private key: {e}")
        return None


def validate_gpg_key(key_id: str) -> bool:
    """Validate that a GPG key has signing capability."""
    try:
        result = subprocess.run(
            ["gpg", "--list-keys", "--with-colons", key_id],
            capture_output=True,
            text=True,
            check=True,
        )

        # Check for 's' (signing) in the pub line
        for line in result.stdout.split('\n'):
            if line.startswith('pub:'):
                flags = line.split(':')[1]
                return 's' in flags

        return False

    except subprocess.CalledProcessError:
        return False


def print_setup_instructions():
    """Print instructions for configuring GitHub Secrets."""
    print("\n" + "="*70)
    print("GITHUB SECRETS SETUP INSTRUCTIONS")
    print("="*70)

    print("""
To enable the automated PDF workflow, you need to add three secrets to your
GitHub repository:

1. GPG_PRIVATE_KEY
   - Your GPG private key in ASCII armor format
   - Used to sign PDFs and hash files
   - IMPORTANT: Keep this secret! Never commit it publicly

2. GPG_PASSPHRASE
   - The passphrase for your GPG private key
   - Required to unlock the private key for signing

3. VT_API_KEY (optional but recommended)
   - VirusTotal API key for malware scanning

TROUBLESHOOTING:

- If GPG signing fails: Check that your key has signing capability ('s' flag)
- If passphrase is wrong: Verify you're using the correct passphrase
- If VT scan fails: Ensure API key is valid and within rate limits
""")


def main() -> int:
    print("\n" + "="*70)
    print("PDF WORKFLOW SETUP HELPER")
    print("="*70)

    # Check GPG installation
    if not check_gpg_installed():
        print("⚠ WARNING: GPG is not installed or not in PATH")
        print("Please install GPG before continuing:")
        print("  - Linux: sudo apt install gnupg")
        print("\nContinuing anyway...")

    # List available keys
    print("\n🔑 Available GPG Keys:")
    print("-" * 70)

    keys = list_gpg_keys()

    if not keys:
        print("No GPG keys found in your keyring.")
        print("Generate a key with: gpg --full-generate-key")
        return 1

    for i, key in enumerate(keys, 1):
        status = "✓" if validate_gpg_key(key['key_id']) else "✗"
        print(f"\n{i}. {status} Key ID: {key['key_id']}")
        print(f"   Fingerprint: {key.get('fingerprint', 'N/A')}")
        print(f"   UID: {key.get('uid', 'Unknown')}")
        print(f"   Created: {key.get('created', 'Unknown')}")

        if key.get('expires'):
            print(f"   Expires: {key['expires']}")

    # Ask user to select key
    print("\n" + "-" * 70)
    try:
        choice = input("\nEnter the number of the key you want to use (1-{}): ".format(len(keys)))
        selected_index = int(choice) - 1

        if not (0 <= selected_index < len(keys)):
            print("Invalid selection!")
            return 1

    except ValueError:
        print("Invalid input! Please enter a number.")
        return 1

    selected_key = keys[selected_index]

    # Validate key has signing capability
    if not validate_gpg_key(selected_key['key_id']):
        print(f"\n⚠ WARNING: Selected key does not have signing capability!")
        print("You need a key with 's' (signing) flag for PDF signatures.")
        confirm = input("Continue anyway? (y/N): ")
        if confirm.lower() != 'y':
            return 1

    # Export public key
    print(f"\n📤 Exporting public key for {selected_key['uid']}...")
    public_key_file = repo_root() / "pgp" / "workflow-public.asc"

    public_key = export_public_key(selected_key['key_id'], public_key_file)

    if not public_key:
        print("Failed to export public key!")
        return 1

    # Show public key info
    print("\n✓ Public Key Information:")
    print("-" * 70)
    for line in public_key.split('\n')[:5]:
        print(line)
    print("...")

    # Instructions for private key export
    print("\n🔐 Private Key Export:")
    print("-" * 70)
    print("""
To get your private key for the GPG_PRIVATE_KEY secret:

1. Run this command (you'll be prompted for passphrase):
   gpg --armor --export-secret-keys {} > workflow-private.asc

2. Copy the ENTIRE output including BEGIN and END lines

3. Add it to GitHub Secrets as 'GPG_PRIVATE_KEY'

⚠ IMPORTANT: Keep your private key secure! Never commit it publicly.
""".format(selected_key['key_id']))

    # Print setup instructions
    print_setup_instructions()

    print("\n" + "="*70)
    print("SETUP COMPLETE!")
    print("="*70)
    print(f"\nPublic key saved to: {public_key_file}")
    print("Next steps:")
    print("1. Export your private key (see instructions above)")
    print("2. Add all three secrets to GitHub repository settings")
    print("3. Test the workflow by triggering a manual build")
    print("\nFor more information, see: docs/guide/dev-workflow.md\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
