#!/usr/bin/env python3
"""
Download self-hosted fonts for the thgtoa MkDocs site.
Run once from the repo root. Requires network access (uses npm registry
via a temporary npm pack, or direct URLs from fontsource CDN as fallback).

Usage:
    python scripts/install_fonts.py

Fonts installed:
    docs/fonts/eb-garamond/   - EB Garamond 400/700 normal+italic (latin, latin-ext)
    docs/fonts/fira-code/     - Fira Code variable (latin, latin-ext)
"""

import os
import subprocess
import sys
import tarfile
import tempfile
import shutil

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS_DIR = os.path.join(REPO_ROOT, "docs", "fonts")

EB_GARAMOND_DIR = os.path.join(FONTS_DIR, "eb-garamond")
FIRA_CODE_DIR = os.path.join(FONTS_DIR, "fira-code")

EB_GARAMOND_FILES = [
    "eb-garamond-latin-400-normal.woff2",
    "eb-garamond-latin-400-italic.woff2",
    "eb-garamond-latin-700-normal.woff2",
    "eb-garamond-latin-700-italic.woff2",
    "eb-garamond-latin-ext-400-normal.woff2",
    "eb-garamond-latin-ext-400-italic.woff2",
    "eb-garamond-latin-ext-700-normal.woff2",
    "eb-garamond-latin-ext-700-italic.woff2",
]

FIRA_CODE_FILES = [
    "fira-code-latin-wght-normal.woff2",
    "fira-code-latin-ext-wght-normal.woff2",
]


def npm_pack(package: str, tmpdir: str) -> str:
    """Run npm pack and return the path to the extracted package dir."""
    result = subprocess.run(
        ["npm", "pack", package, "--silent"],
        cwd=tmpdir, capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"npm pack failed for {package}:\n{result.stderr}")
    tgz = os.path.join(tmpdir, result.stdout.strip())
    with tarfile.open(tgz, "r:gz") as tf:
        tf.extractall(tmpdir)
    return os.path.join(tmpdir, "package")


def install_package(package: str, files: list[str], dest: str) -> None:
    os.makedirs(dest, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"  Fetching {package} ...")
        pkg_dir = npm_pack(package, tmpdir)
        files_dir = os.path.join(pkg_dir, "files")
        for fname in files:
            src = os.path.join(files_dir, fname)
            if not os.path.exists(src):
                print(f"  WARNING: {fname} not found in package", file=sys.stderr)
                continue
            dst = os.path.join(dest, fname)
            shutil.copy2(src, dst)
            size = os.path.getsize(dst)
            print(f"  + {fname} ({size // 1024}K)")


def main() -> None:
    print("Installing self-hosted fonts for thgtoa...\n")

    if shutil.which("npm") is None:
        print("ERROR: npm not found. Install Node.js and re-run.", file=sys.stderr)
        sys.exit(1)

    print("EB Garamond (fontsource):")
    install_package("@fontsource/eb-garamond", EB_GARAMOND_FILES, EB_GARAMOND_DIR)

    print("\nFira Code Variable (fontsource):")
    install_package("@fontsource-variable/fira-code", FIRA_CODE_FILES, FIRA_CODE_DIR)

    print("\nDone. Font files written to docs/fonts/")
    print("Commit docs/fonts/ to the repository so it is served with the site.")


if __name__ == "__main__":
    main()
