---
title: "PGP"
description: "Import our GPG keys to verify our releases and signed content."
hide:
  - navigation
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
---

<div class="hero-block">
  <div class="hero-eyebrow">Trust, but verify.</div>
  <h1 class="hero-title">Our Public Keys<span class="hero-subtitle">Import. Verify. Trust nothing blindly.</span></h1>
  <p class="hero-tagline">
    Anonymous Planet signs all releases and communications with GnuPG (PGP) keys.
    Verify fingerprints against multiple independent sources before importing.
  </p>
  <div class="hero-cta-row">
    <a href="anonymousplanet.asc" class="hero-cta hero-cta--primary">Download Public Keyring</a>
    <a href="#keys" class="hero-cta hero-cta--secondary">View Fingerprints</a>
  </div>
</div>

---

## Our Keys { #keys }

The full keyring is at `https://anonymousplanet.net/pgp/anonymousplanet.asc`.<br>Always verify fingerprints against our [GitHub releases](https://github.com/Anon-Planet/thgtoa/releases) before importing.

<div class="index-grid">

  <div class="index-card">
    <h3 class="index-card__title">Master Signing Key (MSK)</h3>
    <p class="index-card__body">Announcements, signing subkeys, and trust anchoring. The root of our web of trust.</p>
    <code class="pgp-fingerprint">9FA5 436D 0EE3 6098 5157 3825 17EC A05F 768D EDF6</code>
  </div>

  <div class="index-card">
    <h3 class="index-card__title">Release Signing Key (RSK)</h3>
    <p class="index-card__body">Signs all guide releases and distribution artifacts. Check this against every release.</p>
    <code class="pgp-fingerprint">C302 3DBE A3FB 38C4 38BA 1EED CEC6 0AED E8B9 92A2</code>
  </div>

  <div class="index-card">
    <h3 class="index-card__title">Email Encryption / Signing Key (ESK)</h3>
    <p class="index-card__body">Use this to send us encrypted mail or verify signed correspondence from us.</p>
    <code class="pgp-fingerprint">FCBD 2CAB DEFD 1FBA 2E9E 7591 A1A8 2CD2 DD2C F890</code>
  </div>

</div>

---

## Key Rotation { #rotation }

Keys may be rotated periodically. Rotation is always announced via [GitHub Releases](https://github.com/Anon-Planet/thgtoa/releases) and the [changelog](../changelog/index.md). If a key you have on file does not appear here, treat it as compromised and re-import.

---

## Public Keyring { #keyring }

<div class="donate-address-block">
  <div class="donate-address-label">Keyring URL</div>
  <code class="donate-address">https://anonymousplanet.net/pgp/anonymousplanet.asc</code>
</div>

```txt
-----BEGIN PGP PUBLIC KEY BLOCK-----

mDMEZc0QYxYJKwYBBAHaRw8BAQdAm8mOR8/0qWrm9Tqzfl9Ks5rjtIbQZLAR/qxH
HVGJsxi0LUFub255bW91cyBQbGFuZXQgRW1haWwgRW5jcnlwdGlvbi9TaWduaW5n
IEtleYiTBBMWCgA7FiEE/L0sq979H7ounnWRoags0t0s+JAFAmXNEGMCGwMFCwkI
BwICIgIGFQoJCAsCBBYCAwECHgcCF4AACgkQoags0t0s+JDbRAEAuZlBmMGgZ3bh
12Js9jjDcu+jhKqL4fJrJG5z9+KFkQwA/An1StA6EhcM7qlzZ5bzm2SZAbP9hQRZ
GmfaeU2P5KgHiHgEMBYKACAWIQSfpUNtDuNgmFFXOCUX7KBfdo3t9gUCaiCYTgId
AAAKCRAX7KBfdo3t9gNUAP9/SyGBYJ7s9YeqLHOJ+veQZjZYHvFGQ7yPn0Fetx0Z
LAD/UOQ8rP2QaldCMyVSG8SqfPd7n++SEAXWAl2gAo9mhg6IdQQQFgoAHRYhBJ+l
Q20O42CYUVc4JRfsoF92je32BQJmpEUQAAoJEBfsoF92je32tD8A/ir9hE8UjrJE
psG+PNfxYAwAagKUGbAMDUxQp3z+t81+AP45hYT4aR89zSQaankHLs3Lh7Cp5ael
NBe/BtfR9hCLAYkCMwQQAQgAHRYhBF7WeRgs0hkTAMDm6kyyELegkVLWBQJqIJiM
AAoJEEyyELegkVLWjZYP/j1k5vl+r0NDQXmE8hS9IKhaQPggP72iXc5RWeMQHuIv
b1laQZm64xerJNdAh0uk1bwfmJnVGfyxBUrlCgAIeVGRSlni2Rig4azaQ1IS0pqF
4sC1KzKEhEaNdkh3pJyGtP1cikcSjWeU2oYQou3/7VN3vNyW+n8OAVF+2fsC5d78
EvdpZgal+komb+J8Bt552uDbCCVI4TFIPBZmHWoXjaP6L+730YphbV7Aw0L5J6OO
ob0nzHn4X0dIvGE7Phdp2e1yNRUOSRLh8B/D5OiE9k7CaeYmJNPv5qOw/R+NgrrA
ZFnoOuwHo0D+aL9WT9q4aM/cDCEIbvhQ4l5ZhVGqZuQ9wxNCgPi3ZiZRTfk1PW4v
uMw1xGwXBKy7jDO12xWIWWv9MiwIQLw0OxSxKbr76rgucq7e7JrWr64rItu5Wm7F
8qxg2cwmDat6tFSRVWlEDy8oNkRMJNjdQJDu3ez9YOfJNnApAz94Of1XU7CUuYjY
PV88BaHdUBVtANEzy0iSDCcSj6auzLfv9dBN8cOdUxlVcrPf2jjK6JR/6qe6VWNp
wRg9VQW2fe8HJTMUt0o9qQBJUsF68KOHtIdoE4az9AyyBNKl67dKqLB9HoIItLzD
MJRcbS2p6plCTNagwPVvgtPRChll9JP3jLPVhRL2BixYVkbHUoJxsEfscTUl6Azt
tEtBbm9ueW1vdXMgUGxhbmV0IEVtYWlsIEVuY3J5cHRpb24vU2lnbmluZyBLZXkg
PGFub255bW91c3BsYW5ldEBkaXNyb290Lm9yZz6IkwQTFgoAOxYhBPy9LKve/R+6
Lp51kaGoLNLdLPiQBQJmhqXqAhsDBQsJCAcCAiICBhUKCQgLAgQWAgMBAh4HAheA
AAoJEKGoLNLdLPiQJ34A/RJT9Hyj7hT/0D1BbDU6s6YzD+/x7Pyq2+9kNSI0L77W
AQAAG+CfDrKDXJtBNKZVNFZpld3wUeoIOcAqLl7KpsVGCYh1BBAWCgAdFiEEn6VD
bQ7jYJhRVzglF+ygX3aN7fYFAmakRRAACgkQF+ygX3aN7fbypgEAnEg0IbWnpaLj
/4wU179vUZZu/Y0DE63GbJuZjj72hKUA/0xyzIgSvXByjoOkEwCn5w1+RPYXKw7Z
syERsDCUAAMIiQIzBBABCAAdFiEEXtZ5GCzSGRMAwObqTLIQt6CRUtYFAmogmIwA
CgkQTLIQt6CRUtafPQ/+LTWFU84tDZAM0Hp7bWB0dw8nP0JvNQ2WtZf0flh+r1tF
cmVnc9szZBh+zzSpY25iK5+Waa6+l1POYSQpkS67VR0Jrv9nL94YrRhqalSRWsjW
MQJO+Obu4LIRIqiMZLJlAd9Bg9FshYagbQDVDOI8v9mxqCzIVm3tBx1Jp57ATHgm
sMDWn7l1BI0SkLlG49LYxVDQ6QAx4XLCQw+JzdiJs+yExa5ymYmV61evVVbDV5UF
pEwW6nsuEDc68UN6npjr8OuGH5y+1ot1vaBderoXFZ8hRG/czzODX5L0zGDX9R2C
cGyIrv4AoXTtnbiVZGG6Vn1p3C/RMFZsVOMKvyQKh0rjcD9dqVQ4thI41o92jZ0V
K5ALjPiWe1kM4DVYgk/b46q9/8rjzYb4WJCwPQJkRBp36y26oRWM0JaY2Tobzt/H
3c8d36hQSXtjKLY27ZY5jL0N4vJaiclAuy03wKonmKlUc1ROUBEgNoZcvx6rLx6e
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
Eztpvc4cyyGAmI42SLM/jKbqO2yWqwVoAg==
=ww/S
-----END PGP PUBLIC KEY BLOCK-----
```
