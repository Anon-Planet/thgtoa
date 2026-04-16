---
title: "Verify"
description: How to verify the authenticity of our files and check virus scans
---

# PDF Verification Guide

## Files Provided

For each PDF release, you'll receive:

- **PDF file** (`thgtoa.pdf` or `thgtoa-dark.pdf`) - The actual document
- **Signature file** (`.sig`) - GPG detached signature for authenticity verification
- **Hash file** (`.sha256`) - SHA256 checksum for integrity verification

## Quick Verification

### Using Python Script (Recommended)

```bash
# Verify everything (hashes, signatures, and optionally VirusTotal)
python scripts/verify_pdf.py --all

# Only verify hashes
python scripts/verify_pdf.py --hashes

# Only verify GPG signatures
python scripts/verify_pdf.py --signatures

# Check VirusTotal scan status (requires VT_API_KEY environment variable)
python scripts/verify_pdf.py --vt
```

### Manual Verification

#### 1. Verify SHA256 Hash

**Linux/macOS:**
```bash
cd /path/to/repo
sha256sum -c sha256sum-light.txt
```

**Windows (PowerShell):**
```powershell
Get-FileHash -Algorithm SHA256 export\thgtoa.pdf | Select-Object Hash
# Compare with the hash in thgtoa.pdf.sha256
```

#### 2. Verify GPG Signature

First, import the public key:
```bash
gpg --import pgp/anonymousplanet-master.asc
```

Then verify the signature:
```bash
gpg --verify export/thgtoa.pdf.sig export/thgtoa.pdf
gpg --verify export/thgtoa-dark.pdf.sig export/thgtoa-dark.pdf
```

Expected output for successful verification:
```
gpg: Signature made [date]
gpg:                using RSA key [key-id]
gpg: Good signature from "[owner]"
```

#### 3. Check VirusTotal Status

Visit the VirusTotal report links (automatically generated in release notes):
- Light mode: `https://www.virustotal.com/gui/file/[hash]`
- Dark mode: `https://www.virustotal.com/gui/file/[hash]`

Or use the Python script with API key:
```bash
export VT_API_KEY=your_vt_api_key
python scripts/verify_pdf.py --vt
```

## Automated Verification in CI/CD

The GitHub Actions workflows automatically:

1. **Build PDFs** from MkDocs source
2. **Generate SHA256 hashes** and save to root directory
3. **Sign files with GPG** using the repository's private key
4. **Scan with VirusTotal** and update release notes
5. **Create releases** with all verification artifacts

## Security Best Practices

1. **Always verify signatures** before opening PDFs from untrusted sources
2. **Check hashes** to ensure files weren't corrupted during download
3. **Review VirusTotal results** for any suspicious detections
4. **Import keys securely** - verify key fingerprints with the project maintainers
5. **Keep verification scripts updated** to match current security standards

## Troubleshooting

### "Good signature" but wrong owner?
- Ensure you imported the correct public key
- Check the key fingerprint matches the official one from the repository

### Hash mismatch?
- Re-download the file (corruption during transfer)
- Verify you're checking against the correct hash file
- Check for disk errors on your system

### GPG not found?
- Install GPG: `sudo apt install gnupg` (Debian/Ubuntu) or `brew install gnupg` (macOS)
- On Windows, use [Gpg4win](https://www.gpg4win.org/)

## Key Information

**Signing Key:** Anonymous Planet Master Key
**Key ID:** See `pgp/anonymousplanet-master.asc` for details
**Fingerprint:** Verify from the repository's official documentation

---

*For questions or issues with verification, please open an issue on GitHub.*
