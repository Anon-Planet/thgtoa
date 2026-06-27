#!/usr/bin/env python3
"""Build light-mode PDF with MkDocs + Chromium, then produce dark-mode PDF via convert.py.

Usage:
  python scripts/build_guide_pdf.py                    # Light PDF only (clean light theme)
  python scripts/build_guide_pdf.py --dark             # Dark PDF only (requires light PDF to exist)
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
import subprocess
import sys
import tempfile
import time
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


def create_toc_html(tmp_dir: str, headings: list[tuple[int, str]], is_dark: bool) -> str:
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
    for level, title in headings:
        safe = _html_mod.escape(title)
        if level == 2:
            rows.append(
                f'<div class="toc-h2">'
                f'<span class="toc-title">{safe}</span>'
                f'<span class="toc-dots"></span>'
                f"</div>"
            )
        else:
            rows.append(f'<div class="toc-h3">{safe}</div>')

    body = "\n".join(rows)

    css = (
        "* { box-sizing: border-box; margin: 0; padding: 0; }\n"
        "@page { size: A4; margin: 0; }\n"
        "html, body {\n"
        f"    width: 210mm;\n"
        f"    background: {bg};\n"
        f"    color: {fg};\n"
        "    font-family: 'EB Garamond', Georgia, 'Times New Roman', serif;\n"
        "}\n"
        ".page {\n"
        "    width: 210mm;\n"
        "    min-height: 297mm;\n"
        "    padding: 25mm 28mm 28mm 28mm;\n"
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
        "    white-space: nowrap;\n"
        "    overflow: hidden;\n"
        "    flex-shrink: 0;\n"
        "    max-width: 85%;\n"
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

def prepend_front_matter(browser: Path, pdf_path: Path, is_dark: bool) -> Path:
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

    with tempfile.TemporaryDirectory() as tmp:
        print("  Rendering cover page...", flush=True)
        cover_html = create_cover_page(tmp, is_dark=is_dark)
        cover_pdf  = os.path.join(tmp, "cover.pdf")
        _render_html_to_pdf(browser, cover_html, cover_pdf, ci=ci)

        print("  Rendering ToC page...", flush=True)
        toc_html = create_toc_html(tmp, headings, is_dark=is_dark)
        toc_pdf  = os.path.join(tmp, "toc.pdf")
        _render_html_to_pdf(browser, toc_html, toc_pdf, ci=ci)

        merged = str(pdf_path.parent / f".{pdf_path.name}.with-front")
        subprocess.run(
            ["qpdf", "--empty", "--pages",
             cover_pdf, toc_pdf, str(pdf_path),
             "--", merged],
            check=True,
        )

    Path(merged).replace(pdf_path)
    return pdf_path


# ---------------------------------------------------------------------------
# Dark PDF build (delegates to convert.py which adds its own front matter)
# ---------------------------------------------------------------------------

def build_dark_pdf(light_pdf: Path, dark_pdf: Path) -> Path:
    """Convert the light PDF to dark mode using scripts/convert.py."""
    convert_script = repo_root() / "scripts" / "convert.py"
    print(f"Converting {light_pdf.name} -> {dark_pdf.name} (dark mode)...")
    subprocess.run(
        [sys.executable, str(convert_script), str(light_pdf), str(dark_pdf)],
        check=True,
    )
    return dark_pdf


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
                      help="Dark PDF only (light PDF must already exist)")
    mode.add_argument("--both", action="store_true",
                      help="Build light PDF, then dark PDF")
    args = ap.parse_args()

    build_light = not args.dark
    build_dark  = args.dark or args.both

    # --- Light PDF ---
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
        out_light = prepend_front_matter(browser, out_light, is_dark=False)
        size_kb = out_light.stat().st_size // 1024
        print(f"Wrote {out_light.resolve()} ({size_kb} KiB) [Light Mode]")

    # --- Dark PDF ---
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
