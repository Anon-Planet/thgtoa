# Developer Guide

This page covers everything you need to contribute to the project, run the build pipeline locally, configure GitHub Secrets, and publish a release.

---

## Prerequisites

Install these before anything else.

=== "Linux / macOS"

    ```bash
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

    # poppler: download from https://github.com/oschwartz10612/poppler-windows/releases
    # Extract and add the bin\ folder to PATH

    # qpdf: download from https://github.com/qpdf/qpdf/releases
    # Extract and add the bin\ folder to PATH

    # GPG: download Gpg4win from https://gpg4win.org

    # Python dependencies
    pip install "mkdocs-material[imaging]" pillow numpy
    ```

You also need **Google Chrome** or **Microsoft Edge** installed for the light-mode PDF build (headless Chromium).

---

## Repository layout

```
.github/
  workflows/
    build.yml              # builds PDFs, uploads artifact
    sign.yml               # hashes + GPG signs, uploads signatures artifact
    release.yml            # publishes GitHub Release with all assets
    changelog.yml          # prepends a new entry to docs/changelog/index.md
    publish.yml            # deploys MkDocs site to GitHub Pages
    build-sign-release.yml # DEPRECATED - fails on trigger, kept for reference
docs/
  guide/index.md           # the guide (single Markdown file)
  changelog/               # release notes
  code/                    # this page
export/                    # PDF output (PDFs gitignored; .sha256, .b2sum, .asc tracked)
pgp/                       # public signing keys
scripts/
  build_guide_pdf.py       # MkDocs + Chromium PDF builder
  convert.py               # pixel-based dark mode PDF converter
  update_changelog.py      # auto-generates changelog entries from git log
  setup_workflow.py        # GitHub Secrets setup assistant
  verify_pdf.py            # signature verification helper
  archived/
    tag_release.py         # ARCHIVED - GPG tag helper (not used in current flow)
```

---

## Building locally

### Build both PDFs

```bash
python scripts/build_guide_pdf.py --both
```

This builds the MkDocs site, renders it to `export/thgtoa.pdf` via headless Chromium, then calls `scripts/convert.py` to produce `export/thgtoa-dark.pdf`.

| Flag | Effect |
|------|--------|
| `--both` | Light PDF then dark PDF |
| (no flag) | Light PDF only |
| `--dark` | Dark PDF only (light PDF must already exist) |

### Build only the dark PDF from an existing light PDF

```bash
python scripts/convert.py export/thgtoa.pdf export/thgtoa-dark.pdf
```

Options:

| Flag | Default | Description |
|------|---------|-------------|
| `--dpi` | `200` | Rasterization DPI. 150 = smaller file, 300 = sharper but slow |
| `--batch-size` | `50` | Pages per batch. Reduce if you hit OOM |
| `--bg` | `1f1f31` | Background colour (hex) |
| `--text` | `e0e0e0` | Body text colour (hex) |
| `--link` | `5e8bde` | Link / blue element colour (hex) |

### Preview the MkDocs site

```bash
mkdocs serve
```

Opens at `http://127.0.0.1:8000`.

---

## CI/CD pipeline overview

The pipeline is fully manual after the initial build - no step automatically triggers the next. This prevents version mismatches between what was built, what was signed, and what gets released.

```
push to main  (or manual trigger)
      │
      ▼
  build.yml
  Builds thgtoa.pdf + thgtoa-dark.pdf.
  Uploads artifact: pdfs
  Note the run ID.
      │
      │  # manually trigger sign.yml with the build run ID
      ▼
  sign.yml
  Downloads pdfs artifact. Hashes (SHA-256 + BLAKE2b) and GPG-signs
  all files. Commits export/ back to main. Uploads artifacts:
  signatures, pdfs-signed
  Note the run ID.
      │
      │  # manually trigger release.yml with the sign run ID
      ▼
  release.yml
  Downloads signatures + pdfs-signed artifacts. Runs VirusTotal.
  Creates GitHub Release tagged release-YYYYMMDD-<short-sha>.
      │
      │  # manually trigger changelog.yml with the version string
      ▼
  changelog.yml
  Runs update_changelog.py, prepends a new ## [vX.Y.Z] entry,
  commits back to main.
```

Each stage is independent. If signing fails (e.g. an expired key), re-run only `sign.yml` pointing at the existing build artifact - no need to rebuild the PDFs.

!!! warning "Before you push"

    - Make sure the working tree is clean (`git status`)
    - Run `mkdocs build` locally if you changed `docs/` to catch broken links before CI does
    - If you added new footnotes, verify they have both a definition `[^N]:` and at least one inline citation `[^N]`

---

## Release process (step by step)

### 1. Trigger a build

Push to `main` - `build.yml` runs automatically when `docs/`, `mkdocs.yml`, or `scripts/` change. You can also trigger it manually from **Actions → Build PDFs → Run workflow**.

Once it completes successfully, **note the run ID** from the URL or the Actions list.

---

### 2. Sign the PDFs

Go to **Actions → Sign PDFs → Run workflow**.

| Input | Value |
|-------|-------|
| `build_run_id` | The run ID from step 1 |

`sign.yml` will:

- Download the PDFs artifact from the build run
- Compute SHA-256 and BLAKE2b hashes, writing `thgtoa.pdf.sha256`, `thgtoa.pdf.b2sum`, `sha256sums.txt`, `b2sums.txt`, and the dark equivalents
- GPG-sign all PDFs and hash files, writing `.asc` detached signature files
- Commit the updated `export/` directory back to `main`
- Upload two artifacts: `signatures` and `pdfs-signed`

Once it completes successfully, **note the run ID**.

---

### 3. Publish the release

Go to **Actions → Release → Run workflow**.

| Input | Value |
|-------|-------|
| `sign_run_id` | The run ID from step 2 |
| `prerelease` | `false` for a normal release |

`release.yml` will:

- Download `signatures` and `pdfs-signed` artifacts from the sign run
- Upload both PDFs to VirusTotal
- Auto-generate a release tag in the format `release-YYYYMMDD-<short-sha>` (e.g. `release-20260527-abc1234`)
- Create a GitHub Release with all PDFs, hash files, and signatures attached, and the VirusTotal report URLs in the body

No version number needs to be chosen at this step - the tag is derived from the date and commit SHA, so it is always unique and always traceable.

---

### 4. Update the changelog

Go to **Actions → Update Changelog → Run workflow**.

| Input | Value |
|-------|-------|
| `version` | The human-readable version string, e.g. `v1.2.4` |
| `dry_run` | `true` to preview without committing |

`changelog.yml` runs `scripts/update_changelog.py`, which:

- Reads git log since the last `## [vX.Y.Z]` heading in the changelog
- Categorises commits into Added / Changed / Fixed using conventional-commit prefixes
- Prepends a new `## [version]` admonition block to `docs/changelog/index.md`
- Commits the result back to `main`

The version string is the only human decision in the release process. It goes into the changelog only - it does not affect the release tag.

!!! tip "Previewing the changelog entry"
    Run with `dry_run: true` first to review the generated entry before it is committed.

---

## Release tag format

Release tags use the format `release-YYYYMMDD-<short-sha>`, for example:

```
release-20260527-abc1234
```

This format is always unique, requires no version decision at release time, and is directly traceable to the commit that was built. The version string (e.g. `v1.2.4`) is a separate, human-assigned label that lives only in the changelog.

---

## Commit message format

All commits must follow the [Conventional Commits](https://www.conventionalcommits.org) format. This is enforced by the `commitizen` pre-commit hook.

```
<type>(<scope>): <description>
```

Accepted types and their changelog bucket:

| Type | Bucket |
|------|--------|
| `feat`, `feature`, `add` | Added |
| `fix`, `bugfix`, `revert`, `security` | Fixed |
| `perf`, `refactor`, `change`, `chore`, `ci`, `docs`, `style`, `test`, `build` | Changed |

Examples:

```bash
feat: add dark-mode PDF export
fix(scripts): handle locked PDF on Windows
docs: update developer workflow guide
chore(ci): pin Chrome version to 120
```

---

## GitHub Secrets

Configure these in **Settings → Secrets and variables → Actions** before the pipeline will fully work. The build step requires no secrets; signing and releasing require all of them.

### `GPG_PRIVATE_KEY`

The ASCII-armored private key used to sign PDFs and hash files.

```bash
gpg --armor --export-secret-keys C3023DBEA3FB38C438BA1EEDCEC60AEDE8B992A2
```

Copy the entire output (including `-----BEGIN PGP PRIVATE KEY BLOCK-----` and the closing line) and paste it as the secret value.

!!! danger "Key security"
    This is the release signing key. Only repository admins should have access to it. Never commit it to the repository or share it outside of GitHub Secrets.

### `GPG_PASSPHRASE`

The passphrase protecting the private key above. Must match exactly - no trailing newline.

### `ACTIONS_SSH_SIGNING_KEY`

An SSH private key used by `sign.yml` to sign the commit that pushes `export/` back to `main`. Generate a dedicated key for this:

```bash
ssh-keygen -t ed25519 -C "github-actions signing key" -f actions_signing_key
```

Add the **private key** as the `ACTIONS_SSH_SIGNING_KEY` secret, and the **public key** to the repository's Deploy Keys (Settings → Deploy Keys) with write access.

### `VT_API_KEY`

A [VirusTotal](https://www.virustotal.com) API key with file upload permissions. Used by `release.yml` to scan both PDFs before publishing. Get one by creating a free account at `virustotal.com` → API key under your profile. The free tier (4 lookups/minute, 500/day) is sufficient.

### `CHANGELOG_PAT`

A GitHub Personal Access Token with `contents: write` scope on this repository. Needed because `changelog.yml` commits back to `main` - commits made with the default `GITHUB_TOKEN` do not trigger further workflow runs (GitHub loop-prevention). A PAT bypasses this. If absent, falls back to `GITHUB_TOKEN` - the commit still happens, it just won't trigger downstream workflows.

**Creating one:** GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens → set Contents to Read and write for this repo only.

### Secrets summary

| Secret | Required by | What happens if missing |
|--------|------------|------------------------|
| `GPG_PRIVATE_KEY` | `sign.yml` | Signing step fails - no `.asc` files produced |
| `GPG_PASSPHRASE` | `sign.yml` | GPG import succeeds but signing fails |
| `ACTIONS_SSH_SIGNING_KEY` | `sign.yml` | Export commit is unsigned (may fail if branch protection requires signed commits) |
| `VT_API_KEY` | `release.yml` | VirusTotal step fails - release is not published |
| `CHANGELOG_PAT` | `changelog.yml` | Falls back to `GITHUB_TOKEN` - changelog updates but commit won't trigger downstream workflows |

---

## Verifying a release

Anyone can verify the authenticity of a release download.

```bash
# Import the release signing key
gpg --import pgp/anonymousplanet-release.asc

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

A successful verify looks like:

```
gpg: Signature made ...
gpg: Good signature from "Anonymous Planet (Release) ..."
```

---

## Troubleshooting

**`cairosvg` missing during MkDocs build**
Install the imaging extras: `pip install "mkdocs-material[imaging]"`. Required by the `social` plugin.

**`KeyError: 'JPEG'` in convert.py**
Pillow needs libjpeg. Reinstall after installing the system lib: `sudo apt install libjpeg-dev && pip install --force-reinstall pillow`.

**`qpdf: can't find PDF header`**
Ensure you are on the current version of `convert.py` - qpdf only accepts PDF inputs, not PNG.

**GPG signing fails on CI with `No secret key`**
The `GPG_PRIVATE_KEY` secret is missing or malformed. Re-export with `gpg --armor --export-secret-keys <fingerprint>` and paste the full block including header and footer lines.

**GPG signing fails with `Bad passphrase`**
The `GPG_PASSPHRASE` secret has a trailing space or newline. Paste it again with no surrounding whitespace.

**`release.yml` fails on VirusTotal**
The `VT_API_KEY` is missing, invalid, or over the rate limit (500 requests/day on the free tier). Check the secret and re-run after a few minutes.

**`sign.yml` fails downloading PDF artifact**
The `build_run_id` is wrong, or the artifact has expired (90-day retention). Trigger a new build and use the fresh run ID.

**Changelog already contains version X**
`update_changelog.py` will error if `MANUAL_VERSION` is set to a version already in the changelog. Choose the next version string.

**Footnote warnings from MkDocs (`link '#fnref:N' has no anchor`)**
A footnote definition `[^N]:` exists without a matching inline citation. Add the citation or remove the orphaned definition.
