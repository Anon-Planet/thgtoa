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

## [v1.2.3]

CI/CD pipeline split into independent stages, dark PDF quality improved, release signing automated, and the changelog now updates itself on every build. Skipping v1.2.2 which was a placeholder and contained broken Python unsuitable for a tag/release.

???+ tip "Added"

    - **Dark mode PDF** (`scripts/convert.py`): pixel-level converter replaces the broken `--prefers-color-scheme=dark` Chromium flag. Produces a 200 DPI hacker-themed PDF (`#1f1f31` background, `#e0e0e0` text, `#5e8bde` links) with batched page processing to avoid OOM on large documents.
    - **Three independent CI workflows** replacing the old monolithic `build-sign-release.yml`:
        - `build.yml`: builds PDFs and uploads them as an artifact; no secrets required, can be re-run freely.
        - `sign.yml`: downloads the PDF artifact, computes SHA-256 and BLAKE2b hashes, GPG-signs all outputs, and uploads a `signatures` artifact. Can be re-run against any historical build.
        - `release.yml`: downloads both artifacts, uploads to VirusTotal, and publishes a tagged GitHub Release with all 12 assets attached. Can be triggered manually against any previous sign run.
    - **`scripts/update_changelog.py`**: reads `git log` since the last version tag, categorises commits by conventional-commit prefix, and prepends a new entry to this file automatically after each successful build.
    - **`changelog.yml`** workflow: commits the auto-generated changelog entry back to `main` after every build, with `dry_run` and `manual_version` dispatch inputs for safe local testing.
    - **`scripts/tag_release.py`**: interactive guided helper for maintainers to create GPG-signed annotated tags. Checks clean tree and branch, auto-increments the version, pulls the message from the changelog, resolves the release signing key, creates and verifies the tag, then prints the push command.
    - **`docs/code/develop.md`**: full developer reference covering prerequisites, local build instructions, the pipeline flow, all required GitHub Secrets, the release process, verification steps, and a troubleshooting section for every known CI failure mode.

!!! warning "Changed"

    - `build-sign-release.yml` deprecated - push triggers removed, manual dispatch only. Will be deleted once in-flight runs complete.
    - The full pipeline (build → sign → release → changelog) now chains automatically via `workflow_run` on every push to `main`.
    - GPG signing uses `--pinentry-mode loopback` and `--passphrase-fd 0` to avoid interactive prompts on headless runners.
    - VirusTotal scans moved to the release stage so they run once per release, not once per build.
    - `.gitignore` updated to track `.b2` per-file hash files alongside existing `.sha256` and `.sig` entries.
    - Stale information removed from the guide; deprecated ODT section in Appendix A6 commented out.
    - Footer copyright information corrected.

!!! bug "Fixed"

    - `_save_images_as_pdf` in `convert.py` was passing raw PNG files to `qpdf --pages`, which only accepts PDF inputs. Fixed by quantizing each page to palette mode (256 colours, FASTOCTREE) and saving as a single-page PDF before merging.
    - `convert.py` now fails immediately with install instructions if `pdftoppm` or `qpdf` are missing, instead of crashing with an unhelpful `FileNotFoundError`.
    - Pillow `KeyError: 'JPEG'` on CI resolved by installing `mkdocs-material[imaging]` and using palette-mode PDF encoding instead of RGB+JPEG.
    - Orphaned footnote citations `[^536]` and `[^537]` (Australian privacy law and the Identify and Disrupt Act) restored at the key disclosure law paragraph in the guide.
    - Broken internal links and mismatched cross-references throughout the guide corrected.

---

## [v1.2.1]

First automated PDF build and the start of the CI pipeline.

???+ tip "Added"

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
