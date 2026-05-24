# Developer Guide

This page covers everything you need to contribute to the project, run the build pipeline locally, configure GitHub secrets, and cut a signed release.

---

## Prerequisites

Install these before anything else.

=== "Linux / macOS"

    ```bash
    # Python 3.11+
    python3 --version

    # poppler (pdftoppm) and qpdf
    sudo apt install poppler-utils qpdf       # Debian / Ubuntu
    brew install poppler qpdf                 # macOS

    # GPG
    sudo apt install gnupg                    # Debian / Ubuntu
    brew install gnupg                        # macOS

    # Python dependencies
    pip install "mkdocs-material[imaging]" pillow numpy
    ```

=== "Windows"

    ```powershell
    # Python 3.11+ from https://python.org

    # poppler — download from https://github.com/oschwartz10612/poppler-windows/releases
    # Extract and add the bin\ folder to PATH

    # qpdf — download from https://github.com/qpdf/qpdf/releases
    # Extract and add the bin\ folder to PATH

    # GPG — download Gpg4win from https://gpg4win.org

    # Python dependencies
    pip install "mkdocs-material[imaging]" pillow numpy
    ```

You also need **Google Chrome** or **Microsoft Edge** installed for the light-mode PDF build (headless Chromium).

---

## Repository layout

```
.github/
  workflows/
    build.yml        ← builds PDFs, uploads artifact
    sign.yml         ← hashes + GPG signs, uploads signatures artifact
    release.yml      ← publishes GitHub Release with all assets
    changelog.yml    ← auto-updates docs/changelog/index.md
    publish.yml      ← deploys MkDocs site to GitHub Pages
docs/
  guide/index.md     ← the guide (single Markdown file)
  changelog/         ← release notes
  code/              ← this page
export/              ← PDF output (gitignored except .sha256, .b2, .sig)
pgp/                 ← public signing keys
scripts/
  build_guide_pdf.py ← MkDocs + Chromium PDF builder
  convert.py         ← pixel-based dark mode PDF converter
  tag_release.py     ← interactive signed-tag helper for maintainers
  update_changelog.py← auto-generates changelog entries from git log
  setup_workflow.py  ← GitHub Secrets setup assistant
  verify_pdf.py      ← signature verification helper
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

## Pushing changes

The pipeline triggers automatically when you push to `main` — no manual steps are needed for normal contributions.

```
push to main
    │
    ▼
build.yml          builds thgtoa.pdf + thgtoa-dark.pdf
    │ (workflow_run on success)
    ▼
sign.yml           SHA-256 + BLAKE2b hashes, GPG detached signatures
    │ (workflow_run on success)
    ▼
release.yml        VirusTotal scan → tagged GitHub Release
    │
changelog.yml      prepends new ## [vX.Y.Z] entry → commits back to main
```

Each stage runs independently and can be re-triggered manually from the Actions tab. If the build succeeds but signing fails (e.g. an expired key), you can re-run only `sign.yml` pointing at the existing build artifact without rebuilding the PDFs.

!!! warning "Before you push"

    - Make sure the working tree is clean (`git status`)
    - Run `mkdocs build` locally if you changed `docs/` to catch broken links before CI does
    - If you added new footnotes, verify they have both a definition `[^N]:` and at least one inline citation `[^N]`

---

## GitHub Secrets

These must be configured in **Settings → Secrets and variables → Actions** before the pipeline will fully work. The build step requires no secrets; signing and releasing require all of them.

### `GPG_PRIVATE_KEY`

The ASCII-armored private key used to sign PDFs and hash files.

```bash
# Export the release signing key
gpg --armor --export-secret-keys 9FA5436D0EE360985157382517ECA05F768DEDF6
```

Copy the entire output (including `-----BEGIN PGP PRIVATE KEY BLOCK-----` and the closing line) and paste it as the secret value.

!!! danger "Key security"
    This is the release signing key. Only repository admins should have access to it. Never commit it to the repository or share it outside of GitHub Secrets.

---

### `GPG_PASSPHRASE`

The passphrase protecting the private key above. Must match exactly — no trailing newline.

---

### `VT_API_KEY`

A [VirusTotal](https://www.virustotal.com) API key with file upload permissions. Used by `release.yml` to scan both PDFs before publishing the release.

Get one by creating a free account at `virustotal.com` → API key under your profile. The free tier allows 4 lookups/minute and 500/day, which is sufficient for the two PDFs per release.

---

### `CHANGELOG_PAT`

A GitHub **Personal Access Token** with `contents: write` scope on this repository.

**Why it's needed:** `changelog.yml` commits back to `main` after each build. Commits made with the default `GITHUB_TOKEN` do not trigger further workflow runs (GitHub's loop-prevention policy). A PAT bypasses this so the changelog commit itself can be picked up by downstream workflows if needed.

**Creating one:**

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens
2. Set repository access to **Only select repositories** → this repo
3. Under Permissions → Repository permissions, set **Contents** to **Read and write**
4. Set an expiration and add it as the `CHANGELOG_PAT` secret

If this secret is absent, `changelog.yml` falls back to `GITHUB_TOKEN` — the commit still happens, it just won't trigger further workflows.

---

### Secrets summary

| Secret | Required by | What happens if missing |
|--------|------------|------------------------|
| `GPG_PRIVATE_KEY` | `sign.yml` | Signing step fails — no `.sig` files produced |
| `GPG_PASSPHRASE` | `sign.yml` | GPG import succeeds but signing fails |
| `VT_API_KEY` | `release.yml` | VirusTotal step fails — release is not published |
| `CHANGELOG_PAT` | `changelog.yml` | Falls back to `GITHUB_TOKEN` — changelog still updates, but commit won't trigger downstream workflows |

---

## Cutting a release

Releases are tagged manually by maintainers. The `tag_release.py` script handles everything interactively.

### Requirements

- Your GPG keyring must contain the release signing key (`C302 3DBE A3FB 38C4 38BA  1EED CEC6 0AED E8B9 92A2`)
- The working tree must be clean
- You must be on the `main` branch
- A `## [vX.Y.Z]` entry must exist in `docs/changelog/index.md` for the version you are tagging

### Import the release key (first time only)

```bash
gpg --import pgp/anonymousplanet-release.asc
```

### Run the release tagger

```bash
python scripts/tag_release.py
```

The script will:

1. Check the working tree is clean and you are on `main`
2. Detect the latest tag and propose the next patch version
3. Pull the matching changelog entry and format it as the tag message
4. Show you the full tag message for review
5. Ask for confirmation before creating anything
6. Create a GPG-signed annotated tag with `git tag -s`
7. Verify the signature
8. Print the push command

To specify a version explicitly:

```bash
python scripts/tag_release.py --version v1.2.4
```

To preview without creating the tag:

```bash
python scripts/tag_release.py --dry-run
```

To use a different signing key:

```bash
python scripts/tag_release.py --key <fingerprint>
```

### Push the tag

```bash
git push origin v1.2.4
```

### Trigger the release workflow

Pushing a tag does **not** automatically trigger `release.yml` (it listens to `workflow_run` from `sign.yml`, not tag pushes). After pushing the tag, go to **Actions → Release → Run workflow** and paste the most recent `sign.yml` run ID to publish the GitHub Release.

---

## Verifying a release

Anyone can verify the authenticity of a release download.

```bash
# Import the release signing key
gpg --import pgp/anonymousplanet-release.asc

# Verify the PDFs
gpg --verify thgtoa.pdf.sig      thgtoa.pdf
gpg --verify thgtoa-dark.pdf.sig thgtoa-dark.pdf

# Verify the hash files themselves
gpg --verify sha256sums.txt.sig sha256sums.txt
gpg --verify b2sums.txt.sig     b2sums.txt

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
Install the imaging extras: `pip install "mkdocs-material[imaging]"`. This is required by the `social` plugin.

**`KeyError: 'JPEG'` in convert.py**
Pillow needs libjpeg for RGB→PDF encoding. The script works around this by quantizing to palette mode before saving, so this error should not appear with the current code. If it does, reinstall Pillow after installing libjpeg: `sudo apt install libjpeg-dev && pip install --force-reinstall pillow`.

**`qpdf: can't find PDF header`**
An older version of `convert.py` tried to pass PNG files to qpdf. Make sure you are running the current version — qpdf only accepts PDF inputs to `--pages`.

**GPG signing fails on CI with `No secret key`**
The `GPG_PRIVATE_KEY` secret is missing or malformed. Re-export with `gpg --armor --export-secret-keys <fingerprint>` and paste the full block including the header and footer lines.

**GPG signing fails with `Bad passphrase`**
The `GPG_PASSPHRASE` secret has a trailing space or newline. Paste it again carefully with no surrounding whitespace.

**`release.yml` fails on VirusTotal**
The `VT_API_KEY` is missing, invalid, or over the rate limit (500 requests/day on the free tier). Check the secret and re-run the workflow after a few minutes.

**Footnote warnings from MkDocs (`link '#fnref:N' has no anchor`)**
A footnote definition `[^N]:` exists without a matching inline citation `[^N]` in the body text. Add the citation where it belongs in the guide, or remove the orphaned definition.
