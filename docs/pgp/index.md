---
title: "PGP"
description: "Import our GPG keys to verify our releases and signed content."
schema:
  "@context": https://schema.org
  "@type": Organization
  "@id": https://anonymousplanet.net/
  name: Anonymous Planet PGP
  url: https://anonymousplanet.net/pgp/
  logo: ../media/profile.png
  sameAs:
    - https://github.com/Anon-Planet
    - https://opencollective.com/anonymousplanetorg
    - https://mastodon.social/@anonymousplanet
---

# PGP Keyring for Verification

<div style="text-align: center; margin: 2rem 0;">
<a href="../pgp/anonymousplanet.asc" class="btn-download">
    Download Our Public Keyring (anonymousplanet.asc)
</a>
</div>

Import this keyring to verify the authenticity of our releases and signed content.

## Import Instructions

### GnuPG (Command Line)

```bash
gpg --import docs/pgp/anonymousplanet.asc
```

Or directly from GitHub:

```bash
gpg --keyserver keys.openpgp.org --recv-keys C302 3DBE A3FB 38C4 38BA 1EED CEC6 0AED E8B9 92A2
```

### Import and Verify

```bash
# Import the keyring (includes both MSK and RSK)
gpg --import docs/pgp/anonymousplanet.asc

# List imported keys
gpg --list-keys anonymousplanet.net

# Verify a release signature (replace with your file)
gpg --verify file.sig file.pdf
```

### GPG-Agent Setup

Ensure GPG-agent is running:

```bash
export GNUPGHOME="${XDG_DATA_HOME:-$HOME/.local/share}/gnupg"
chmod 700 "$GNUPGHOME"  # Critical for security!
```

## Our Keys

| Name | Key ID | Purpose |
|------|--------|---------|
| **Master Signing Key (MSK)** | `9FA5436D0EE360985157382517ECA05F768DEFDA` | Code releases, signing GPG-agent |
| **Release Signing Key (RSK)** | `C3023DBEA3FB38C438BA1EECEC60AEDE8B992A2` | Release artifacts only |

**Fingerprint verification:** Always verify key fingerprints against our [GitHub announcements](https://github.com/Anon-Planet/thgtoa/releases) before importing.

## Security Notes

- Keep `GNUPGHOME` permissions set to `700` (owner only).
- Never share private keys — we don't have any!

??? warning "Key Rotation"

    We may rotate keys periodically. Check our [GitHub Releases](https://github.com/Anon-Planet/thgtoa/releases) and [changelog](../changelog/index.md) for announcements.
