#!/usr/bin/env python3
"""Verification script for PDF files.

This script verifies:
1. SHA256 hash integrity of PDF files
2. GPG signature authenticity
3. VirusTotal scan status (optional)

Usage:
  python scripts/verify_pdf.py --all                    # Verify everything
  python scripts/verify_pdf.py --hashes                 # Only verify hashes
  python scripts/verify_pdf.py --signatures             # Only verify signatures
  python scripts/verify_pdf.py --vt                     # Check VT status (requires API key)

Examples:
  python scripts/verify_pdf.py --all
  python scripts/verify_pdf.py --hashes --file export/thgtoa.pdf
"""

from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys
from pathlib import Path

def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent

def calculate_sha256(file_path: Path) -> str:
    """Calculate SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def verify_hash(file_path: Path, expected_hash: str) -> bool:
    """Verify file hash against expected value."""
    actual_hash = calculate_sha256(file_path)
    is_valid = actual_hash == expected_hash
    status = "✓ PASS" if is_valid else "✗ FAIL"
    print(f"{status}: {file_path.name}")
    print(f"  Expected: {expected_hash}")
    print(f"  Actual:   {actual_hash}")
    return is_valid

def verify_signature(file_path: Path, sig_file: Path) -> bool:
    """Verify GPG signature of a file."""
    if not sig_file.exists():
        print(f"✗ FAIL: Signature file not found: {sig_file}")
        return False

    try:
        result = subprocess.run(
            ["gpg", "--verify", str(sig_file), str(file_path)],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            print(f"✓ PASS: {file_path.name} signature verified")
            # Extract key info from GPG output
            for line in result.stdout.split('\n'):
                if 'Good signature' in line or 'key ID' in line.lower():
                    print(f"  {line.strip()}")
            return True
        else:
            print(f"✗ FAIL: {file_path.name} signature verification failed")
            print(f"  Error: {result.stderr}")
            return False

    except FileNotFoundError:
        print("⚠ WARNING: GPG not installed. Skipping signature verification.")
        return None

def verify_from_hash_file(file_path: Path, hash_file: Path) -> bool:
    """Verify file hash from a hash file."""
    if not hash_file.exists():
        print(f"✗ FAIL: Hash file not found: {hash_file}")
        return False

    expected_hash = None
    with open(hash_file, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 2 and parts[1] == str(file_path):
                expected_hash = parts[0]
                break

    if not expected_hash:
        print(f"✗ FAIL: Hash not found in {hash_file.name} for {file_path.name}")
        return False

    return verify_hash(file_path, expected_hash)

def check_virustotal(file_hash: str, api_key: str | None = None) -> dict | None:
    """Check VirusTotal scan status for a file hash."""
    if not api_key:
        print("⚠ WARNING: VT_API_KEY not set. Skipping VirusTotal check.")
        return None

    try:
        import urllib.request
        import json

        url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
        request = urllib.request.Request(url, headers={"x-apikey": api_key})

        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode())

            stats = data.get('data', {}).get('attributes', {}).get('last_analysis_stats', {})
            total = sum(stats.values()) if stats else 0

            print(f"\n🦠 VirusTotal Results for {file_hash[:16]}...")
            print(f"  Total scans: {total}")

            if stats:
                print(f"  Malicious:    {stats.get('malicious', 0)}")
            print(f"  Suspicious:   {stats.get('suspicious', 0)}")
            print(f"  Undetected:   {stats.get('undetected', 0)}")
            print(f"  Clean:        {stats.get('harmless', 0)}")

            return data

    except Exception as e:
        print(f"⚠ ERROR checking VirusTotal: {e}")
        return None

def main() -> int:
    root = repo_root()
    ap = argparse.ArgumentParser(description="Verify PDF files (hashes, signatures, VT).")

    # File paths
    ap.add_argument(
        "--light-pdf",
        type=Path,
        default=root / "export" / "thgtoa.pdf",
        help="Light mode PDF file",
    )
    ap.add_argument(
        "--dark-pdf",
        type=Path,
        default=root / "export" / "thgtoa-dark.pdf",
        help="Dark mode PDF file",
    )
    ap.add_argument(
        "--hash-file",
        type=Path,
        default=root / "export" / "thgtoa.pdf.sha256",
        help="Hash file to verify against",
    )

    # Verification modes
    group = ap.add_mutually_exclusive_group()
    group.add_argument("--all", action="store_true", help="Verify everything")
    group.add_argument("--hashes", action="store_true", help="Only verify hashes")
    group.add_argument("--signatures", action="store_true", help="Only verify signatures")
    ap.add_argument("--vt", action="store_true", help="Check VirusTotal status")

    args = ap.parse_args()

    # Determine what to verify
    if not any([args.all, args.hashes, args.signatures, args.vt]):
        args.all = True

    all_passed = True

    pdf_files = [
        ("Light", args.light_pdf),
        ("Dark", args.dark_pdf),
    ]

    for mode_name, pdf_file in pdf_files:
        if not pdf_file.exists():
            print(f"⚠ WARNING: {pdf_file.name} not found. Skipping.")
            continue

        print(f"\n{'='*60}")
        print(f"Verifying {mode_name} PDF: {pdf_file.name}")
        print('='*60)

        # Verify hash if requested
        if args.all or args.hashes:
            if not verify_from_hash_file(pdf_file, args.hash_file):
                all_passed = False

        # Verify signature if requested
        if args.all or args.signatures:
            sig_file = pdf_file.with_suffix(pdf_file.suffix + ".sig")
            result = verify_signature(pdf_file, sig_file)
            if result is False:  # None means skipped (GPG not installed)
                all_passed = False

        # Check VirusTotal if requested
        if args.all or args.vt:
            file_hash = calculate_sha256(pdf_file)
            api_key = os.environ.get("VT_API_KEY")
            check_virustotal(file_hash, api_key)

    print(f"\n{'='*60}")
    if all_passed:
        print("✓ All verifications PASSED")
        return 0
    else:
        print("✗ Some verifications FAILED")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
