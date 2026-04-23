# Development

??? Note "How the pipeline works"

    **Automatic PDF Generation:** - Builds both light and dark mode PDFs from MkDocs source
    **SHA256 Hash Generation:** - Creates hash files for integrity verification
    **GPG Signature Signing:** - Signs all PDFs and hash files with repository GPG key
    **VirusTotal Scanning:** - Automatically scans PDFs and updates release notes
    **Release Automation:** - Packages everything into GitHub releases

## Architecture

### Build PDF Workflow (`build-sign-release.yml`)

!!! Note "Steps"

    - Checkout repository
    - Set up Python and MkDocs Material
    - Install Chromium browser
    - Generate both light and dark mode PDFs with `scripts\build_guide_pdf.py`
    - Create SHA256 and blake2 hash files in `export/`
    - Sign all files with GPG in `export/`
    - Upload artifacts to GitHub Actions **manually**

### SHA256 Hash Verification

!!! Note "**How it works**"

    - Each PDF gets a unique SHA256 hash calculated at build time
    - Hash stored in `.sha256` files alongside the PDFs
    - Combined `sha256sum.txt` for batch verification

### GPG Signature Verification

**Purpose:** Verify authenticity and prevent tampering

!!! Note "How it works"

    - Detached signatures created for each PDF and hash file
    - Public keys available in `/pgp/` directory

**Verification command:**
```bash
gpg --import pgp/anonymousplanet-master.asc
gpg --verify export/thgtoa.pdf.sig export/thgtoa.pdf
```

---

*This workflow is designed for security-conscious users who need to verify the authenticity and integrity of downloaded documents.*
