# Import

```bash
$ gpg --import pgp/core-devs/*
```

# Verify

```bash
$ gpg --verify pgp/core-devs/than/than-crypto.txt


gpg: Signature made Sat 19 Jul 2025 02:04:10 AM EDT
gpg:                using EDDSA key 8B3A74890536BAD50D9376EBF1CB32F67E3302A1
gpg: Good signature from "nopenothinghere@proton.me <nopenothinghere@proton.me>" [ultimate]
gpg:                 aka "Nope Nothing (Anonymous Planet Contact) <no@anonymousplanet.org>" [ultimate]
gpg:                 aka "Nope Nothing (Systems Administrator) <admin@itsnothing.net>" [ultimate]
Primary key fingerprint: 8B3A 7489 0536 BAD5 0D93  76EB F1CB 32F6 7E33 02A1
```

## All signing keys are signed by the Master Signing Key

TODO

