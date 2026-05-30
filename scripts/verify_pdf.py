#!/usr/bin/env python3
"""Verification script for thgtoa PDF releases.

Verifies SHA-256 hashes, BLAKE2b hashes, and GPG signatures (.asc) for
the light and dark PDFs. Optionally checks VirusTotal scan status.

Usage:
  python scripts/verify_pdf.py
  python scripts/verify_pdf.py --hashes
  python scripts/verify_pdf.py --signatures
  python scripts/verify_pdf.py --vt
  python scripts/verify_pdf.py --file export/thgtoa.pdf --hashes
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _read_bare_hash(hash_file: Path) -> str | None:
    """Read a bare hex digest from a single-value hash file."""
    try:
        return hash_file.read_text(encoding="utf-8").strip().split()[0]
    except (OSError, IndexError):
        return None


def _read_hash_from_sumfile(sum_file: Path, pdf_path: Path) -> str | None:
    """Read a hash from a two-column sumfile (sha256sum / b2sum format).

    Matches on the filename only (not the full path) so the file can be used
    regardless of where the PDFs sit on disk.
    """
    if not sum_file.exists():
        return None
    target = pdf_path.name
    try:
        for line in sum_file.read_text(encoding="utf-8").splitlines():
            parts = line.strip().split(None, 1)
            if len(parts) == 2 and Path(parts[1].lstrip("*")).name == target:
                return parts[0]
    except OSError:
        return None
    return None

# Hash verification

def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _blake2b(path: Path) -> str:
    h = hashlib.blake2b()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_hashes(pdf: Path, export_dir: Path) -> bool:
    """Verify all available hash files for a PDF. Returns True if all pass."""
    stem = pdf.name  # e.g. "thgtoa.pdf" or "thgtoa-dark.pdf"
    results: list[bool] = []

    checks = [
        ("SHA-256", _sha256,  export_dir / f"{stem}.sha256",  export_dir / "sha256sums.txt"),
        ("BLAKE2b", _blake2b, export_dir / f"{stem}.b2sum",   export_dir / "b2sums.txt"),
    ]

    for algo, fn, bare_file, sum_file in checks:
        # Resolve expected hash — prefer bare file, fall back to sumfile
        expected = _read_bare_hash(bare_file) if bare_file.exists() else None
        if expected is None:
            expected = _read_hash_from_sumfile(sum_file, pdf)
        if expected is None:
            print(f"  ⚠  {algo}: no hash file found (checked {bare_file.name}, {sum_file.name})")
            continue

        actual = fn(pdf)
        ok = actual == expected
        results.append(ok)
        mark = "✓" if ok else "✗"
        print(f"  {mark} {algo}")
        if not ok:
            print(f"      expected: {expected}")
            print(f"      actual:   {actual}")

    return all(results) if results else False

# Signature verification

def verify_signature(pdf: Path) -> bool | None:
    """Verify the .asc detached signature for a PDF.

    Returns True on success, False on failure, None if GPG is not installed
    or the signature file is missing.
    """
    sig = pdf.with_suffix(pdf.suffix + ".asc")
    if not sig.exists():
        print(f"  ⚠  Signature file not found: {sig.name}")
        return None

    try:
        result = subprocess.run(
            ["gpg", "--verify", str(sig), str(pdf)],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        print("  ⚠  GPG not installed — skipping signature verification")
        return None

    if result.returncode == 0:
        print(f"  ✓ GPG signature valid")
        # Surface the key info line from stderr (that's where gpg writes it)
        for line in result.stderr.splitlines():
            if any(kw in line for kw in ("Good signature", "key ID", "fingerprint", "using")):
                print(f"     {line.strip()}")
        return True
    else:
        print(f"  ✗ GPG signature INVALID")
        for line in result.stderr.splitlines():
            if line.strip():
                print(f"     {line.strip()}")
        return False

# VirusTotal

def check_virustotal(pdf: Path, api_key: str) -> bool:
    """Query VirusTotal for the SHA-256 of a PDF. Returns True if clean."""
    file_hash = _sha256(pdf)
    url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
    req = urllib.request.Request(url, headers={"x-apikey": api_key})

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"  ⚠  Not yet scanned on VirusTotal (hash: {file_hash[:16]}…)")
        else:
            print(f"  ⚠  VirusTotal HTTP error: {e.code}")
        return False
    except Exception as e:
        print(f"  ⚠  VirusTotal error: {e}")
        return False

    stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
    malicious  = stats.get("malicious",  0)
    suspicious = stats.get("suspicious", 0)
    undetected = stats.get("undetected", 0)
    harmless   = stats.get("harmless",   0)
    total      = malicious + suspicious + undetected + harmless

    clean = malicious == 0 and suspicious == 0
    mark = "✓" if clean else "✗"
    print(f"  {mark} VirusTotal  ({malicious} malicious, {suspicious} suspicious, "
          f"{harmless} clean / {total} engines)")
    print(f"     https://www.virustotal.com/gui/file/{file_hash}")
    return clean

def main() -> int:
    root = repo_root()
    export = root / "export"

    ap = argparse.ArgumentParser(
        description="Verify thgtoa PDF hashes, signatures, and VirusTotal status.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument(
        "--file",
        type=Path,
        default=None,
        metavar="PDF",
        help="Verify a single PDF instead of both light and dark",
    )
    ap.add_argument(
        "--export-dir",
        type=Path,
        default=export,
        metavar="DIR",
        help=f"Directory containing hash and signature files (default: {export})",
    )
    ap.add_argument("--hashes",     action="store_true", help="Verify hashes only")
    ap.add_argument("--signatures", action="store_true", help="Verify signatures only")
    ap.add_argument("--vt",         action="store_true", help="Check VirusTotal status")
    args = ap.parse_args()

    # Default: verify everything
    do_hashes = args.hashes or not any([args.hashes, args.signatures, args.vt])
    do_sigs   = args.signatures or not any([args.hashes, args.signatures, args.vt])
    do_vt     = args.vt or not any([args.hashes, args.signatures, args.vt])

    # Resolve PDFs to check
    if args.file:
        pdfs = [args.file]
    else:
        pdfs = [export / "thgtoa.pdf", export / "thgtoa-dark.pdf"]

    vt_api_key = os.environ.get("VT_API_KEY", "")

    overall_pass = True

    for pdf in pdfs:
        bar = "─" * 60
        print(f"\n{bar}")
        print(f"  {pdf.name}")
        print(bar)

        if not pdf.exists():
            print(f"  ⚠  File not found: {pdf} — skipping")
            overall_pass = False
            continue

        if do_hashes:
            ok = verify_hashes(pdf, args.export_dir)
            if not ok:
                overall_pass = False

        if do_sigs:
            result = verify_signature(pdf)
            if result is False:
                overall_pass = False

        if do_vt:
            if not vt_api_key:
                print("  ⚠  VT_API_KEY not set — skipping VirusTotal check")
            else:
                ok = check_virustotal(pdf, vt_api_key)
                if not ok:
                    overall_pass = False

    print(f"\n{'─' * 60}")
    if overall_pass:
        print("  ✓ All checks passed")
    else:
        print("  ✗ One or more checks failed")
    print()

    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
