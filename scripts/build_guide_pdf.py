#!/usr/bin/env python3
"""Build the MkDocs site, then render docs/guide/ to a single PDF via a Chromium-based browser.

Uses headless Chrome/Edge print-to-PDF (embeds images). WeasyPrint-based mkdocs-with-pdf is
omitted here because it needs GTK/Pango (awkward on Windows).

Usage (from repo root):
  python scripts/build_guide_pdf.py
  python scripts/build_guide_pdf.py --site-dir build/html --pdf export/guide.pdf
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def find_chromium_executable() -> Path | None:
    if sys.platform == "win32":
        paths = [
            Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Microsoft/Edge/Application/msedge.exe",
            Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft/Edge/Application/msedge.exe",
            Path(os.environ.get("PROGRAMFILES", "")) / "Google/Chrome/Application/chrome.exe",
            Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Google/Chrome/Application/chrome.exe",
            Path(os.environ.get("LOCALAPPDATA", "")) / "Google/Chrome/Application/chrome.exe",
        ]
        for p in paths:
            if p.is_file():
                return p
        for name in ("chrome", "msedge"):
            w = shutil.which(name)
            if w:
                return Path(w)
    elif sys.platform == "darwin":
        for p in (
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
        ):
            if os.path.isfile(p):
                return Path(p)
    for name in ("google-chrome-stable", "google-chrome", "chromium-browser", "chromium", "chrome"):
        w = shutil.which(name)
        if w:
            return Path(w)
    return None


def run_mkdocs(site_dir: Path) -> None:
    site_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [sys.executable, "-m", "mkdocs", "build", "-d", str(site_dir)],
        cwd=repo_root(),
        check=True,
    )


def print_to_pdf(browser: Path, html_file: Path, pdf_out: Path) -> Path:
    """Write PDF to ``pdf_out``. Uses a temp file first so an open ``guide.pdf`` on Windows
    does not block the build: if the final path is locked, writes ``guide-new.pdf`` instead.
    """
    pdf_out.parent.mkdir(parents=True, exist_ok=True)
    partial = pdf_out.parent / f".{pdf_out.name}.writing"
    partial.unlink(missing_ok=True)

    uri = html_file.resolve().as_uri()
    # Chromium headless print; allow time for fonts/images on very large pages.
    cmd = [str(browser)]
    if os.environ.get("CI"):
        # GitHub Actions / other CI runners often need these for Chromium to start.
        cmd += [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
        ]
    cmd += [
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={partial.resolve()}",
        uri,
    ]
    subprocess.run(cmd, check=True, timeout=600)
    deadline = time.time() + 120
    while time.time() < deadline:
        if partial.exists() and partial.stat().st_size > 0:
            break
        time.sleep(0.25)
    else:
        partial.unlink(missing_ok=True)
        raise RuntimeError(f"PDF was not written to {partial}")

    try:
        if pdf_out.exists():
            pdf_out.unlink()
    except PermissionError:
        fallback = pdf_out.with_name(f"{pdf_out.stem}-new{pdf_out.suffix}")
        fallback.unlink(missing_ok=True)
        partial.replace(fallback)
        return fallback

    partial.replace(pdf_out)
    return pdf_out


def main() -> int:
    root = repo_root()
    ap = argparse.ArgumentParser(description="Build MkDocs + single-page guide PDF.")
    ap.add_argument(
        "--site-dir",
        type=Path,
        default=root / "site",
        help="MkDocs output directory (default: ./site)",
    )
    ap.add_argument(
        "--pdf",
        type=Path,
        default=root / "export" / "guide.pdf",
        help="Output PDF path (default: ./export/guide.pdf)",
    )
    ap.add_argument("--skip-mkdocs", action="store_true", help="Reuse existing site dir; only run print-to-pdf.")
    args = ap.parse_args()

    guide_html = args.site_dir / "guide" / "index.html"
    if not args.skip_mkdocs:
        run_mkdocs(args.site_dir)
    if not guide_html.is_file():
        print(f"Missing {guide_html}; run without --skip-mkdocs first.", file=sys.stderr)
        return 1

    browser = find_chromium_executable()
    if not browser:
        print(
            "No Chromium-based browser found (Chrome, Edge, or Chromium). "
            "Install Google Chrome or Microsoft Edge, or add Chromium to PATH.",
            file=sys.stderr,
        )
        return 1

    out = print_to_pdf(browser, guide_html, args.pdf)
    size_kb = out.stat().st_size // 1024
    print(f"Wrote {out.resolve()} ({size_kb} KiB)")
    if out.resolve() != args.pdf.resolve():
        print(
            f"Note: {args.pdf.name} was in use; close it and rename or replace with the file above.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
