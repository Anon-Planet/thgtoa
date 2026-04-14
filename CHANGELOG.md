# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Refactored GitHub Actions workflow **Build guide PDF** (`scripts\build_guide_pdf.py`): now builds both light and dark mode PDFs (`export/thgtoa.pdf` and `export/thgtoa-dark.pdf` respectively).

## [1.2.1] - 2026-04-11

### Added

- GitHub Actions workflow **Build guide PDF** (`.github/workflows/build-pdf.yml`): installs Chromium on `ubuntu-latest`, runs `scripts/build_guide_pdf.py`, uploads `export/guide.pdf` as the `guide-pdf` artifact. Runs on `workflow_dispatch`, on pushes to `main` that touch docs or build inputs, and on matching pull requests.

- `scripts/build_guide_pdf.py` to build the MkDocs site and render the guide to a single PDF (`export/guide.pdf` by default) using a Chromium-based browser (Chrome or Edge) headless print-to-PDF.
- `docs/stylesheets/extra.css` and `extra_css` in `mkdocs.yml` for shared site styling.
- This `CHANGELOG.md`.

### Changed

- `README.md` “Ways to read or export the guide”: hosted link, local `mkdocs serve`, PDF build via the script, ODT note, raw Markdown link.
- Guide landing layout: wrap the opening block in `docs/guide/index.md` with a `guide-intro-lead` container so the logo and first sections share one layout context for web and print.
- `.gitignore` to exclude local build outputs `export/`, `site/`, and `_site_test/`.
- `scripts/build_guide_pdf.py`: when the `CI` environment variable is set, pass Chromium flags (`--no-sandbox`, `--disable-setuid-sandbox`, `--disable-dev-shm-usage`) so headless print works on typical CI images.
- `README.md`: note the **Build guide PDF** GitHub Actions workflow and the `guide-pdf` artifact.

### Fixed

- `docs/guide/index.md`: replace broken reference-style internal links (`[label][label:]`) with working same-page fragment links to the correct headings; correct the mismatched “Real-Name System” cross-reference; fix a broken footnote marker on the “free (unallocated) space of your hard drive” list item.

[Unreleased]: https://github.com/Anon-Planet/thgtoa/compare/v1.2.1...HEAD
[1.2.1]: https://github.com/Anon-Planet/thgtoa/releases/tag/v1.2.1
