#!/usr/bin/env python3
"""Experimental dark mode support.

This script builds both light and dark mode MkDocs site, then renders docs/guide/ to single PDFs via Chromium.

Usage:
  python scripts/build_guide_pdf.py                    # Generate light mode PDF only
  python scripts/build_guide_pdf.py --dark-mode        # Generate dark mode PDF only
  python scripts/build_guide_pdf.py --both             # Generate both light and dark mode PDFs

Examples:
  python scripts/build_guide_pdf.py --site-dir build/html --pdf-light export/thgtoa.pdf
  python scripts/build_guide_pdf.py --dark-mode --pdf-dark export/thgtoa-dark.pdf
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


def print_to_pdf(browser: Path, html_file: Path, pdf_out: Path, dark_mode: bool = False) -> Path:
    """Write PDF to ``pdf_out``. Uses a temp file first so an open ``guide.pdf`` on Windows
    does not block the build: if the final path is locked, writes ``guide-new.pdf`` instead.

    Args:
        browser: Path to Chromium executable
        html_file: Path to HTML file to convert
        pdf_out: Output PDF path
        dark_mode: If True, use dark mode color scheme via --prefers-color-scheme flag
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
    ]

    # Add dark mode preference if requested
    if dark_mode:
        cmd.append("--prefers-color-scheme=dark")

    cmd += [
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


def generate_dark_mode_html(html_file: Path, output_file: Path, dark_css_path: Path) -> None:
    """Create a temporary HTML file with dark mode stylesheet applied.

    This is used when we need to force dark mode rendering via CSS rather than browser flags.
    """
    try:
        from bs4 import BeautifulSoup

        # Read the original HTML
        html_content = html_file.read_text(encoding='utf-8')
        soup = BeautifulSoup(html_content, 'html.parser')

        # Add dark mode stylesheet link if not present
        existing_links = [link.get('href', '') for link in soup.find_all('link', rel='stylesheet')]
        if not any(dark_css_path.name in link for link in existing_links):
            head = soup.head or soup.new_tag('head')
            link_tag = soup.new_tag('link', rel='stylesheet', href=str(dark_css_path))
            if soup.head:
                soup.head.append(link_tag)
            else:
                # Create a new head section
                new_head = soup.new_tag('head')
                new_head.append(link_tag)
                soup.insert(0, new_head)

        # Write the modified HTML
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(str(soup), encoding='utf-8')
    except ImportError:
        print("BeautifulSoup not available. Skipping CSS injection.")


def main() -> int:
    root = repo_root()
    ap = argparse.ArgumentParser(description="Build MkDocs + single-page guide PDF (light and/or dark mode).")
    ap.add_argument(
        "--site-dir",
        type=Path,
        default=root / "build" / "html",
        help="MkDocs output directory (default: ./build/html)",
    )
    ap.add_argument(
        "--pdf-light",
        type=Path,
        default=root / "export" / "thgtoa.pdf",
        help="Output PDF path for light mode (default: ./export/guide.pdf)",
    )
    ap.add_argument(
        "--pdf-dark",
        type=Path,
        default=root / "export" / "thgtoa-dark.pdf",
        help="Output PDF path for dark mode (default: ./export/guide-dark.pdf)",
    )
    ap.add_argument("--skip-mkdocs", action="store_true", help="Reuse existing site dir; only run print-to-pdf.")
    ap.add_argument("--dark-mode", action="store_true", help="Generate dark mode PDF only")
    ap.add_argument("--both", action="store_true", help="Generate both light and dark mode PDFs")
    args = ap.parse_args()

    # Determine which modes to generate
    if args.dark_mode:
        modes = ["dark"]
    elif args.both:
        modes = ["light", "dark"]
    else:
        modes = ["light"]

    guide_html = args.site_dir / "guide" / "index.html"

    if not args.skip_mkdocs or any(mode == "light" for mode in modes):
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

    dark_css_path = root / "docs" / "stylesheets" / "dark-extra.css"

    # Generate light mode PDF (default)
    if "light" in modes:
        out_light = print_to_pdf(browser, guide_html, args.pdf_light, dark_mode=False)
        size_kb = out_light.stat().st_size // 1024
        print(f"Wrote {out_light.resolve()} ({size_kb} KiB) [Light Mode]")
        if out_light.resolve() != args.pdf_light.resolve():
            print(
                f"Note: {args.pdf_light.name} was in use; close it and rename or replace with the file above.",
                file=sys.stderr,
            )

    # Generate dark mode PDF
    if "dark" in modes:
        out_dark = print_to_pdf(browser, guide_html, args.pdf_dark, dark_mode=True)
        size_kb = out_dark.stat().st_size // 1024
        print(f"Wrote {out_dark.resolve()} ({size_kb} KiB) [Dark Mode]")
        if out_dark.resolve() != args.pdf_dark.resolve():
            print(
                f"Note: {args.pdf_dark.name} was in use; close it and rename or replace with the file above.",
                file=sys.stderr,
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
