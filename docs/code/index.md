---
title: "Content Contributions"
description: "How to contribute to the Hitchhiker's Guide — building, signing, releasing, and writing."
hide:
  - toc
schema:
  "@context": https://schema.org
  "@type": Organization
  "@id": https://anonymousplanet.net/
  name: Anonymous Planet
  url: https://anonymousplanet.net/code/
  logo: ../media/profile.png
  sameAs:
    - https://github.com/Anon-Planet
    - https://opencollective.com/anonymousplanetorg
---

<div class="hero-block">
  <div class="hero-eyebrow">Open source. Every PR matters.</div>
  <h1 class="hero-title">Contribute<span class="hero-subtitle">Help us improve the Hitchhiker's Guide..</span></h1>
  <p class="hero-tagline">
    Contributions range from fixing a typo to writing entire new sections.
  </p>
  <div class="hero-cta-row">
    <a href="https://github.com/Anon-Planet/thgtoa/issues/new" class="hero-cta hero-cta--primary">Open an Issue</a>
    <a href="#pipeline" class="hero-cta hero-cta--secondary">Release Pipeline</a>
  </div>
</div>

---

## Setup { #setup }

Install these before anything else.

=== "Linux / macOS"

    ```sh
    # Python 3.11+
    python3 --version

    # poppler (pdftoppm) and qpdf
    sudo apt install poppler-utils qpdf # Debian/Ubuntu
    brew install poppler qpdf           # macOS

    # GPG
    sudo apt install gnupg # Debian/Ubuntu
    brew install gnupg     # macOS

    # Python dependencies
    pip install "mkdocs-material[imaging]" pillow numpy
    ```

=== "Windows"

    ```powershell
    # Python 3.11+ from https://python.org

    # poppler: https://github.com/oschwartz10612/poppler-windows/releases
    # Extract and add the bin\ folder to PATH

    # qpdf: https://github.com/qpdf/qpdf/releases
    # Extract and add the bin\ folder to PATH

    # GPG: https://gpg4win.org

    # Python dependencies
    pip install "mkdocs-material[imaging]" pillow numpy
    ```

You also need **Google Chrome** or **Microsoft Edge** installed for the light-mode PDF build (headless Chromium).

---

## Repository Layout { #layout }

```txt
.github/
  workflows/
    01-build.yml      # builds PDFs, uploads artifact
    02-sign.yml       # hashes + GPG signs, uploads signatures artifact
    03-release.yml    # publishes GitHub Release with all assets
    04-changelog.yml  # prepends a new entry to docs/changelog/index.md
    publish.yml       # deploys MkDocs site to GitHub Pages
docs/
  guide/index.md      # the guide (single Markdown file)
  changelog/          # release notes
  code/               # this page
export/               # PDF output (PDFs gitignored; .sha256, .b2sum, .asc tracked)
pgp/                  # public signing keys
scripts/
  build_guide_pdf.py  # MkDocs + Chromium PDF builder
  convert.py          # pixel-based dark mode PDF converter
  install_fonts.py    # install fonts locally
  update_changelog.py # auto-generates changelog entries from git log
  setup_workflow.py   # GitHub Secrets setup assistant
  verify_pdf.py       # signature verification helper
  archived/
    tag_release.py    # ARCHIVED — GPG tag helper (not used in current flow)
```

---

## Building Locally { #build }

```sh
python scripts/build_guide_pdf.py --both
```

Builds the MkDocs site, renders it to `export/thgtoa.pdf` via headless Chromium, then produces `export/thgtoa-dark.pdf`.

| Flag | Effect |
|------|--------|
| `--both` | Light PDF then dark PDF |
| _(none)_ | Light PDF only |
| `--dark` | Dark PDF only (light PDF must already exist) |

Build only the dark PDF from an existing light:

```sh
python scripts/convert.py export/thgtoa.pdf export/thgtoa-dark.pdf
```

| Flag | Default | Description |
|------|---------|-------------|
| `--dpi` | `200` | Rasterization DPI |
| `--batch-size` | `50` | Pages per batch — reduce if OOM |
| `--bg` | `1f1f31` | Background colour (hex) |
| `--text` | `e0e0e0` | Body text colour (hex) |
| `--link` | `5e8bde` | Link colour (hex) |

Preview the site:

```sh
mkdocs serve
# Opens at http://127.0.0.1:8000
```

---

## Contributing Content { #contributing }

<div class="index-grid">

  <div class="index-card">
    <h3 class="index-card__title">Use a Topic Branch</h3>
    <p class="index-card__body">Never commit directly to <code>main</code>. Use a topic branch per change so PRs stay reviewable and independent.</p>
  </div>

  <div class="index-card">
    <h3 class="index-card__title">Small PRs</h3>
    <p class="index-card__body">Split large changes into multiple PRs — one for new content, one for fixes, one for style. Big PRs block merges and create review debt.</p>
  </div>

  <div class="index-card">
    <h3 class="index-card__title">Conventional Commits</h3>
    <p class="index-card__body">All commits must follow <code>&lt;type&gt;(&lt;scope&gt;): &lt;description&gt;</code> format. Enforced by the <code>commitizen</code> pre-commit hook.</p>
  </div>

  <div class="index-card">
    <h3 class="index-card__title">Describe Your Changes</h3>
    <p class="index-card__body">Never leave a PR description blank. Include what changed, why, and any context a reviewer needs. Link related issues.</p>
  </div>

</div>

### Commit Types

| Type | Changelog bucket |
|------|-----------------|
| `feat`, `feature`, `add` | Added |
| `fix`, `bugfix`, `revert`, `security` | Fixed |
| `perf`, `refactor`, `change`, `chore`, `ci`, `docs`, `style`, `test`, `build` | Changed |

Examples:

```sh
feat: add dark-mode PDF export
fix(scripts): handle locked PDF on Windows
docs: update developer workflow guide
chore(ci): pin Chrome version to 120
```

### Rules

- **Do** target PRs at the `main` branch
- **Do** write "WIP" or open a draft PR for unfinished work
- **Do** follow the [50/72 rule](http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html) for commit messages
- **Don't** make mass search/replace changes without context-checking every instance
- **Don't** abandon a PR mid-review — stay responsive
- **Don't** modify a PR directly while it's under active review — submit changes to the review branch instead

For an example of what _not_ to do, see [PR #51](https://github.com/Anon-Planet/thgtoa/pull/51).

!!! warning "Before you push"
    - Make sure the working tree is clean (`git status`)
    - Run `mkdocs build` locally if you changed `docs/` to catch broken links
    - If you added footnotes, verify each has both a definition `[^N]:` and at least one inline citation `[^N]`

---

## Release Pipeline { #pipeline }

The pipeline is fully manual after the initial build — no step triggers the next automatically. This prevents version mismatches between what was built, what was signed, and what gets released.

```txt
push to main  (or manual trigger)
      │
      ▼
  01-build.yml
  Builds thgtoa.pdf + thgtoa-dark.pdf.
  Uploads artifact: pdfs — note the run ID.
      │
      │  manually trigger 02-sign.yml with the build run ID
      ▼
  02-sign.yml
  Hashes (SHA-256 + BLAKE2b) and GPG-signs all files.
  Commits export/ back to main.
  Uploads: signatures, pdfs-signed — note the run ID.
      │
      │  manually trigger 03-release.yml with the sign run ID
      ▼
  03-release.yml
  Runs VirusTotal. Creates GitHub Release tagged release-YYYYMMDD-<short-sha>.
      │
      │  manually trigger 04-changelog.yml with the version string
      ▼
  04-changelog.yml
  Prepends a new ## [vX.Y.Z] entry to docs/changelog/index.md and commits.
```

### Release Tags

Tags use the format `release-YYYYMMDD-<short-sha>`, e.g. `release-20260527-abc1234`. No version decision is needed at release time — the tag is always unique and traceable to the exact commit.

The version string (e.g. `v1.2.4`) is a separate, human-assigned label that lives only in the changelog.

### Triggering Each Step

**Build:** Push to `main` or go to **Actions → Build PDFs → Run workflow**. Note the run ID.

**Sign:** **Actions → Sign PDFs → Run workflow**, enter the build run ID. Note the run ID.

**Release:** **Actions → Release → Run workflow**, enter the sign run ID.

**Changelog:** **Actions → Update Changelog → Run workflow**, enter the version string. Use `dry_run: true` to preview.

---

## Verifying a Release { #verify }

```sh
# Import the release signing key
gpg --import pgp/anonymousplanet.asc

# Verify the PDFs
gpg --verify thgtoa.pdf.asc      thgtoa.pdf
gpg --verify thgtoa-dark.pdf.asc thgtoa-dark.pdf

# Verify the hash files
gpg --verify sha256sums.txt.asc sha256sums.txt
gpg --verify b2sums.txt.asc     b2sums.txt

# Check the PDF hashes match
sha256sum -c sha256sums.txt
b2sum     -c b2sums.txt
```

Expected output:

```txt
gpg: Signature made Sun 31 May 2026 03:23:26 AM EDT
gpg:                using EDDSA key C3023DBEA3FB38C438BA1EEDCEC60AEDE8B992A2
gpg: Good signature from "Anonymous Planet Release Signing Key" [ultimate]
Primary key fingerprint: C302 3DBE A3FB 38C4 38BA  1EED CEC6 0AED E8B9 92A2
```

You can safely ignore GitHub/Codeberg warnings like "The email in this signature doesn't match the committer email."

---

## Troubleshooting { #troubleshooting }

**`cairosvg` missing during MkDocs build**
`pip install "mkdocs-material[imaging]"` — required by the `social` plugin.

**`KeyError: 'JPEG'` in convert.py**
`sudo apt install libjpeg-dev && pip install --force-reinstall pillow`

**`qpdf: can't find PDF header`**
qpdf only accepts PDF inputs — ensure you are on the current version of `convert.py`.

**GPG signing fails — `No secret key`**
Re-export: `gpg --armor --export-secret-keys <fingerprint>` and re-paste the full block including headers into the `GPG_PRIVATE_KEY` secret.

**GPG signing fails — `Bad passphrase`**
The `GPG_PASSPHRASE` secret has a trailing space or newline. Re-paste without surrounding whitespace.

**`03-release.yml` fails on VirusTotal**
`VT_API_KEY` is missing, invalid, or over the 500 req/day free-tier limit. Re-run after a few minutes.

**`02-sign.yml` fails downloading PDF artifact**
Wrong `build_run_id`, or the artifact expired (90-day retention). Trigger a new build.

**Changelog already contains version X**
`update_changelog.py` errors if the version is already present. Choose the next version string.

**Footnote warnings — `link '#fnref:N' has no anchor`**
A definition `[^N]:` exists without a matching inline citation. Add the citation or remove the orphaned definition.
