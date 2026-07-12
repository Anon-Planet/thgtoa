---
title: "Verify"
description: "Verify the authenticity and integrity of Anonymous Planet releases."
hide:
  - navigation
schema:
  "@context": https://schema.org
  "@type": Organization
  "@id": https://anonymousplanet.net/
  name: Anonymous Planet
  url: https://anonymousplanet.net/verify/
  logo: ../media/profile.png
---

<div class="hero-block">
  <div class="hero-eyebrow">Never blindly trust anything you download.</div>
  <h1 class="hero-title">Verify Releases<span class="hero-subtitle">Signatures. Hashes. Trust nothing blindly.</span></h1>
  <p class="hero-tagline">
    Every release is GPG-signed and hashed. Verify before you read.
  </p>
  <div class="hero-cta-row">
    <a href="#quick-verification" class="hero-cta hero-cta--primary">Quick Verification</a>
    <a href="../pgp/" class="hero-cta hero-cta--secondary">Import Our Keys</a>
  </div>
</div>

---

## What We Publish { #artifacts }

<div class="index-grid">

  <div class="index-card">
    <h3 class="index-card__title">PDF Guide</h3>
    <p class="index-card__body"><code>thgtoa.pdf</code> and <code>thgtoa-dark.pdf</code> — the full guide in light and dark mode. The only canonical single-file export.</p>
    <a href="https://github.com/Anon-Planet/thgtoa/releases" class="index-card__link">Latest release</a>
  </div>

  <div class="index-card">
    <h3 class="index-card__title">Detached Signatures</h3>
    <p class="index-card__body"><code>.asc</code> files for every PDF and hash file, signed with the Release Signing Key (RSK). Verify with <code>gpg --verify</code>.</p>
    <a href="../pgp/" class="index-card__link">Our keys</a>
  </div>

  <div class="index-card">
    <h3 class="index-card__title">Hash Files</h3>
    <p class="index-card__body"><code>sha256sums.txt</code> and <code>b2sums.txt</code> for integrity. Both are also signed. Check with <code>sha256sum -c</code> or <code>b2sum -c</code>.</p>
    <a href="#manual-verification" class="index-card__link">Manual steps</a>
  </div>

</div>

---

## Quick Verification { #quick-verification }

### Using the Python Script (Recommended)

```sh
# Verify everything — hashes, signatures, and optionally VirusTotal
python scripts/verify_pdf.py --all

# Hashes only
python scripts/verify_pdf.py --hashes

# GPG signatures only
python scripts/verify_pdf.py --signatures

# VirusTotal scan status (requires VT_API_KEY env var)
python scripts/verify_pdf.py --vt
```

---

## Manual Verification { #manual-verification }

### 1. Import the key

```sh
gpg --import pgp/anonymousplanet.asc
```

Verify the fingerprint against our [PGP page](../pgp/index.md) and [GitHub releases](https://github.com/Anon-Planet/thgtoa/releases) before trusting it.

### 2. Verify the PDFs

```sh
gpg --verify export/thgtoa.pdf.asc      export/thgtoa.pdf
gpg --verify export/thgtoa-dark.pdf.asc export/thgtoa-dark.pdf
```

Expected output:

```text
gpg: Signature made Sun 31 May 2026 03:23:26 AM EDT
gpg:                using EDDSA key C3023DBEA3FB38C438BA1EEDCEC60AEDE8B992A2
gpg: Good signature from "Anonymous Planet Release Signing Key" [ultimate]
Primary key fingerprint: C302 3DBE A3FB 38C4 38BA  1EED CEC6 0AED E8B9 92A2
```

!!! note "About the WARNING"
    `WARNING: This key is not certified with a trusted signature` is expected. It means the key has not been co-signed by another key in your web of trust — not that the signature is invalid.

### 3. Check hashes

=== "Linux / macOS"

    ```sh
    sha256sum -c sha256sums.txt
    b2sum     -c b2sums.txt
    ```

=== "Windows (PowerShell)"

    ```powershell
    Get-FileHash -Algorithm SHA256 export\thgtoa.pdf | Select-Object Hash
    # Compare with the value in thgtoa.pdf.sha256
    ```

### 4. VirusTotal (optional)

```sh
export VT_API_KEY=your_vt_api_key
python scripts/verify_pdf.py --vt
```

Or open the VirusTotal report URLs listed in the release notes directly.

---

## Troubleshooting { #troubleshooting }

**"Good signature" but wrong owner?**
Ensure you imported the correct key from [`pgp/`](../pgp/index.md). Check the fingerprint matches the RSK: `C302 3DBE A3FB 38C4 38BA  1EED CEC6 0AED E8B9 92A2`.

**Hash mismatch?**
Re-download the file. Verify you are using the correct hash file for the edition (light vs dark). Check for disk errors.

**GPG not installed?**

| Platform | Command |
|---|---|
| Debian / Ubuntu | `sudo apt install gnupg` |
| RHEL / Fedora | `sudo dnf install gnupg2` |
| macOS | `brew install gnupg` |
| Windows | [Gpg4win](https://gpg4win.org) |
