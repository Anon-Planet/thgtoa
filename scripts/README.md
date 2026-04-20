# PDF Build, Scan & Release Scripts

This directory contains scripts for building PDFs from MkDocs documentation, scanning them with VirusTotal, generating hashes, and uploading artifacts to GitHub releases.

## Scripts

### `pdf_release.sh` (v2 - Recommended)
The main script that handles:
- SHA256 hash generation for PDF files
- VirusTotal scanning of PDFs
- Release creation/update on GitHub
- GPG signature verification support

**Usage:**
```bash
./scripts/pdf_release.sh --build <light|dark|both> --release <tag|latest> [--vt-api-key VT_KEY] [--github-token TOKEN]
```

**Options:**
- `--build`: PDF build mode (`light`, `dark`, or `both`) - Required
- `--release`: Release update mode (`tag` for tagged releases, `latest` to always update) - Default: `tag`
- `--vt-api-key`: VirusTotal API key (optional)
- `--github-token`: GitHub token for release operations (optional)

### `build_guide_pdf.py`
Python script that builds MkDocs documentation and converts it to PDF using Chromium/Chrome.

**Usage:**
```bash
python scripts/build_guide_pdf.py --both  # Build both light and dark mode
python scripts/build_guide_pdf.py --dark-mode  # Dark mode only
python scripts/build_guide_pdf.py --skip-mkdocs  # Skip MkDocs build, use existing site
```

## GitHub Actions Workflow

The workflow `.github/workflows/build-pdf-combined.yml` combines all operations:

1. **Build PDFs** - Generates light/dark mode PDFs with GPG signatures
2. **Scan & Release** - Scans with VirusTotal and updates/releases artifacts

### Required Secrets

Add these to your repository settings under **Settings > Secrets and variables > Actions**:

- `GPG_PRIVATE_KEY`: Your GPG private key for signing
- `GPG_PASSPHRASE`: Passphrase for the GPG key (if any)
- `VT_API_KEY`: VirusTotal API key for malware scanning
- `GITHUB_TOKEN`: Automatically available, but can be manually added

### Workflow Triggers

The workflow runs on:
- Manual dispatch (`workflow_dispatch`) with customizable options
- Push to main branch when docs, mkdocs.yml, or scripts change

## Output Files

After running the build and release process, you'll get:

```
export/
├── thgtoa.pdf                    # Light mode PDF
├── thgtoa-dark.pdf               # Dark mode PDF
├── thgtoa.pdf.sig                # GPG signature for light PDF
├── thgtoa-dark.pdf.sig           # GPG signature for dark PDF
├── thgtoa.pdf.sha256             # SHA256 hash for light PDF
├── thgtoa-dark.pdf.sha256        # SHA256 hash for dark PDF
├── sha256sum-combined.txt        # Combined hash file
├── sha256sum-combined.txt.sig    # GPG signature for combined hashes
└── virus-total-results.md        # VirusTotal scan results
```

## Hash Verification

To verify the integrity of downloaded PDFs:

```bash
# Verify against individual hash file
sha256sum -c thgtoa.pdf.sha256

# Or verify against combined hash file
sha256sum -c sha256sum-combined.txt
```

## VirusTotal Integration

When a `VT_API_KEY` is provided, the script will:
1. Upload each PDF to VirusTotal's API
2. Generate individual scan reports
3. Include VT report links in release notes and artifacts

The VT results file (`virus-total-results.md`) contains:
- Scan timestamp
- SHA256 hashes for each PDF
- Direct links to VirusTotal GUI reports

## Release Management

The script supports two release modes:

1. **Tag mode** (`--release tag`): Updates the release matching the current git tag
2. **Latest mode** (`--release latest`): Always updates the most recent release (useful for continuous deployment)

When running in a GitHub Actions workflow with a tag push, it will automatically create or update the corresponding release.

## Troubleshooting

### PDF Build Fails
- Ensure Chrome/Chromium is installed: `sudo apt install chromium-browser`
- Check MkDocs configuration is valid: `mkdocs build --strict`
- Verify all documentation files are present and properly formatted

### VirusTotal Scan Fails
- Check VT_API_KEY secret is correctly set in repository settings
- Verify the API key has sufficient quota (free tier allows 4 requests/minute)
- Check network connectivity to VirusTotal API

### Release Upload Fails
- Ensure GITHUB_TOKEN has appropriate permissions (repo scope)
- For existing releases, use `--release latest` instead of `tag`
- Check that the release tag format matches GitHub's requirements (e.g., `v1.0.0`)

## Security Notes

- **GPG Keys**: Never commit private keys to version control. Use GitHub Secrets.
- **VT API Key**: Keep your VirusTotal API key secret and rotate periodically.
- **Release Artifacts**: All uploaded artifacts are publicly visible on your releases page.

## License

These scripts are part of the "The How-To Guide To Anonymity" project and follow the same licensing as the main repository.
