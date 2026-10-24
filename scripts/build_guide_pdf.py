#!/usr/bin/env python3
"""Build light-mode PDF with MkDocs + Chromium, then produce dark-mode PDF via convert.py.

Usage:
  python scripts/build_guide_pdf.py                    # Light PDF only (clean light theme)
  python scripts/build_guide_pdf.py --dark             # Dark PDF only (requires a body-only
                                                         # cache from a prior light build in
                                                         # this checkout, e.g. via --both)
  python scripts/build_guide_pdf.py --both             # Light PDF, then dark PDF

Examples:
  python scripts/build_guide_pdf.py --site-dir build/html --pdf-light export/thgtoa.pdf
  python scripts/build_guide_pdf.py --both --pdf-light export/thgtoa.pdf --pdf-dark export/thgtoa-dark.pdf
"""

from __future__ import annotations

import argparse
import html as _html_mod
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unicodedata
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def find_chromium_executable() -> Path | None:
    """Find a Chromium-based browser on the system (prioritizes WSL/Linux paths).

    On WSL Windows, checks WSL tools first, then falls back to Windows paths.
    """
    import os as _os
    import shutil

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
        if os.path.isfile(p):
            return Path(p)

    for name in ("google-chrome-stable", "google-chrome", "chromium-browser", "chromium",
                 "microsoft-edge-stable", "microsoft-edge", "msedge", "chrome"):
        w = shutil.which(name)
        if w:
            return Path(w)

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


def run_mkdocs(site_dir: Path) -> None:
    """Build MkDocs site."""
    site_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [sys.executable, "-m", "mkdocs", "build", "-d", str(site_dir)],
        cwd=repo_root(),
        check=True,
    )


def inject_print_light_css(html_file: Path) -> Path:
    """Inject print-light.css inline into the built HTML for light PDF builds."""
    html_path = html_file.resolve()
    print_light_css = repo_root() / "docs" / "stylesheets" / "print-light.css"

    if not print_light_css.is_file():
        print(f"Warning: {print_light_css} not found, skipping CSS injection.", file=sys.stderr)
        return html_path

    css_content = print_light_css.read_text(encoding="utf-8")
    html_content = html_path.read_text(encoding="utf-8")

    head_match = re.search(r"<head(?:[^>]*)>", html_content, re.IGNORECASE)
    if not head_match:
        print("Warning: Could not find <head> tag in HTML, skipping CSS injection.", file=sys.stderr)
        return html_path

    insert_pos = head_match.end()
    style_block = (
        "\n<!-- Light PDF theme: injected inline so file:// URI resolves correctly -->\n"
        "<style>\n"
        + css_content
        + "\n</style>\n"
    )

    new_html = html_content[:insert_pos] + style_block + html_content[insert_pos:]

    output_file = html_path.with_stem(html_path.stem + "-light-pdf")
    output_file.write_text(new_html, encoding="utf-8")
    return output_file


def print_to_pdf(browser: Path, html_file: Path, pdf_out: Path) -> Path:
    """Render html_file to pdf_out via headless Chromium."""
    pdf_out.parent.mkdir(parents=True, exist_ok=True)
    partial = pdf_out.parent / f".{pdf_out.name}.writing"
    partial.unlink(missing_ok=True)

    html_file = inject_print_light_css(html_file)
    uri = html_file.resolve().as_uri()

    cmd = [str(browser)]
    if os.environ.get("CI"):
        cmd += ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
    cmd += [
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--print-background",
        "--no-margins",
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


# Page numbers (stamped with qpdf; no extra Python dependencies)

def stamp_page_numbers(pdf_path: Path) -> None:
    """Stamp a right-aligned page number at the bottom of every page, in place.

    Chromium's --print-to-pdf can't draw page numbers when the default
    header/footer is disabled, and @page margin boxes need Chrome >= 131
    (CI pins 120). So build a tiny overlay PDF by hand (standard Times font,
    no dependencies) and merge it with `qpdf --overlay`.

    Called on the body-only PDF, before the cached copy is taken and before
    the cover + ToC are prepended, so the body starts at page 1 in both the
    light and dark builds.
    """
    n_pages = int(
        subprocess.run(
            ["qpdf", "--show-npages", str(pdf_path)],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
    )

    width, height = 595.28, 841.89      # A4 in points (matches @page size)
    font_size = 10
    baseline_y = 28                      # ~10 mm from the bottom edge (inside the 16 mm margin)
    digit_w = 0.5 * font_size            # Times-Roman digits are 500/1000 em
    right_x = width - 12 * 72 / 25.4     # right text edge (12 mm page margin)

    objs: list[bytes] = [b""] * (3 + 2 * n_pages)
    kids = " ".join(f"{4 + 2 * i} 0 R" for i in range(n_pages))
    objs[0] = b"<< /Type /Catalog /Pages 2 0 R >>"
    objs[1] = f"<< /Type /Pages /Kids [{kids}] /Count {n_pages} >>".encode()
    objs[2] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Times-Roman >>"
    for i in range(n_pages):
        label = str(i + 1)
        x = right_x - digit_w * len(label)
        stream = f"BT /F1 {font_size} Tf 0.33 g {x:.2f} {baseline_y} Td ({label}) Tj ET".encode()
        objs[3 + 2 * i] = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {width} {height}] "
            f"/Resources << /Font << /F1 3 0 R >> >> /Contents {5 + 2 * i} 0 R >>"
        ).encode()
        objs[4 + 2 * i] = (
            f"<< /Length {len(stream)} >>\nstream\n".encode() + stream + b"\nendstream"
        )

    out = bytearray(b"%PDF-1.4\n")
    offsets: list[int] = []
    for num, body in enumerate(objs, start=1):
        offsets.append(len(out))
        out += f"{num} 0 obj\n".encode() + body + b"\nendobj\n"
    xref_pos = len(out)
    out += f"xref\n0 {len(objs) + 1}\n".encode()
    out += b"0000000000 65535 f \n"
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode()
    out += (
        f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_pos}\n%%EOF\n"
    ).encode()

    with tempfile.TemporaryDirectory() as tmp:
        overlay = Path(tmp) / "page-numbers.pdf"
        overlay.write_bytes(bytes(out))
        stamped = Path(tmp) / "stamped.pdf"
        subprocess.run(
            ["qpdf", str(pdf_path), "--overlay", str(overlay), "--", str(stamped)],
            check=True,
        )
        shutil.move(str(stamped), str(pdf_path))


# ---------------------------------------------------------------------------
# Front matter: ToC parsing + HTML generation
# ---------------------------------------------------------------------------

def parse_toc_headings(guide_md: Path) -> list[tuple[int, str]]:
    """Extract H2 and H3 headings from the guide markdown source.

    Returns a list of (level, title) tuples in document order.
    Strips MkDocs anchor suffixes like { #some-id } and common inline markup.
    Skips headings inside fenced code blocks.
    """
    headings: list[tuple[int, str]] = []
    in_fence = False
    fence_re   = re.compile(r"^\s*```")
    heading_re = re.compile(r"^(#{2,3})\s+(.+?)(?:\s*\{[^}]*\})?\s*$")
    inline_re  = re.compile(
        r"\*{1,2}([^*]+)\*{1,2}"    # **bold** / *italic*
        r"|`[^`]+`"                   # `code`
        r"|\[([^\]]+)\]\([^)]*\)"    # [text](url)
    )

    for line in guide_md.read_text(encoding="utf-8").splitlines():
        if fence_re.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = heading_re.match(line)
        if m:
            level = len(m.group(1))
            raw   = m.group(2).strip()
            title = inline_re.sub(
                lambda x: x.group(1) or x.group(2) or "", raw
            ).strip()
            headings.append((level, title))
    return headings


def create_toc_html(
    tmp_dir: str,
    headings: list[tuple[int, str]],
    pages: list[int | None],
    is_dark: bool,
    scale: float = 1.0,
) -> str:
    """Write a research-style Table of Contents HTML file and return its path.

    H2 entries: full-width row with dot leader.
    H3 entries: indented, italic, muted colour.
    Layout matches the cover page (A4, same font stack, no Chromium margins).
    """
    if is_dark:
        bg      = "#1f1f31"
        fg      = "#e0e0e0"
        muted   = "#a0a0c0"
        rule    = "#4a4a6a"
        h3color = "#b8b8d8"
    else:
        bg      = "#ffffff"
        fg      = "#1a1a1a"
        muted   = "#555555"
        rule    = "#cccccc"
        h3color = "#444466"

    rows: list[str] = []
    for (level, title), page in zip(headings, pages):
        safe = _html_mod.escape(title)
        page_html = f'<span class="toc-page">{page}</span>' if page else ""
        cls = "toc-h2" if level == 2 else "toc-h3"
        rows.append(
            f'<div class="{cls}">'
            f'<span class="toc-title">{safe}</span>'
            f'<span class="toc-dots"></span>'
            f"{page_html}"
            f"</div>"
        )

    body = "\n".join(rows)

    css = (
        "* { box-sizing: border-box; margin: 0; padding: 0; }\n"
        "@page { size: A4; margin: 12mm 12mm 16mm 12mm; }\n"
        "html, body {\n"
        f"    background: {bg};\n"
        f"    color: {fg};\n"
        "    font-family: 'EB Garamond', Georgia, 'Times New Roman', serif;\n"
        "}\n"
        ".page {\n"
        "    padding: 0;\n"
        f"    zoom: {scale};\n"
        "}\n"
        ".toc-heading {\n"
        "    font-size: 18pt;\n"
        "    font-weight: normal;\n"
        "    letter-spacing: 0.04em;\n"
        "    margin-bottom: 8mm;\n"
        "    padding-bottom: 3mm;\n"
        f"    border-bottom: 1px solid {rule};\n"
        f"    color: {fg};\n"
        "}\n"
        ".toc-h2 {\n"
        "    display: flex;\n"
        "    align-items: baseline;\n"
        "    font-size: 10.5pt;\n"
        "    font-weight: normal;\n"
        f"    color: {fg};\n"
        "    margin-top: 3.5pt;\n"
        "    margin-bottom: 1.5pt;\n"
        "}\n"
        ".toc-title {\n"
        "    flex: 0 1 auto;\n"
        "    max-width: 88%;\n"
        "}\n"
        ".toc-page {\n"
        "    flex-shrink: 0;\n"
        "    padding-left: 4pt;\n"
        "    font-style: normal;\n"
        "    font-variant-numeric: tabular-nums;\n"
        "}\n"
        ".toc-dots {\n"
        "    flex: 1;\n"
        f"    border-bottom: 1px dotted {muted};\n"
        "    margin: 0 4pt;\n"
        "    position: relative;\n"
        "    top: -2pt;\n"
        "    min-width: 8pt;\n"
        "}\n"
        ".toc-h3 {\n"
        "    display: flex;\n"
        "    align-items: baseline;\n"
        "    font-size: 9pt;\n"
        f"    color: {h3color};\n"
        "    padding-left: 10mm;\n"
        "    margin-top: 1pt;\n"
        "    margin-bottom: 1pt;\n"
        "    font-style: italic;\n"
        "}\n"
    )

    html = (
        '<!DOCTYPE html>\n<html>\n<head>\n<meta charset="UTF-8">\n'
        f"<style>\n{css}</style>\n</head>\n<body>\n"
        '<div class="page">\n'
        '  <p class="toc-heading">Table of Contents</p>\n'
        f"{body}\n"
        "</div>\n</body>\n</html>\n"
    )

    html_path = os.path.join(tmp_dir, "toc.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    return html_path


# ---------------------------------------------------------------------------
# Locating headings in the built body PDF (for ToC page numbers)
# ---------------------------------------------------------------------------

def locate_heading_pages(
    pdf_path: Path, headings: list[tuple[int, str]]
) -> list[int | None]:
    """Return the 1-based page each (level, title) heading starts on in pdf_path.

    Uses pdftotext (poppler, already required by convert.py) and matches each
    heading, in document order, against a whole line (or up to 3 consecutive
    wrapped lines), so a passing mention in body text can't be mistaken for
    the heading. Headings that can't be found get None: the ToC row then shows
    dots only, and a warning is printed.
    """
    def norm(s: str) -> str:
        s = unicodedata.normalize("NFKC", s).replace("­", "")
        s = (s.replace("‘", "'").replace("’", "'")
               .replace("“", '"').replace("”", '"')
               .replace("–", "-").replace("—", "-"))
        return " ".join(s.split()).casefold()

    raw = subprocess.run(
        ["pdftotext", "-enc", "UTF-8", str(pdf_path), "-"],
        check=True, capture_output=True,
    ).stdout.decode("utf-8", "replace")

    lines: list[tuple[int, str]] = []
    for page_no, page_text in enumerate(raw.split("\f"), start=1):
        for line in page_text.splitlines():
            n = norm(line)
            if n:
                lines.append((page_no, n))

    result: list[int | None] = []
    missing: list[str] = []
    cursor = 0
    for _level, title in headings:
        target = norm(title)
        hit: tuple[int, int] | None = None
        for j in range(cursor, len(lines)):
            joined = lines[j][1]
            if not target.startswith(joined):
                continue
            for k in range(1, 4):
                if k > 1:
                    if j + k - 1 >= len(lines):
                        break
                    joined = joined + " " + lines[j + k - 1][1]
                    if not target.startswith(joined):
                        break
                if joined == target:
                    hit = (j, k)
                    break
            if hit:
                break
        if hit:
            result.append(lines[hit[0]][0])
            cursor = hit[0] + hit[1]
        else:
            result.append(None)
            missing.append(title)

    found = len(headings) - len(missing)
    print(f"  Located {found}/{len(headings)} headings in the body PDF.", flush=True)
    for t in missing:
        print(f"  Warning: no page found for heading: {t!r}", file=sys.stderr)
    return result


# ---------------------------------------------------------------------------
# Shared Chromium render helper
# ---------------------------------------------------------------------------

def _render_html_to_pdf(
    browser: Path, html_path: str, pdf_path: str, ci: bool = False
) -> None:
    """Render a local HTML file to PDF via headless Chromium."""
    cmd = [
        str(browser),
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--print-background",
        "--no-margins",
        f"--print-to-pdf={pdf_path}",
        Path(html_path).resolve().as_uri(),
    ]
    if ci:
        cmd[1:1] = ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
    subprocess.run(cmd, check=True, capture_output=True, timeout=120)


# ---------------------------------------------------------------------------
# Front matter assembly: cover + ToC prepended to body PDF
# ---------------------------------------------------------------------------

def prepend_front_matter(
    browser: Path,
    pdf_path: Path,
    is_dark: bool,
    page_source: Path | None = None,
) -> Path:
    """Render cover + ToC and prepend them to pdf_path in-place.

    - Cover HTML is sourced from convert.py (single definition).
    - ToC headings are parsed from docs/guide/index.md.
    - Merged order: cover -> toc -> body, via a single qpdf call.
    """
    sys.path.insert(0, str(repo_root() / "scripts"))
    from convert import create_cover_page  # noqa: PLC0415

    guide_md = repo_root() / "docs" / "guide" / "index.md"
    ci       = bool(os.environ.get("CI"))

    print("  Parsing ToC headings...", flush=True)
    headings = parse_toc_headings(guide_md)
    n_h2 = sum(1 for l, _ in headings if l == 2)
    n_h3 = sum(1 for l, _ in headings if l == 3)
    print(f"  Found {len(headings)} headings ({n_h2} H2, {n_h3} H3).", flush=True)

    # Page numbers come from a text-bearing body PDF: pdf_path itself for the
    # light build; the cached light body for dark (its pages are rasterised).
    pages = locate_heading_pages(page_source or pdf_path, headings)

    with tempfile.TemporaryDirectory() as tmp:
        print("  Rendering cover page...", flush=True)
        cover_html = create_cover_page(tmp, is_dark=is_dark)
        cover_pdf  = os.path.join(tmp, "cover.pdf")
        _render_html_to_pdf(browser, cover_html, cover_pdf, ci=ci)

        print("  Rendering ToC page...", flush=True)
        toc_pdf = os.path.join(tmp, "toc.pdf")

        def _render_toc(scale: float) -> int:
            html_path = create_toc_html(tmp, headings, pages, is_dark=is_dark, scale=scale)
            _render_html_to_pdf(browser, html_path, toc_pdf, ci=ci)
            return int(subprocess.run(
                ["qpdf", "--show-npages", toc_pdf],
                check=True, capture_output=True, text=True,
            ).stdout.strip())

        # If the ToC spills onto an extra page, shrink it a little at a time
        # (down to 85%) until it fits in one page fewer; otherwise keep 100%.
        toc_pages = _render_toc(1.0)
        if toc_pages > 1:
            for scale in (0.97, 0.94, 0.91, 0.88, 0.85):
                if _render_toc(scale) < toc_pages:
                    print(f"  ToC scaled to {scale:.0%} to save a page.", flush=True)
                    break
            else:
                _render_toc(1.0)

        merged = str(pdf_path.parent / f".{pdf_path.name}.with-front")
        subprocess.run(
            ["qpdf", "--empty", "--pages",
             cover_pdf, toc_pdf, str(pdf_path),
             "--", merged],
            check=True,
        )

    Path(merged).replace(pdf_path)
    return pdf_path


def build_dark_pdf(browser: Path, body_pdf: Path, dark_pdf: Path) -> Path:
    """Convert a body-only PDF to dark mode, then prepend fresh front matter."""
    convert_script = repo_root() / "scripts" / "convert.py"
    print(f"Converting {body_pdf.name} -> {dark_pdf.name} (dark mode)...")
    subprocess.run(
        [sys.executable, str(convert_script), str(body_pdf), str(dark_pdf)],
        check=True,
    )
    return prepend_front_matter(browser, dark_pdf, is_dark=True, page_source=body_pdf)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

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
    mode.add_argument("--dark", action="store_true",
                      help="Dark PDF only (requires a body-only cache from a prior light build)")
    mode.add_argument("--both", action="store_true",
                      help="Build light PDF, then dark PDF")
    args = ap.parse_args()

    build_light = not args.dark
    build_dark  = args.dark or args.both
    body_cache = args.pdf_light.parent / f".{args.pdf_light.stem}.body.pdf"

    browser = find_chromium_executable()
    if not browser:
        print(
            "No Chromium-based browser found (Chrome, Edge, or Chromium). "
            "Install Google Chrome or Microsoft Edge, or add Chromium to PATH.",
            file=sys.stderr,
        )
        return 1

    # --- Light PDF ---
    if build_light:
        guide_html = args.site_dir / "guide" / "index.html"

        if not args.skip_mkdocs:
            run_mkdocs(args.site_dir)

        if not guide_html.is_file():
            print(f"Missing {guide_html}; run without --skip-mkdocs first.", file=sys.stderr)
            return 1

        out_light = print_to_pdf(browser, guide_html, args.pdf_light)
        print("  Stamping page numbers...", flush=True)
        stamp_page_numbers(out_light)

        import shutil as _shutil  # noqa: PLC0415
        body_cache.parent.mkdir(parents=True, exist_ok=True)
        _shutil.copy2(out_light, body_cache)

        out_light = prepend_front_matter(browser, out_light, is_dark=False)
        size_kb = out_light.stat().st_size // 1024
        print(f"Wrote {out_light.resolve()} ({size_kb} KiB) [Light Mode]")

    # --- Dark PDF ---
    if build_dark:
        if not body_cache.exists():
            print(
                f"No body-only PDF cached at {body_cache}. "
                "Run with --both (or a plain light build first) so a fresh "
                "body-only copy exists before converting to dark mode.",
                file=sys.stderr,
            )
            return 1

        out_dark = build_dark_pdf(browser, body_cache, args.pdf_dark)
        size_kb = out_dark.stat().st_size // 1024
        print(f"Wrote {out_dark.resolve()} ({size_kb} KiB) [Dark Mode]")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
