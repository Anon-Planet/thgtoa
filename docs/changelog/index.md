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

## [v2.0.1]

!!! Note "Meta"

    - Released 2026-05-24 from [`c658c35`](https://github.com/Anon-Planet/thgtoa/commit/c658c354ee0b982163167a7ac7106a0bf16465ed)

!!! Note "Added"

    - Add tag_release.py — guided signed release tagger
    - How to verify the authenticity of our files and check virus scans

!!! Note "Changed"

    - Rewrite developer guide for current pipeline
    - 8/8 chore(bump): v1.2.3
    - 8/8 chore(scripts): minor cleanup to setup_workflow.py
    - 7/8 docs(guide): bump version string to v1.2.3
    - 6/8 chore: track .b2 hash files in .gitignore
    - 5/8 docs(changelog): rewrite for v1.2.3 — consolidate and clean up
    - 4/8 ci: add automated changelog update workflow
    - 3/8 ci: split monolithic workflow into build, sign, release stages
    - 2/8 refactor(pdf): wire dark mode through convert.py
    - 1/8 feat(pdf): add pixel-based dark mode PDF converter
    - Refactor pipeline into independent build/sign/release/changelog workflows
    - Submit actual develop page
    - Fix copy information in website footer
    - Fix some broken YAML references
    - Delete stale information
    - Sign local copy
    - Tweaking some of the build to function
    - Tweaking some of the build to function
    - Tweaking some of the build to function
    - Tweaking some of the build to function
    - Tweaking some of the build to function
    - Tweaking some of the build to function
    - Tweaking some of the build to function pt6
    - Tweaking some of the build to function pt5
    - Tweaking some of the build to function pt4
    - Tweaking some of the build to function pt3
    - Tweaking some of the build to function pt2
    - Tweaking some of the build to function
    - Moving some things around
    - One job to rule them all
    - Forgot to add flag
    - The GPG bit fails, let's try again pt2
    - The GPG bit fails, let's try again
    - Move out some scripts
    - Combined actions refactor
    - Combined actions into one file for less overhead
    - Overhaul the Hashing, scanning, release management
    - Overhaul the Hashing, scanning, release management
    - Refactor build action
    - Slightly refactor the workflow task
    - Fix README
    - Build pipeline WIP
    - Refactoring the VT job
    - Downgrade to working versions to fix broken jobs
    - Appendix A6: comment out deprecated ODT information
    - Replace broken internal link with correct rel path
    - Add nav in mkdocs.yml config
    - Fix broken link to page
    - Update VT scan workflow
    - Use VT v5.x
    - Add VirusTotal scans for submitted PDFs
    - Fix path
    - Refactor PDF build in CI, add dark mode PDF (pt 4)
    - Fix PDF build in CI
    - Fix PDF build in CI
    - Archive Matrix database and shutdown
    - The Tor onion v3 address works
    - Fix
    - Revert "Fix some metadata"
    - File endings
    - Missing parenthesis
    - Extra parenthesis
    - Creating your anonymous online identities
    - Traffic anonymization
    - OPSEC thoughts
    - Watermarking
    - Browser and device fingerprinting
    - Requirements refs
    - Local data leaks, forensics
    - Whonix virtual machines
    - Some more
    - Adversarial considerations (threats)
    - Some more
    - Some Tails refs
    - Some additional measures against forensics refs
    - Comparing versions ref
    - Persistent plausible deniability
    - All refs I have time for at the moment
    - Fix some metadata
    - Update admin info in Matrix listing
    - Fix some metadata
    - Fix discussion channels
    - Fix nope's Matrix pushed to only one repo
    - Fix Das' Matrix pushed to only one repo
    - Remove commitizen requirement
    - Remove than/nope signed canary
    - Upgrade pre-commit hooks
    - Wikiless.org --> Wikiless.com
    - Minor updated information
    - Still broken, try again
    - Fix workflow
    - Missing README.md
    - Fix some references and tidy up language
    - Cleanup old remnants
    - Sample publishing config
    - Move CNAME to docs
    - Add CNAME
    - Remove old site artifacts
    - Fix some absolute links
    - Add Blackhat USA 2024 conference on Wi-Fi dangers
    - Add Blackhat USA 2024 conference on Wi-Fi dangers
    - Formatting and tooling upgrades to improve performance

!!! Note "Fixed"

    - Actually save per-page PDFs for qpdf, not PNGs
    - Fail fast with helpful message if pdftoppm or qpdf missing
    - Resolve Pillow JPEG KeyError and cairosvg missing dep

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
