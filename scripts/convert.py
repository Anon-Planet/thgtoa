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
    - Near-white pixels      → bg color
    - Dark pixels (ink/text) → text color
    - Blue-ish pixels        → link color
    """
    arr  = np.array(img.convert('RGB'), dtype=np.float32)
    orig = arr.copy()
    norm = arr / 255.0

    lightness = (
        0.299 * norm[:, :, 0]
        + 0.587 * norm[:, :, 1]
        + 0.114 * norm[:, :, 2]
    )

    r, g, b = orig[:, :, 0], orig[:, :, 1], orig[:, :, 2]
    link_mask = (
        (b > 100)
        & (b > r * 1.3)
        & (b > g * 0.9)
        & (lightness < 0.85)
    )
    content_mask = (lightness < 0.85) & ~link_mask
    blend = ((1.0 - lightness) / 0.85).clip(0, 1)

    bg_f   = [c / 255.0 for c in bg]
    text_f = [c / 255.0 for c in text]
    link_f = [c / 255.0 for c in link]

    out = np.zeros_like(norm)
    for i, (b_c, t, lc) in enumerate(zip(bg_f, text_f, link_f)):
        channel = np.full(lightness.shape, b_c)
        channel = np.where(content_mask, b_c + blend * (t - b_c), channel)
        channel = np.where(link_mask,    b_c + blend * (lc - b_c), channel)
        out[:, :, i] = channel

    return Image.fromarray((out * 255).clip(0, 255).astype('uint8'))


def _save_images_as_pdf(images: list, output_path: str) -> None:
    """Save a list of RGB PIL images as a PDF using PNG compression via qpdf.

    Pillow's built-in PDF writer defaults to JPEG encoding for RGB images,
    which fails when libjpeg is not available in the environment. Instead we
    write each page as a lossless PNG to a temp directory and assemble them
    with qpdf, which embeds the PNGs directly without re-encoding.
    """
    import tempfile as _tempfile
    with _tempfile.TemporaryDirectory() as staging:
        png_paths = []
        for i, img in enumerate(images):
            p = os.path.join(staging, f'p{i:05d}.png')
            img.save(p, format='PNG')
            png_paths.append(p)
        subprocess.run(
            ['qpdf', '--empty', '--pages'] + png_paths + ['--', output_path],
            check=True,
        )


def _check_qpdf() -> bool:
    return subprocess.run(
        ['qpdf', '--version'], capture_output=True
    ).returncode == 0


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
    """
    input_path  = str(input_path)
    output_path = str(output_path)

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

        # 2. Process in batches
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
                del dark

            # 3. Merge batches with qpdf
            print("  Merging batches…", flush=True)
            subprocess.run(
                ['qpdf', '--empty', '--pages'] + batch_files + ['--', output_path],
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

    size_mb = os.path.getsize(output_path) / 1024 / 1024
    print(f"  Saved → {output_path} ({size_mb:.1f} MB)")


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
