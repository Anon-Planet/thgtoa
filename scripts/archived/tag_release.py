#!/usr/bin/env python3
"""Release tagging helper for Anonymous Planet maintainers.

Creates a GPG-signed annotated git tag using the release key, with a
message derived from the changelog entry for that version.

Usage:
  python scripts/tag_release.py                  # auto-detect next version
  python scripts/tag_release.py --version v1.2.4
  python scripts/tag_release.py --version v1.2.4 --key <fingerprint>
  python scripts/tag_release.py --version v1.2.4 --dry-run

What it does:
  1. Checks the working tree is clean and the branch is main
  2. Resolves the version (auto-increments patch if not given)
  3. Finds the matching ## [vX.Y.Z] entry in the changelog
  4. Lists available signing keys and selects the release key
  5. Creates a signed annotated tag: git tag -s vX.Y.Z -u <key> -m <message>
  6. Verifies the tag signature
  7. Prints the push command

Requirements:
  - git
  - GPG with the release signing key imported
"""

# The Hitchhiker's Guide to Online Anonymity © 2026 by Anonymous Planet is licensed under Creative
# Commons Attribution-NonCommercial 4.0 International

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


# Default release signing key fingerprint.
# Maintainers with a different key can pass --key on the CLI.
DEFAULT_SIGNING_KEY = "C3023DBEA3FB38C438BA1EEDCEC60AEDE8B992A2"

CHANGELOG = Path(__file__).resolve().parent.parent / "docs" / "changelog" / "index.md"


# --------------------------------------------------------------------------- #
#  Helpers
# --------------------------------------------------------------------------- #

def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def git(*args: str, check: bool = True) -> str:
    return run(["git", *args], check=check).stdout.strip()


def check_gpg_installed() -> bool:
    try:
        return run(["gpg", "--version"], check=False).returncode == 0
    except FileNotFoundError:
        return False


# --------------------------------------------------------------------------- #
#  Git state checks
# --------------------------------------------------------------------------- #

def check_clean_tree() -> bool:
    """Return True if the working tree and index are clean."""
    status = git("status", "--porcelain")
    return status == ""


def current_branch() -> str:
    return git("rev-parse", "--abbrev-ref", "HEAD")


def latest_tag() -> str | None:
    """Return the most recent vX.Y.Z tag, or None."""
    out = run(["git", "tag", "--sort=-version:refname", "--list", "v*"], check=False).stdout
    for line in out.splitlines():
        if re.match(r"^v\d+\.\d+\.\d+", line.strip()):
            return line.strip()
    return None


def tag_exists(version: str) -> bool:
    out = run(["git", "tag", "--list", version], check=False).stdout.strip()
    return bool(out)


def head_sha() -> str:
    return git("rev-parse", "HEAD")


def short_sha() -> str:
    return git("rev-parse", "--short", "HEAD")


# --------------------------------------------------------------------------- #
#  Version logic
# --------------------------------------------------------------------------- #

def auto_increment(tag: str | None) -> str:
    """Bump the patch number of tag, or return v1.0.0 if no tag exists."""
    if not tag:
        return "v1.0.0"
    m = re.match(r"^v?(\d+)\.(\d+)\.(\d+)", tag)
    if not m:
        return "v1.0.0"
    return f"v{m.group(1)}.{m.group(2)}.{int(m.group(3)) + 1}"


def normalise_version(v: str) -> str:
    return v if v.startswith("v") else f"v{v}"


# --------------------------------------------------------------------------- #
#  Changelog parsing
# --------------------------------------------------------------------------- #

def extract_changelog_entry(version: str) -> str | None:
    """Return the raw text of the ## [version] section, or None if not found."""
    if not CHANGELOG.exists():
        return None

    content = CHANGELOG.read_text(encoding="utf-8")
    # Find the heading for this version
    pattern = re.compile(
        rf"^(## \[{re.escape(version)}\].*?)(?=^## \[|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    m = pattern.search(content)
    if not m:
        return None
    return m.group(1).strip()


def changelog_to_tag_message(version: str, entry: str | None, sha: str) -> str:
    """Convert a changelog entry into a clean tag message."""
    if not entry:
        return f"{version}\n\nNo changelog entry found for {version}.\nCommit: {sha}"

    lines = []
    current_bucket = None

    for line in entry.splitlines():
        # Skip the ## [vX.Y.Z] heading — we'll add our own first line
        if re.match(r"^## \[", line):
            continue
        # Skip admonition headers like !!! Note "Added" → use bucket name as section
        m = re.match(r'^!!!\s+\w+\s+"(.+)"', line)
        if m:
            current_bucket = m.group(1)
            lines.append(f"\n{current_bucket}:")
            continue
        # Skip Meta bucket entirely
        if current_bucket == "Meta":
            continue
        # Strip 4-space admonition indent and leading bullet dash
        stripped = re.sub(r"^ {4}", "", line)
        stripped = re.sub(r"^- ", "  - ", stripped)
        # Skip blank lines inside admonitions (keep structure clean)
        if stripped.strip():
            lines.append(stripped)

    body = "\n".join(lines).strip()
    return f"{version}\n\n{body}\n\nCommit: {sha}"


# --------------------------------------------------------------------------- #
#  GPG key selection
# --------------------------------------------------------------------------- #

def list_secret_keys() -> list[dict]:
    """Return a list of available secret keys with fingerprint and uid."""
    result = run(["gpg", "--list-secret-keys", "--with-colons"], check=False)
    keys = []
    current: dict = {}
    for line in result.stdout.splitlines():
        parts = line.split(":")
        if parts[0] == "sec":
            if current:
                keys.append(current)
            current = {"fingerprint": None, "uid": None, "key_id": parts[4] if len(parts) > 4 else ""}
        elif parts[0] == "fpr" and current is not None:
            if not current.get("fingerprint"):
                current["fingerprint"] = parts[9] if len(parts) > 9 else ""
        elif parts[0] == "uid" and current is not None:
            if not current.get("uid"):
                current["uid"] = parts[9] if len(parts) > 9 else ""
    if current:
        keys.append(current)
    return keys


def resolve_signing_key(preferred: str) -> str | None:
    """
    Return the fingerprint to use for signing.
    Prefers the key matching `preferred` (full fingerprint or key ID suffix).
    Falls back to interactive selection if not found.
    """
    keys = list_secret_keys()
    if not keys:
        return None

    # Try to match preferred fingerprint/key ID
    preferred_upper = preferred.upper()
    for k in keys:
        fp = (k.get("fingerprint") or "").upper()
        kid = (k.get("key_id") or "").upper()
        if preferred_upper in (fp, kid) or fp.endswith(preferred_upper) or kid.endswith(preferred_upper):
            return k["fingerprint"]

    # Not found — show what's available and ask
    print("\n⚠  Preferred key not found in keyring. Available keys:\n")
    for i, k in enumerate(keys, 1):
        print(f"  {i}.  {k.get('fingerprint', 'N/A')}")
        print(f"       {k.get('uid', 'Unknown')}\n")

    try:
        choice = input(f"Select key (1–{len(keys)}) or press Enter to abort: ").strip()
        if not choice:
            return None
        idx = int(choice) - 1
        if 0 <= idx < len(keys):
            return keys[idx]["fingerprint"]
    except (ValueError, EOFError):
        pass

    return None


# --------------------------------------------------------------------------- #
#  Tag creation and verification
# --------------------------------------------------------------------------- #

def create_signed_tag(version: str, key_fingerprint: str, message: str, dry_run: bool) -> bool:
    """Create a GPG-signed annotated tag. Returns True on success."""
    sha = head_sha()
    cmd = [
        "git", "tag",
        "-s", version,
        sha,
        "-u", key_fingerprint,
        "-m", message,
    ]

    print(f"\n{'─' * 70}")
    print(f"  Tag:     {version}")
    print(f"  Commit:  {sha[:12]}")
    print(f"  Key:     {key_fingerprint}")
    print(f"{'─' * 70}")
    print("\nTag message:\n")
    for line in message.splitlines():
        print(f"  {line}")
    print()

    if dry_run:
        print("── DRY RUN — tag not created. Remove --dry-run to proceed.\n")
        return True

    confirm = input("Create this tag? [y/N] ").strip().lower()
    if confirm != "y":
        print("Aborted.")
        return False

    result = run(cmd, check=False)
    if result.returncode != 0:
        print(f"\n✗ Tag creation failed:\n{result.stderr}")
        return False

    print(f"\n✓ Tag {version} created.")
    return True


def verify_tag(version: str) -> bool:
    """Verify the GPG signature on the tag."""
    result = run(["git", "tag", "-v", version], check=False)
    output = result.stdout + result.stderr
    if result.returncode == 0:
        print("\n✓ Tag signature verified:")
        for line in output.splitlines():
            if any(k in line for k in ("gpg:", "Primary", "using", "issuer", "Good")):
                print(f"  {line.strip()}")
        return True
    else:
        print(f"\n✗ Tag signature verification failed:\n{output}")
        return False


# --------------------------------------------------------------------------- #
#  Main
# --------------------------------------------------------------------------- #

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Create a GPG-signed release tag from the changelog."
    )
    ap.add_argument(
        "--version", "-v",
        help="Version to tag, e.g. v1.2.4 (default: auto-increment from latest tag)",
    )
    ap.add_argument(
        "--key", "-k",
        default=DEFAULT_SIGNING_KEY,
        help=f"GPG key fingerprint to sign with (default: {DEFAULT_SIGNING_KEY})",
    )
    ap.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Print the tag message and exit without creating the tag",
    )
    args = ap.parse_args()

    root = repo_root()

    print("\n" + "=" * 70)
    print("  RELEASE TAGGER — Anonymous Planet")
    print("=" * 70)

    # 1. GPG available?
    if not check_gpg_installed():
        print("\n✗ GPG is not installed or not in PATH.")
        print("  Install with: sudo apt install gnupg  |  brew install gnupg")
        return 1

    # 2. Working tree clean?
    if not check_clean_tree():
        print("\n✗ Working tree is not clean. Commit or stash changes first.")
        result = run(["git", "status", "--short"], check=False)
        print(result.stdout)
        return 1

    # 3. On main?
    branch = current_branch()
    if branch != "main":
        print(f"\n⚠  You are on branch '{branch}', not 'main'.")
        confirm = input("   Tag anyway? [y/N] ").strip().lower()
        if confirm != "y":
            return 1

    # 4. Resolve version
    last_tag = latest_tag()
    version = normalise_version(args.version) if args.version else auto_increment(last_tag)
    print(f"\n  Latest tag:   {last_tag or '(none)'}")
    print(f"  New version:  {version}")
    print(f"  Branch:       {branch}")
    print(f"  HEAD:         {short_sha()}")

    if tag_exists(version) and not args.dry_run:
        print(f"\n✗ Tag {version} already exists.")
        print("  Use --version to specify a different version, or delete the tag first:")
        print(f"    git tag -d {version}")
        return 1

    # 5. Build tag message from changelog
    entry = extract_changelog_entry(version)
    if not entry:
        print(f"\n⚠  No changelog entry found for {version}.")
        print(f"   Add a '## [{version}]' section to {CHANGELOG.relative_to(root)}")
        print("   and re-run, or proceed with a minimal message.")
        confirm = input("   Proceed with minimal message? [y/N] ").strip().lower()
        if confirm != "y":
            return 1

    message = changelog_to_tag_message(version, entry, head_sha())

    # 6. Resolve signing key
    print(f"\n  Signing key:  {args.key}")
    key = resolve_signing_key(args.key)
    if not key:
        print("\n✗ Could not resolve a signing key. Aborting.")
        print("  Import the release key with:")
        print("    gpg --import pgp/anonymousplanet.asc")
        return 1
    print(f"  Resolved to:  {key}")

    # 7. Create tag
    if not create_signed_tag(version, key, message, args.dry_run):
        return 1

    if args.dry_run:
        return 0

    # 8. Verify
    if not verify_tag(version):
        return 1

    # 9. Push instructions
    print("\n" + "=" * 70)
    print("  ✓ All done. Push the tag with:")
    print(f"\n    git push origin {version}\n")
    print("  The 03-release.yml workflow can then be triggered manually from")
    print("  GitHub Actions to publish the GitHub Release for this tag.")
    print("=" * 70 + "\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
