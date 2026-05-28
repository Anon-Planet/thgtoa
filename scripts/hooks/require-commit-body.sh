#!/usr/bin/env bash

COMMIT_MSG_FILE="$1"

if [ -z "$COMMIT_MSG_FILE" ]; then
  echo "require-commit-body: no commit message file supplied" >&2
  exit 1
fi

stripped=$(grep -v '^\s*#' "$COMMIT_MSG_FILE" | sed 's/[[:space:]]*$//')

subject=$(echo "$stripped" | sed -n '1p')
separator=$(echo "$stripped" | sed -n '2p')
body=$(echo "$stripped" | tail -n +3 | grep -v '^\s*$')

if [ -z "$subject" ]; then
  echo ""
  echo "  COMMIT REJECTED: subject line is empty." >&2
  echo ""
  exit 1
fi

if [ -z "$separator" ] && [ -z "$body" ]; then
  echo ""
  echo "  COMMIT REJECTED: commit has no body." >&2
  echo ""
  echo "  Every commit must explain *why*, not just *what*." >&2
  echo "  Format:" >&2
  echo ""
  echo "    type(scope): short subject" >&2
  echo ""
  echo "    Explain the motivation for this change. What problem does" >&2
  echo "    it solve? Why is this the right approach? Reference any" >&2
  echo "    relevant issues, prior art, or context." >&2
  echo ""
  exit 1
fi

if [ -n "$separator" ]; then
  echo ""
  echo "  COMMIT REJECTED: no blank line between subject and body." >&2
  echo ""
  echo "  The second line of a commit message must be blank." >&2
  echo ""
  exit 1
fi

if [ -z "$body" ]; then
  echo ""
  echo "  COMMIT REJECTED: commit body is empty." >&2
  echo ""
  echo "  Add at least one line after the blank separator explaining" >&2
  echo "  why this change was made." >&2
  echo ""
  exit 1
fi

exit 0
