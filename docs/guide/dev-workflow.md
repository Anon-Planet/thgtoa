# Development

## Overview

This repository now includes an automated workflow that handles PDF generation, verification, and distribution with the following features:

??? Note "How the pipeline works"

    1. **Automatic PDF Generation** - Builds both light and dark mode PDFs from MkDocs source
    2. **SHA256 Hash Generation** - Creates hash files for integrity verification
    3. **GPG Signature Signing** - Signs all PDFs and hash files with repository GPG key
    4. **VirusTotal Scanning** - Automatically scans PDFs and updates release notes
    5. **Release Automation** - Packages everything into GitHub releases

## Workflow Architecture

### 1. Build PDF Workflow (`build-pdf.yml`)

**Trigger:** Push to main, pull requests, or manual dispatch

??? Note "Steps"

    - Checkout repository
    - Set up Python 3.13 and MkDocs Material
    - Install Chromium browser
    - Generate both light and dark mode PDFs
    - Create SHA256 hash files
    - Sign all files with GPG
    - Upload artifacts to GitHub Actions
    - Publish release

### 2. VirusTotal Scan Workflow (`vt-scan.yml`)

**Trigger:** Push to main, tags, or manual dispatch (runs after build-pdf)

??? Note "Steps"

    - Download PDF artifacts from build workflow
    - Scan both PDFs with VirusTotal API
    - Extract scan results and generate report links
    - Update release notes with VT scan status and URLs

## File Structure

After a successful build, the repository will contain:

```
.../
├── export/
│   ├── thgtoa.pdf              # Light mode PDF
│   ├── thgtoa-dark.pdf         # Dark mode PDF
│   ├── thgtoa.pdf.sig          # GPG signature (light)
│   └── thgtoa-dark.pdf.sig     # GPG signature (dark)
├── thgtoa.pdf.sha256           # Hash file (light)
├── thgtoa-dark.pdf.sha256      # Hash file (dark)
├── sha256sum-light.txt         # Combined hash file
└── scripts/
    ├── build_guide_pdf.py      # PDF generation script
    └── verify_pdf.py           # Verification utility
```

## Security Features

### 1. SHA256 Hash Verification

**Purpose:** Ensure file integrity during download/transit

**How it works:**
- Each PDF gets a unique SHA256 hash calculated at build time
- Hash stored in `.sha256` files alongside the PDFs
- Combined `sha256sum-light.txt` for batch verification

**Verification command:**
```bash
sha256sum -c sha256sum-light.txt
```

### 2. GPG Signature Verification

**Purpose:** Verify authenticity and prevent tampering

??? Note "How it works"

    - Detached signatures created for each PDF and hash file
    - Public keys available in `/pgp/` directory

**Verification command:**
```bash
gpg --import pgp/anonymousplanet-master.asc
gpg --verify export/thgtoa.pdf.sig export/thgtoa.pdf
```

### 3. VirusTotal Integration

**Purpose:** Malware detection and security scanning

??? Note "How it works"

    - Automatic scan of all generated PDFs
    - Results published in release notes with direct links
    - Provides third-party validation of file safety

## Usage Examples

### Local Development

```bash
# Build PDFs locally
python scripts/build_guide_pdf.py --both

# Verify hashes
python scripts/verify_pdf.py --hashes

# Verify signatures (requires GPG installed)
python scripts/verify_pdf.py --signatures

# Full verification with VirusTotal check
export VT_API_KEY=your_api_key
python scripts/verify_pdf.py --all
```

### CI/CD Verification

The workflows automatically verify everything during the build process. To manually trigger:

1. Go to Actions tab
2. Select "Build guide PDF" or "VirusTotal Scan"
3. Click "Run workflow"
4. Download artifacts from successful run

## Release Process

When you create a tag (e.g., `v1.0.0`):

1. Push the tag: `git push origin v1.0.0`
2. Build PDF workflow triggers automatically
3. VirusTotal scan workflow runs after build completes
4. Both workflows update/create GitHub release with:
   - Light and dark mode PDFs
   - GPG signatures for all files
   - Hash files for verification
   - Release notes with VT scan results

## Troubleshooting

### Common Issues

**GPG signing fails:**
- Check that `GPG_PRIVATE_KEY` is in ASCII armor format
- Verify passphrase is correct
- Ensure key has signing capability

**Hash mismatch after download:**
- Re-download the file (corruption during transfer)
- Verify you're using the correct hash file
- Check disk integrity

**VirusTotal scan fails:**
- Verify `VT_API_KEY` is set correctly
- Check API quota limits (free tier: 4 requests/minute)
- Ensure PDF files exist before scanning

### Debug Mode

Enable verbose output by adding to workflow:
```yaml
- name: Debug
  run: |
    echo "Current directory:" && pwd
    echo "Files in export:" && ls -la export/
    echo "Hash file contents:" && cat sha256sum-light.txt
```

## Best Practices

1. **Always verify signatures** before opening PDFs from untrusted sources
2. **Check VirusTotal results** for any suspicious detections
3. **Keep GPG keys secure** - never commit private keys to repository
4. **Monitor API usage** for VirusTotal to avoid rate limiting
5. **Test locally** before pushing tags to production

## Future Enhancements

Potential improvements:
- Multi-signature support (multiple maintainers)
- Automated changelog generation with hashes
- Cross-platform signature verification scripts
- Integration with additional malware scanners
- Automatic mirror updates with verified files

---

*This workflow is designed for security-conscious users who need to verify the authenticity and integrity of downloaded documents.*
