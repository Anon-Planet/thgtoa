---
title: "Release Notes"
description: "Release Notes"
schema:
  "@context": https://schema.org
  "@type": Organization
  "@id": https://www.anonymousplanet.org/
  name: Anonymous Planet
  url: https://www.anonymousplanet.org/authors/
  logo: ../media/profile.png
  sameAs:
    - https://github.com/Anon-Planet
    - https://opencollective.com/anonymousplanetorg
    - https://mastodon.social/@anonymousplanet
---

# Release Notes

Notable changes to the guide and its tooling. Follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v1.2.3] — 2026-05-22

CI/CD pipeline split into independent stages, dark PDF quality improved, and the changelog is now updated automatically on every release. v1.2.2 was just a placeholder, this is a minor but CI breaking change.

!!! success "Added"

    - **Dark mode PDF** (`scripts/convert.py`): pixel-level converter replaces the broken `--prefers-color-scheme=dark` Chromium flag. Produces a 200 DPI hacker-themed PDF (`#1f1f31` background, `#e0e0e0` text, `#5e8bde` links) with batched page processing to avoid OOM.
    - **Three independent CI workflows** replacing the old monolithic `build-sign-release.yml`:
        - `build.yml` — builds PDFs and uploads them as an artifact; no secrets required.
        - `sign.yml` — downloads the PDF artifact, computes SHA-256 and BLAKE2b hashes, GPG-signs all outputs, and uploads a `signatures` artifact. Can be re-run against any historical build.
        - `release.yml` — downloads both artifacts, uploads to VirusTotal, and publishes a tagged GitHub Release with all 12 assets attached. **Can be triggered manually against any previous sign run**.
    - **`scripts/update_changelog.py`**: reads `git log` since the last version tag, categorises commits by conventional-commit prefix, and prepends a new entry here automatically after each successful build.
    - **`changelog.yml`** workflow: commits the auto-generated changelog entry back to `main` after every build, with `dry_run` and `manual_version` dispatch inputs for testing.

!!! warning "Changed"

    - `build-sign-release.yml` is now deprecated — push triggers removed, manual dispatch only. Will be deleted once in-flight runs complete.
    - The full pipeline (build → sign → release) now chains automatically via `workflow_run` on every push to `main`.
    - GPG signing uses `--pinentry-mode loopback` and `--passphrase-fd 0` to avoid interactive prompts on headless runners.
    - VirusTotal scans moved to the release stage so they run once per release, not once per build.

!!! bug "Fixed"

    - Broken internal links and a mismatched cross-reference in `docs/about/index.md`.
    - Deprecated ODT section commented out in Appendix A6 of the guide.

---

## [v1.2.1] — 2025

First automated PDF build and the start of the CI pipeline.

!!! success "Added"

    - `scripts/build_guide_pdf.py`: builds the MkDocs site and renders the full guide to a single PDF via headless Chromium (Chrome or Edge). Supports `--dark`, `--light`, and `--both` modes.
    - GitHub Actions workflow that installs Chromium, runs the build script, and uploads `export/thgtoa.pdf` as an artifact on every push to `main` or manual dispatch.
    - `docs/stylesheets/extra.css` for shared site styling.
    - This changelog.

!!! warning "Changed"

    - `README.md` updated with instructions for local PDF export and a note about the GitHub Actions artifact.
    - `.gitignore` updated to exclude local build outputs (`export/`, `site/`, `_site_test/`).

!!! bug "Fixed"

    - Broken reference-style internal links throughout `docs/guide/index.md` replaced with correct fragment links.
    - Broken footnote marker on the "free (unallocated) space" list item in the guide.

---

[v1.2.3]: https://github.com/Anon-Planet/thgtoa/releases/tag/v1.2.3
[v1.2.1]: https://github.com/Anon-Planet/thgtoa/releases/tag/v1.2.1
