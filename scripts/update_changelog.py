#!/usr/bin/env python3
"""Auto-generate and prepend a changelog entry to docs/changelog/index.md.

Called by .github/workflows/04-changelog.yml. Reads git log since the last
changelog version, categorises commits by conventional-commit prefix,
and prepends a new ## [vX.Y.Z] section in the MkDocs admonition format used
by the rest of the file.

Environment variables:
  MANUAL_VERSION   Version string to record (required when run from CI).
                   Falls back to auto-increment from the changelog for local runs.
  TRIGGERING_SHA   The commit SHA that triggered this run (used as range end).
  DRY_RUN          If "true", print the entry and exit without writing.

Note: version is sourced from the changelog file, not from git tags. Git tags
are no longer used as the version authority. The changelog is the source of truth.
"""

from __future__ import annotations

import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


CHANGELOG = Path(__file__).resolve().parent.parent / "docs" / "changelog" / "index.md"

# Conventional-commit prefixes → changelog bucket
BUCKET_MAP: dict[str, str] = {
    "feat":     "Added",
    "feature":  "Added",
    "add":      "Added",
    "fix":      "Fixed",
    "bugfix":   "Fixed",
    "perf":     "Changed",
    "refactor": "Changed",
    "change":   "Changed",
    "chore":    "Changed",
    "ci":       "Changed",
    "docs":     "Changed",
    "style":    "Changed",
    "test":     "Changed",
    "revert":   "Fixed",
    "security": "Fixed",
    "build":    "Changed",
}

BUCKET_ORDER = ["Added", "Changed", "Fixed"]


def run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()


def auto_increment_version(current: str | None) -> str:
    """Bump the patch number of the current version, or default to v1.0.0."""
    if not current:
        return "v1.0.0"
    m = re.match(r"^v?(\d+)\.(\d+)\.(\d+)", current)
    if not m:
        return "v1.0.0"
    major, minor, patch = int(m.group(1)), int(m.group(2)), int(m.group(3))
    return f"v{major}.{minor}.{patch + 1}"


def version_from_changelog() -> str | None:
    """Parse the most recent ## [vX.Y.Z] heading from the changelog file.

    This is the primary version source — the changelog is the authority,
    not git tags.
    """
    if not CHANGELOG.exists():
        return None
    for line in CHANGELOG.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^## \[(v\d+\.\d+\.\d+)\]", line)
        if m:
            return m.group(1)
    return None


def commits_since(ref: str | None, until: str) -> list[str]:
    """Return one-line commit messages between ref and until (exclusive/inclusive).

    When no ref is given we fall back to the merge-base between HEAD and
    origin/main to avoid dumping the entire history into the changelog.
    """
    if ref:
        log_range = f"{ref}..{until}"
    else:
        merge_base = run(["git", "merge-base", "HEAD", "origin/main"])
        if merge_base:
            log_range = f"{merge_base}..{until}"
        else:
            # Truly brand new repo with no remote — limit to last 50 commits
            log_range = f"-50 {until}"
    out = run(["git", "log", "--pretty=format:%s", log_range])
    return [line.strip() for line in out.splitlines() if line.strip()]


def categorise(messages: list[str]) -> dict[str, list[str]]:
    """Sort commit messages into Added / Changed / Fixed buckets."""
    buckets: dict[str, list[str]] = {b: [] for b in BUCKET_ORDER}

    NOISE = re.compile(
        r"""
        \[skip\ ci\]                     # CI skip marker
        | ^Merge\ (pull\ request|branch) # merge commits
        | ^chore:\ bump                  # version bump chores
        | update\ changelog              # self-referential
        | ^\d+/\d+                       # numbered commit series (e.g. 3/8)
        | ^Tweaking                      # vague WIP messages
        | ^Moving\ some                  # vague WIP messages
        | \ pt\d+$                       # "...pt2", "...pt3" suffixes
        | ^Fix\ (workflow|path|README)$  # one-word infrastructure fixes
        | ^Still\ broken                 # embarrassing mid-fix notes
        | ^WIP\b                         # work in progress
        | ^Forgot\ to                    # oops commits
        | ^Revert\ "                     # reverts (surface the original instead)
        | ^One\ job\ to\ rule            # joke commit messages
        """,
        re.VERBOSE | re.IGNORECASE,
    )

    for msg in messages:
        if NOISE.search(msg):
            continue

        m = re.match(r"^(\w+)(?:\([^)]+\))?!?:\s*(.+)$", msg)
        if m:
            prefix = m.group(1).lower()
            description = m.group(2).strip()
            bucket = BUCKET_MAP.get(prefix, "Changed")
        else:
            description = msg
            bucket = "Changed"

        description = description[0].upper() + description[1:] if description else description
        buckets[bucket].append(description)

    return buckets


def format_admonition(bucket: str, items: list[str]) -> str:
    lines = [f'!!! Note "{bucket}"', ""]
    for item in items:
        lines.append(f"    - {item}")
    lines.append("")
    return "\n".join(lines)


def build_entry(version: str, buckets: dict[str, list[str]], sha: str) -> str:
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [f"## [{version}]", ""]
    lines.append('!!! Note "Meta"')
    lines.append("")
    lines.append(f"    - Released {date} from [`{sha[:7]}`](https://github.com/Anon-Planet/thgtoa/commit/{sha})")
    lines.append("")

    for bucket in BUCKET_ORDER:
        if buckets.get(bucket):
            lines.append(format_admonition(bucket, buckets[bucket]))

    if not any(buckets[b] for b in BUCKET_ORDER):
        lines.append('!!! Note "Changed"')
        lines.append("")
        lines.append("    - Minor updates and maintenance")
        lines.append("")

    return "\n".join(lines)


def prepend_entry(entry: str) -> None:
    """Insert the new entry after the # Release Notes heading."""
    content = CHANGELOG.read_text(encoding="utf-8")

    insert_at = content.find("\n## ")
    if insert_at == -1:
        content = content.rstrip() + "\n\n" + entry + "\n"
    else:
        content = content[: insert_at + 1] + entry + "\n" + content[insert_at + 1 :]

    CHANGELOG.write_text(content, encoding="utf-8")


def already_has_version(version: str) -> bool:
    if not CHANGELOG.exists():
        return False
    return f"## [{version}]" in CHANGELOG.read_text(encoding="utf-8")


def main() -> int:
    dry_run        = os.environ.get("DRY_RUN", "false").lower() == "true"
    manual_version = os.environ.get("MANUAL_VERSION", "").strip()
    triggering_sha = os.environ.get("TRIGGERING_SHA", "HEAD").strip() or "HEAD"

    # Version authority: MANUAL_VERSION (required in CI) → changelog → auto-increment.
    # Git tags are intentionally not consulted.
    last_cl_ver = version_from_changelog()
    new_version = manual_version or auto_increment_version(last_cl_ver)

    print(f"Last CL version:  {last_cl_ver or '(none)'}")
    print(f"New version:      {new_version}")
    print(f"Triggering SHA:   {triggering_sha}")

    if already_has_version(new_version) and not manual_version:
        print(f"Changelog already contains {new_version} — nothing to do.")
        return 0

    if already_has_version(new_version) and manual_version:
        print(f"::error::Changelog already contains {new_version}. Choose a different version.")
        return 1

    # Collect commits since the last changelog version (using it as a git ref
    # is a best-effort — if the tag doesn't exist, commits_since handles it gracefully).
    messages = commits_since(last_cl_ver, triggering_sha)
    print(f"Commits found:    {len(messages)}")
    for m in messages:
        print(f"  {m}")

    buckets = categorise(messages)
    entry   = build_entry(new_version, buckets, triggering_sha)

    print("\n--- Generated entry ---")
    print(entry)
    print("-----------------------\n")

    if dry_run:
        print("DRY RUN — not writing to file.")
        return 0

    prepend_entry(entry)
    print(f"Prepended {new_version} to {CHANGELOG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
