#!/usr/bin/env python3
"""Build light-mode PDF with MkDocs + Chromium, then produce dark-mode PDF via convert.py.

Usage:
  python scripts/build_guide_pdf.py                    # Light PDF only
  python scripts/build_guide_pdf.py --dark             # Dark PDF only (requires light PDF to exist)
  python scripts/build_guide_pdf.py --both             # Light PDF, then dark PDF

Examples:
  python scripts/build_guide_pdf.py --site-dir build/html --pdf-light export/thgtoa.pdf
  python scripts/build_guide_pdf.py --both --pdf-light export/thgtoa.pdf --pdf-dark export/thgtoa-dark.pdf
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
    """Render html_file to pdf_out via headless Chromium.

    Uses a temp file first so an open guide.pdf on Windows does not block the
    build; if the final path is still locked, writes guide-new.pdf instead.
    """
    pdf_out.parent.mkdir(parents=True, exist_ok=True)
    partial = pdf_out.parent / f".{pdf_out.name}.writing"
    partial.unlink(missing_ok=True)

    uri = html_file.resolve().as_uri()

    cmd = [str(browser)]
    if os.environ.get("CI"):
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

# Use scripts/convert.py in place of broken dark-mode hack
def build_dark_pdf(light_pdf: Path, dark_pdf: Path) -> Path:
    """Convert the light PDF to dark mode using scripts/convert.py."""
    convert_script = repo_root() / "scripts" / "convert.py"
    print(f"Converting {light_pdf.name} → {dark_pdf.name} (dark mode)…")
    subprocess.run(
        [sys.executable, str(convert_script), str(light_pdf), str(dark_pdf)],
        check=True,
    )
    return dark_pdf


def main() -> int:
    root = repo_root()
    ap = argparse.ArgumentParser(
        description="Build MkDocs + single-page guide PDF (light and/or dark mode)."
    )
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
        help="Output path for light PDF (default: ./export/thgtoa.pdf)",
    )
    ap.add_argument(
        "--pdf-dark",
        type=Path,
        default=root / "export" / "thgtoa-dark.pdf",
        help="Output path for dark PDF (default: ./export/thgtoa-dark.pdf)",
    )
    ap.add_argument(
        "--skip-mkdocs",
        action="store_true",
        help="Reuse existing site dir; skip MkDocs build.",
    )

    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--dark",  action="store_true", help="Dark PDF only (light PDF must already exist)")
    mode.add_argument("--both",  action="store_true", help="Build light PDF, then dark PDF")
    # default (no flag) = light only
    args = ap.parse_args()

    build_light = not args.dark
    build_dark  = args.dark or args.both

    # --- Light PDF (Chromium) ---
    if build_light:
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

        out_light = print_to_pdf(browser, guide_html, args.pdf_light)
        size_kb = out_light.stat().st_size // 1024
        print(f"Wrote {out_light.resolve()} ({size_kb} KiB) [Light Mode]")
        if out_light.resolve() != args.pdf_light.resolve():
            print(
                f"Note: {args.pdf_light.name} was in use; "
                "close it and rename or replace with the file above.",
                file=sys.stderr,
            )

    # --- Dark PDF (pixel converter) ---
    if build_dark:
        if not args.pdf_light.exists():
            print(
                f"Light PDF not found at {args.pdf_light}. "
                "Run without --dark first, or use --both.",
                file=sys.stderr,
            )
            return 1

        out_dark = build_dark_pdf(args.pdf_light, args.pdf_dark)
        size_kb = out_dark.stat().st_size // 1024
        print(f"Wrote {out_dark.resolve()} ({size_kb} KiB) [Dark Mode]")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
