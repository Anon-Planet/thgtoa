#!/usr/bin/env python3
"""
Dark-mode PDF converter (pixel-based, batch-safe).

Rasterizes each page with pdftoppm, applies the hacker theme palette
pixel-by-pixel, then reassembles into a PDF. Processes in batches of 50
pages to stay within memory limits on large documents, then merges with qpdf.

Usage:
  python scripts/convert.py INPUT.pdf [OUTPUT.pdf]
  python scripts/convert.py INPUT.pdf [OUTPUT.pdf] [--dpi 200]
                            [--bg 1f1f31] [--text e0e0e0] [--link 5e8bde]
                            [--batch-size 50]

Examples:
  python scripts/convert.py export/thgtoa.pdf export/thgtoa-dark.pdf
  python scripts/convert.py export/thgtoa.pdf --dpi 150 --bg 0d1117

Note: Adds a cover page at the start with title/subtitle/version info.
"""

from __future__ import annotations

import argparse
import glob
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image


# --------------------------------------------------------------------------- #
#  Defaults (Hacker theme)
# --------------------------------------------------------------------------- #
DEFAULT_BG   = (0x1f, 0x1f, 0x31)
DEFAULT_TEXT = (0xe0, 0xe0, 0xe0)
DEFAULT_LINK = (0x5e, 0x8b, 0xde)
DEFAULT_DPI  = 200
DEFAULT_BATCH = 50


def hex_to_rgb(h: str) -> tuple:
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def apply_dark_theme(
    img: Image.Image,
    bg=DEFAULT_BG,
    text=DEFAULT_TEXT,
    link=DEFAULT_LINK,
) -> Image.Image:
    """
    Remap a white-background page image to a dark theme.

    Strategy:
    - Near-white pixels (page background)  → bg color
    - Dark, low-saturation pixels (text)    → text color
    - Blue-dominant dark pixels (links)     → link color
    - High-saturation pixels (photos/images) → preserved exactly as-is
      (no dark remapping; images stay at natural colors)

    The key fix vs. the old version: output is initialized from the *original*
    pixels, so any pixel that doesn't match a remap mask keeps its source color.
    This prevents the "black blobs" bug where image regions fell through to the
    zero-initialized buffer.
    """
    arr  = np.array(img.convert('RGB'), dtype=np.float32)
    norm = arr / 255.0

    # Luminance (Rec. 601)
    lum = (
        0.299 * norm[:, :, 0] +
        0.587 * norm[:, :, 1] +
        0.114 * norm[:, :, 2]
    )

    # Saturation (HSV model, vectorised)
    ch_min = np.min(norm, axis=2)
    ch_max = np.max(norm, axis=2)
    # Suppress the numpy divide error, idc
    # division happens on all elements including the zero ones
    with np.errstate(divide='ignore', invalid='ignore'):
        sat = np.where(ch_max > 0.001, (ch_max - ch_min) / ch_max, 0.0).astype(np.float32)

    # --- Masks ---
    # High-saturation = image/photo content — leave untouched
    is_image = sat > 0.20

    # Near-white page background
    is_bg = (lum > 0.88) & ~is_image

    # Blue-ish hyperlinks: blue channel dominant, dark, not an image
    is_link = (
        ~is_image &
        ~is_bg &
        (norm[:, :, 2] > 0.30) &
        (norm[:, :, 2] > norm[:, :, 0] * 1.20) &
        (lum < 0.75)
    )

    # Dark ink (text, borders, rules): not image, not bg, not link
    is_text = ~is_image & ~is_bg & ~is_link & (lum < 0.85)

    # --- Build output from original pixels ---
    # Start from a copy so anything not matched keeps source color.
    out = arr.copy()

    bg_f   = np.array(bg,   dtype=np.float32)
    text_f = np.array(text, dtype=np.float32)
    link_f = np.array(link, dtype=np.float32)

    # Full-strength remap for text: anything that was dark ink becomes text_color
    # at full brightness. No partial blend — partial blends leave mid-gray elements
    # (captions, borders, muted labels) at unreadable intermediate values.
    bg_mask3   = is_bg[..., np.newaxis]
    text_mask3 = is_text[..., np.newaxis]
    link_mask3 = is_link[..., np.newaxis]

    out = np.where(bg_mask3,   bg_f,   out)
    out = np.where(text_mask3, text_f, out)
    out = np.where(link_mask3, link_f, out)

    return Image.fromarray(out.clip(0, 255).astype(np.uint8))


def _save_images_as_pdf(images: list, output_path: str) -> None:
    """Save a list of RGB PIL images as a PDF without requiring libjpeg.

    Pillow's PDF writer defaults to JPEG encoding for RGB images, which
    fails when libjpeg is absent in the environment. Fix: quantize each
    image to palette mode (256 colours, FASTOCTREE) so Pillow uses
    zlib/deflate instead of JPEG, save each as an individual single-page
    PDF, then merge the page PDFs with qpdf.

    Colour fidelity is preserved — the hacker theme uses only a handful
    of distinct colours so 256-colour quantization is visually lossless.
    """
    import tempfile as _tempfile
    with _tempfile.TemporaryDirectory() as staging:
        page_pdfs = []
        for i, img in enumerate(images):
            page_path = os.path.join(staging, f'p{i:05d}.pdf')
            img.quantize(colors=256, method=Image.Quantize.FASTOCTREE).save(
                page_path, format='PDF'
            )
            page_pdfs.append(page_path)
        subprocess.run(
            ['qpdf', '--empty', '--pages'] + page_pdfs + ['--', output_path],
            check=True,
        )


def _check_qpdf() -> bool:
    return subprocess.run(
        ['qpdf', '--version'], capture_output=True
    ).returncode == 0


def _check_dependencies() -> None:
    """Verify required system tools are available before doing any work."""
    missing = []
    for tool in ('pdftoppm', 'qpdf'):
        if subprocess.run(['which', tool], capture_output=True).returncode != 0:
            missing.append(tool)
    if missing:
        tools = ', '.join(missing)
        instructions = (
            f"Install with:\n"
            f"  Linux/WSL:  sudo apt install poppler-utils qpdf\n"
            f"  macOS:      brew install poppler qpdf\n"
            f"  Windows:    see docs/code/develop.md"
        )
        raise RuntimeError(
            f"Missing required system tool(s): {tools}\n{instructions}"
        )


def create_cover_page(tmp_dir: str, is_dark: bool) -> str:
    """Create a research-style text-only cover page for Chromium rendering."""
    if is_dark:
        bg_color    = '#1f1f31'
        text_color  = '#e0e0e0'
        rule_color  = '#4a4a6a'
        meta_color  = '#a0a0c0'
    else:
        bg_color    = '#ffffff'
        text_color  = '#1a1a1a'
        rule_color  = '#cccccc'
        meta_color  = '#555555'

    html_path = os.path.join(tmp_dir, 'cover.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
* {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}}
@page {{
    size: A4;
    margin: 0;
}}
html, body {{
    width: 210mm;
    height: 297mm;
    background: {bg_color};
    color: {text_color};
    font-family: 'EB Garamond', Georgia, 'Times New Roman', serif;
}}
.page {{
    width: 210mm;
    height: 297mm;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 30mm 25mm;
    text-align: center;
}}
.title {{
    font-size: 28pt;
    font-weight: normal;
    line-height: 1.25;
    letter-spacing: 0.01em;
    margin-bottom: 10mm;
}}
.rule {{
    width: 80mm;
    height: 1px;
    background: {rule_color};
    margin: 0 auto 10mm auto;
}}
.subtitle {{
    font-size: 13pt;
    font-weight: normal;
    font-style: italic;
    color: {meta_color};
    margin-bottom: 14mm;
}}
.meta {{
    font-size: 11pt;
    color: {meta_color};
    line-height: 1.9;
}}
.meta strong {{
    color: {text_color};
    font-weight: normal;
}}
.version {{
    font-size: 11pt;
    color: {meta_color};
    margin-top: 12mm;
    letter-spacing: 0.05em;
}}
</style>
</head>
<body>
<div class="page">
  <p class="title">The Hitchhiker&#8217;s Guide<br>to Online Anonymity</p>
  <div class="rule"></div>
  <p class="subtitle">The comprehensive guide for online anonymity and OpSec.</p>
  <div class="meta">
    <p><strong>Author</strong> &nbsp; Anonymous Planet</p>
    <p><strong>License</strong> &nbsp; Creative Commons BY-SA 4.0</p>
    <p><strong>Source</strong> &nbsp; https://anonymousplanet.net</p>
  </div>
  <p class="version">v1.2.6 &mdash; July 12 2026</p>
</div>
</body>
</html>""")
    return html_path


def convert_pdf_to_dark(
    input_path: str | Path,
    output_path: str | Path,
    dpi: int = DEFAULT_DPI,
    bg=DEFAULT_BG,
    text=DEFAULT_TEXT,
    link=DEFAULT_LINK,
    batch_size: int = DEFAULT_BATCH,
) -> None:
    """
    Full pipeline: rasterize → apply dark theme → reassemble as PDF.

    For large documents, pages are processed in batches of `batch_size` to
    avoid OOM, then merged with qpdf. Falls back to single-pass Pillow save
    if qpdf is not available (fine for small documents).

    Adds a cover page at the start with title/subtitle/version info.
    """
    input_path  = str(input_path)
    output_path = str(output_path)

    _check_dependencies()

    with tempfile.TemporaryDirectory() as tmp:
        # 1. Rasterize all pages
        prefix = os.path.join(tmp, 'page')
        result = subprocess.run(
            ['pdftoppm', '-r', str(dpi), '-png', input_path, prefix],
            capture_output=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"pdftoppm failed:\n{result.stderr.decode()}"
            )

        pages = sorted(glob.glob(prefix + '-*.png'))
        if not pages:
            raise RuntimeError(
                "pdftoppm produced no output pages — "
                "is the PDF valid and not password-protected?"
            )

        total = len(pages)
        print(f"  Converting {total} page(s) at {dpi} DPI…", flush=True)

        out_dir = os.path.dirname(output_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        # Determine theme from filename for cover page
        pdf_output = Path(output_path)
        pdf_name = pdf_output.stem.lower()
        is_dark = 'dark' in pdf_name

        print(f"  Theme: {'Going dark' if is_dark else 'Light mode'}")

        # 2. Build front matter: cover + ToC
        # Import ToC helpers from build_guide_pdf.py (single source of truth).
        scripts_dir = str(Path(__file__).resolve().parent)
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        from build_guide_pdf import parse_toc_headings, create_toc_html  # noqa: PLC0415

        cover_html_path = create_cover_page(tmp, is_dark)
        browser = find_chromium_executable()

        if not browser:
            raise RuntimeError(
                "No Chromium-based browser found; needed for cover page rendering.\n"
                "Install Chrome, Edge, or add Chromium to PATH."
            )

        cover_pdf = os.path.join(tmp, 'cover.pdf')
        cmd = [str(browser), "--headless=new", "--disable-gpu",
               "--no-pdf-header-footer", "--print-background", "--no-margins",
               f"--print-to-pdf={cover_pdf}", cover_html_path]
        subprocess.run(cmd, check=True, capture_output=True)

        guide_md = Path(__file__).resolve().parent.parent / 'docs' / 'guide' / 'index.md'
        if guide_md.is_file():
            print("  Building ToC...", flush=True)
            headings = parse_toc_headings(guide_md)
            toc_html_path = create_toc_html(tmp, headings, is_dark)
            toc_pdf = os.path.join(tmp, 'toc.pdf')
            cmd_toc = [str(browser), "--headless=new", "--disable-gpu",
                       "--no-pdf-header-footer", "--print-background", "--no-margins",
                       f"--print-to-pdf={toc_pdf}", toc_html_path]
            subprocess.run(cmd_toc, check=True, capture_output=True)
            front_pages = [cover_pdf, toc_pdf]
        else:
            print("  Warning: guide/index.md not found, skipping ToC.", file=sys.stderr)
            front_pages = [cover_pdf]

        # 3. Process pages with theme remapping
        use_batches = total > batch_size and _check_qpdf()

        if use_batches:
            batch_dir = os.path.join(tmp, 'batches')
            os.makedirs(batch_dir)
            batch_files = []

            for start in range(0, total, batch_size):
                batch = pages[start:start + batch_size]
                batch_num = start // batch_size + 1
                batch_path = os.path.join(batch_dir, f'batch_{batch_num:04d}.pdf')

                print(
                    f"  Batch {batch_num}/{(total + batch_size - 1) // batch_size}: "
                    f"pages {start + 1}–{start + len(batch)}",
                    flush=True,
                )

                dark = [apply_dark_theme(Image.open(p), bg, text, link) for p in batch]
                _save_images_as_pdf(dark, batch_path)
                batch_files.append(batch_path)

            # Merge batches with front matter using qpdf
            print("  Merging batches and front matter...", flush=True)
            subprocess.run(
                ['qpdf', '--empty', '--pages'] + front_pages + batch_files + ['--', output_path],
                check=True,
            )

        else:
            # Single-pass for small documents or when qpdf is unavailable
            dark_pages = []
            for i, p in enumerate(pages, 1):
                if i % 50 == 0 or i == 1:
                    print(f"  Page {i}/{total}", flush=True)
                dark_pages.append(apply_dark_theme(Image.open(p), bg, text, link))

            _save_images_as_pdf(dark_pages, output_path)

        # Prepend front matter to the single-pass output
        if not use_batches:
            tmp_body = os.path.join(tmp, 'body_only.pdf')
            os.rename(output_path, tmp_body)
            subprocess.run(
                ['qpdf', '--empty', '--pages'] + front_pages + [tmp_body] + ['--', output_path],
                check=True,
            )

    size_mb = os.path.getsize(output_path) / 1024 / 1024
    print(f"  Saved → {output_path} ({size_mb:.1f} MB)")


def find_chromium_executable() -> Path | None:
    """Find a Chromium-based browser on the system (prioritizes WSL/Linux paths).

    On WSL Windows, checks WSL tools first, then falls back to Windows paths.
    """
    import os as _os
    import shutil
    import sys

    # First, check WSL/Linux locations (common for WSL Windows)
    wsl_paths = [
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium-browser",
        "/usr/bin/chromium",
        "/usr/bin/microsoft-edge",
        "/usr/bin/microsoft-edge-stable",
        "/usr/bin/microsoft-edge-dev",
        "/snap/bin/chromium",
        "/usr/local/bin/chrome",
        "/opt/google-chrome/",
    ]

    for p in wsl_paths:
        if _os.path.isfile(p):
            return Path(p)

    # Then check shutil.which (standard PATH, includes WSL paths)
    for name in ("google-chrome-stable", "google-chrome", "chromium-browser", "chromium",
                 "microsoft-edge-stable", "microsoft-edge", "msedge", "chrome"):
        w = shutil.which(name)
        if w:
            return Path(w)

    # Finally, Windows-specific paths (if running natively on Windows)
    if sys.platform == "win32":
        paths = [
            Path(_os.environ.get("PROGRAMFILES(X86)", "")) / "Microsoft/Edge/Application/msedge.exe",
            Path(_os.environ.get("LOCALAPPDATA", "")) / "Microsoft/Edge/Application/msedge.exe",
            Path(_os.environ.get("PROGRAMFILES", "")) / "Google/Chrome/Application/chrome.exe",
        ]
        for p in paths:
            if p.is_file():
                return p

    return None


# --------------------------------------------------------------------------- #
#  CLI
# --------------------------------------------------------------------------- #
def main() -> int:
    parser = argparse.ArgumentParser(description='Convert a PDF to dark mode.')
    parser.add_argument('input',  help='Input PDF path')
    parser.add_argument('output', nargs='?', help='Output PDF path (optional)')
    parser.add_argument('--dpi',        type=int, default=DEFAULT_DPI,   help='Rasterization DPI (default: 200)')
    parser.add_argument('--batch-size', type=int, default=DEFAULT_BATCH, help='Pages per batch (default: 50)')
    parser.add_argument('--bg',   default='1f1f31', help='Background hex color  (default: 1f1f31)')
    parser.add_argument('--text', default='e0e0e0', help='Body text hex color   (default: e0e0e0)')
    parser.add_argument('--link', default='5e8bde', help='Link/blue hex color   (default: 5e8bde)')
    args = parser.parse_args()

    if not args.output:
        base = Path(args.input).stem
        args.output = str(Path(args.input).parent / f"{base}-dark.pdf")

    convert_pdf_to_dark(
        args.input,
        args.output,
        dpi=args.dpi,
        bg=hex_to_rgb(args.bg),
        text=hex_to_rgb(args.text),
        link=hex_to_rgb(args.link),
        batch_size=args.batch_size,
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
