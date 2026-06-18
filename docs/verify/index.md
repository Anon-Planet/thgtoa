---
title: "Verifying authenticity"
---

<div style="font-family: var(--code-font); color: var(--crt-red); font-size: 0.9rem; margin-bottom: 2em;">
Never blindly trust the information you see online.
</div>

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5em; max-width: 1000px; margin: 0 auto;">

<div class="quick-access-card">
<h4 style="font-family: var(--code-font); font-size: 1.1rem; margin: 0;">Get our keyring</h4>
<p style="margin: 0 0 1em;">The Anonymous Planet MSK and other keys in our keyring can be found here.</p>
<a href="../../pgp/" style="font-family: var(--code-font); font-size: 0.85rem; color: var(--crt-amber);">Access our public keyring <span style="font-size: 0.7em;"></span></a>
</div>
</div>

## Files Provided

For each release, you'll receive:

| File Type | Purpose | Verification Command |
|-----------|---------|---------------------|
| **PDF** (`thgtoa.pdf`) | The actual guide document | Check hash + signature |
| **.sig file** | GPG detached signature for authenticity | `gpg --verify file.sig file.pdf` |
| **.sha256** | SHA256 checksum for integrity | `sha256sum -c file.sha256` |

## Quick Verification

### Using Python Script (Recommended)

```sh
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

```sh
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

```sh
gpg --import pgp/anonymousplanet.asc
```

Then verify the signature:

```sh
gpg --verify export/thgtoa.pdf.sig export/thgtoa.pdf
gpg --verify export/thgtoa-dark.pdf.sig export/thgtoa-dark.pdf
```

**Example output for successful verification:**

```text
gpg: Signature made Mon 20 Apr 2026 01:46:40 AM EDT
gpg:                using EDDSA key 9FA5436D0EE360985157382517ECA05F768DEFDA
gpg: Good signature from "Anonymous Planet Master Signing Key" [unknown]
gpg: WARNING: This key is not certified with a trusted signature!
gpg:           There is no indication that the signature belongs to the owner.
Primary key fingerprint: 9FA5 436D 0EE3 6098 5157  3825 17EC A05F 768D EDF6
```

**Note:** The "WARNING" is expected - it means the key hasn't been signed by another trusted key. This is normal for independent signing keys.

#### 3. Check VirusTotal Status

Visit the VirusTotal report links (automatically generated in release notes):
- Light mode: `https://www.virustotal.com/gui/file/[hash]`
- Dark mode: `https://www.virustotal.com/gui/file/[hash]`

Or use the Python script with API key:

```sh
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

- Ensure you imported the correct public key from [`pgp/`](../pgp/index.md)
- Check the key fingerprint matches the official one from the repository announcements

### Hash mismatch?

- Re-download the file (corruption during transfer)
- Verify you're checking against the correct hash file for the mode (light/dark)
- Check for disk errors on your system

### GPG not found?

- **Linux/Debian:** `sudo apt install gnupg`
- **Linux/RHEL/CentOS:** `sudo yum install gnupg2` or `sudo dnf install gnupg2`
- **macOS:** `brew install gnupg` or use Homebrew Casks: `brew install --cask gnupg`
- **Windows:** Use [Gpg4win](https://www.gpg4win.org/)
