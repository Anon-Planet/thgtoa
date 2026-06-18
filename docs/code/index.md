---
title: "Content Contributions"
description: We are the maintainers of the Hitchhiker's Guide and the PSA Matrix space.
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

    # poppler: download from https://github.com/oschwartz10612/poppler-windows/releases
    # Extract and add the bin\ folder to PATH

    # qpdf: download from https://github.com/qpdf/qpdf/releases
    # Extract and add the bin\ folder to PATH

    # GPG: download Gpg4win from https://gpg4win.org

    # Python dependencies
    pip install "mkdocs-material[imaging]" pillow numpy
    ```

You also need **Google Chrome** or **Microsoft Edge** installed for the light-mode PDF build (headless Chromium).

You can [submit bugs and feature requests](https://github.com/Anon-Planet/thgtoa/issues/new) with detailed information about your issue or idea:

- If you'd like to propose an addition, please follow the standards outlined here.
- If you're reporting an issue, please be sure to include the expected behaviour, the observed behaviour, and steps to reproduce the problem.
- This can require technical knowledge, but you can also get involved in conversations about bug reports and feature requests. This is a great way to get involved without getting too overwhelmed!
- [Help fellow committers test recently submitted pull requests](https://github.com/Anon-Planet/thgtoa/pulls). Simply by pulling down a pull request and testing it, you can help ensure our new code contributions for stability and quality.

For those of you who are looking to add content to the guide, include the following:

- **Do** create a [topic branch] to work on instead of working directly on `main`. This helps to:
    + Protect the process.
    + Ensures users are aware of commits on the branch being considered for merge.
    + Allows for a location for more commits to be offered without mingling with other contributor changes.
    + Allows contributors to make progress while a PR is still being reviewed.
- **Do** follow the [50/72 rule] for Git commit messages.
- **Do** write "WIP" on your PR and/or open a [draft PR] if submitting unfinished changes..
- **Do** make sure the title of a draft PR makes it immediately clear that it's a draft
- **Do** target your pull request to the **main branch**.
- **Do** specify a descriptive title to make searching for your pull request easier.
- **Don't** leave your pull request description blank.
- **Don't** abandon your pull request. Being responsive helps us land your changes faster.
- **Don't** post questions in older closed PRs.
- **Do** stick to the guide to find common style issues.
- **Don't** make mass changes (such as replacing "I" with "we") using automated search/replace functionality.
    + Search/replace doesn't understand context, and as such, will inevitably cause inconsistencies and make the guide harder to read.
    + If it's part of a larger PR, it'll also make the reviewer's life harder, as they'll have to go through manually and undo everything by hand.
    + _If you're going to make mass changes, take the time to do it properly_. Otherwise we'll just have to undo it anyway.
    + If your change contains backslashes (`\`), either escape them with another backslash (`\\`) or put them in a ```code block```.

When reporting guide issues:

- **Do** write a detailed description of your issue and use a descriptive title.
- **Do** make it as detailed as possible and don't just submit 50 line changes without explaining.
- **Don't** file duplicate reports; search for your bug before filing a new report.
- **Don't** attempt to report issues on a closed PR.

Please split large sets of changes into multiple PRs. For example, a PR that adds Windows 11 support, removes Windows AME references, and fixes typos can be split into 3 PRs. This makes PRs easier to review prior to merging.

For an example of what _not_ to do, see: <https://github.com/Anon-Planet/thgtoa/pull/51>. This PR contains enough changes to split into multiple smaller and individually reviewable PRs.

While a PR is being reviewed, modifications may be made to it by the reviewer prior to merging. If this is the case, a new branch will be created for the PR's review. If you would like to submit a change to a PR that is in the process of being reviewed, _do not update the PR directly_. This will only cause merge conflicts and delay the PR from being merged. Instead, submit your changes to the PR's review branch.

For an example of what _not_ to do, see: <https://github.com/Anon-Planet/thgtoa/pull/51>. Instead of submitting changes to the PR directly, they should have been submitted as changes to the PR's associated review branch.

**Thank you** for taking the few moments to read this far! You're already way ahead of the
curve, so keep it up!

## Repository layout

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
  update_changelog.py # auto-generates changelog entries from git log
  setup_workflow.py   # GitHub Secrets setup assistant
  verify_pdf.py       # signature verification helper
  archived/
    tag_release.py    # ARCHIVED - GPG tag helper (not used in current flow)
```

## Building locally

```sh
python scripts/build_guide_pdf.py --both
```

This builds the MkDocs site, renders it to `export/thgtoa.pdf` via headless Chromium, then calls `scripts/convert.py` to produce `export/thgtoa-dark.pdf`.

| Flag | Effect |
|------|--------|
| `--both` | Light PDF then dark PDF |
| (no flag) | Light PDF only |
| `--dark` | Dark PDF only (light PDF must already exist) |

Build only the dark PDF from an existing light PDF:

```sh
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

# Preview the MkDocs site

```sh
mkdocs serve
```

Opens at `http://127.0.0.1:8000`.

# CI/CD pipeline overview

The pipeline is fully manual after the initial build - no step automatically triggers the next. This prevents version mismatches between what was built, what was signed, and what gets released. The workflows are numbered to help guide you.

```txt
push to main  (or manual trigger)
      │
      ▼
  01-build.yml
  Builds thgtoa.pdf + thgtoa-dark.pdf.
  Uploads artifact: pdfs
  Note the run ID.
      │
      │  # manually trigger 02-sign.yml with the build run ID
      ▼
  02-sign.yml
  Downloads pdfs artifact. Hashes (SHA-256 + BLAKE2b) and GPG-signs
  all files. Commits export/ back to main. Uploads artifacts:
  signatures, pdfs-signed
  Note the run ID.
      │
      │  # manually trigger 03-release.yml with the sign run ID
      ▼
  03-release.yml
  Downloads signatures + pdfs-signed artifacts. Runs VirusTotal.
  Creates GitHub Release tagged release-YYYYMMDD-<short-sha>.
      │
      │  # manually trigger 04-changelog.yml with the version string
      ▼
  04-changelog.yml
  Runs update_changelog.py, prepends a new ## [vX.Y.Z] entry,
  commits back to main.
```

Each stage is independent. If signing fails (e.g. an expired/revoked key, other problems in CI), re-run only `02-sign.yml` pointing at the existing build artifact - no need to rebuild the PDFs.

!!! warning "Before you push"

    - Make sure the working tree is clean (`git status`)
    - Run `mkdocs build` locally if you changed `docs/` to catch broken links before CI does
    - If you added new footnotes, verify they have both a definition `[^N]:` and at least one inline citation `[^N]`

---

# Release process

## Trigger a build

Push to `main` - `01-build.yml` runs automatically when `docs/`, `mkdocs.yml`, or `scripts/` change. You can also trigger it manually from **Actions → Build PDFs → Run workflow**.

Once it completes successfully, **note the run ID** from the URL or the Actions list.

---

## Sign the PDFs

Go to **Actions → Sign PDFs → Run workflow**.

| Input | Value |
|-------|-------|
| `build_run_id` | The run ID from step 1 |

`02-sign.yml` will:

- Download the PDFs artifact from the build run
- Compute SHA-256 and BLAKE2b hashes, writing `thgtoa.pdf.sha256`, `thgtoa.pdf.b2sum`, `sha256sums.txt`, `b2sums.txt`, and the dark equivalents
- GPG-sign all PDFs and hash files, writing `.asc` detached signature files
- Commit the updated `export/` directory back to `main`
- Upload two artifacts: `signatures` and `pdfs-signed`

Once it completes successfully, **note the run ID**.

---

## Publish the release

Go to **Actions → Release → Run workflow**.

| Input | Value |
|-------|-------|
| `sign_run_id` | The run ID from step 2 |
| `prerelease` | `false` for a normal release |

`03-release.yml` will:

- Download `signatures` and `pdfs-signed` artifacts from the sign run
- Upload both PDFs to VirusTotal
- Auto-generate a release tag in the format `release-YYYYMMDD-<short-sha>` (e.g. `release-20260527-abc1234`)
- Create a GitHub Release with all PDFs, hash files, and signatures attached, and the VirusTotal report URLs in the body

No version number needs to be chosen at this step - the tag is derived from the date and commit SHA, so it is always unique and always traceable.

---

## Update the changelog

Go to **Actions → Update Changelog → Run workflow**.

| Input | Value |
|-------|-------|
| `version` | The human-readable version string, e.g. `v1.2.4` |
| `dry_run` | `true` to preview without committing |

`04-changelog.yml` runs `scripts/update_changelog.py`, which:

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

```txt
release-20260527-abc1234
```

This format is always unique, requires no version decision at release time, and is directly traceable to the commit that was built. The version string (e.g. `v1.2.4`) is a separate, human-assigned label that lives only in the changelog.

---

## Commit message format

All commits must follow the [Conventional Commits](https://www.conventionalcommits.org) format. This is enforced by the `commitizen` pre-commit hook. Not because we want to limit cooperation with others, but becasue it promotes a cleaner Changelog; we can avoid all the noise by doing this programatically.

```txt
<type>(<scope>): <description>
```

Accepted types and their changelog bucket:

| Type | Bucket |
|------|--------|
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

# Verifying a release

Anyone can verify the authenticity of a release download.

```sh
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

```txt
gpg: Signature made Sun 31 May 2026 03:23:26 AM EDT
gpg:                using EDDSA key C3023DBEA3FB38C438BA1EEDCEC60AEDE8B992A2
gpg: Good signature from "Anonymous Planet Release Signing Key" [ultimate]
Primary key fingerprint: C302 3DBE A3FB 38C4 38BA  1EED CEC6 0AED E8B9 92A2
```

You can safely ignore Github, Codeberg, etc. warnings like "The email in this signature doesn’t match the committer email."

```txt
λ > git tag -v v1.2.3
object cdc54d8b3bc2b286827b23921d8d4062f85295cf
type commit
tag v1.2.3
tagger nopeitsnothing <no@anonymousplanet.net> 1780212206 -0400

v1.2.3
gpg: Signature made Sun 31 May 2026 03:23:26 AM EDT
gpg:                using EDDSA key C3023DBEA3FB38C438BA1EEDCEC60AEDE8B992A2
gpg: Good signature from "Anonymous Planet Release Signing Key" [ultimate]
Primary key fingerprint: C302 3DBE A3FB 38C4 38BA  1EED CEC6 0AED E8B9 92A2
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

**`03-release.yml` fails on VirusTotal**
The `VT_API_KEY` is missing, invalid, or over the rate limit (500 requests/day on the free tier). Check the secret and re-run after a few minutes.

**`02-sign.yml` fails downloading PDF artifact**
The `build_run_id` is wrong, or the artifact has expired (90-day retention). Trigger a new build and use the fresh run ID.

**Changelog already contains version X**
`update_changelog.py` will error if `MANUAL_VERSION` is set to a version already in the changelog. Choose the next version string.

**Footnote warnings from MkDocs (`link '#fnref:N' has no anchor`)**
A footnote definition `[^N]:` exists without a matching inline citation. Add the citation or remove the orphaned definition.

[discussions]: https://github.com/Anon-Planet/thgtoa/discussions
[issues]: https://github.com/Anon-Planet/thgtoa/issues
[help fellow users with open issues]: https://github.com/Anon-Planet/thgtoa/issues
[topic branch]: http://git-scm.com/book/en/Git-Branching-Branching-Workflows#Topic-Branches
[Qubes#7457]: https://github.com/QubesOS/qubes-issues/issues/7457
[50/72 rule]: http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html
[draft pr]: https://help.github.com/en/articles/about-pull-requests#draft-pull-requests
[console output]: https://docs.github.com/en/free-pro-team@latest/github/writing-on-github/creating-and-highlighting-code-blocks#fenced-code-blocks
[verification steps]: https://docs.github.com/en/free-pro-team@latest/github/writing-on-github/basic-writing-and-formatting-syntax#task-lists
[reference associated issues]: https://github.com/blog/1506-closing-issues-via-pull-requests
[help fellow committers test recently submitted pull requests]: https://github.com/Anon-Planet/thgtoa/pulls
