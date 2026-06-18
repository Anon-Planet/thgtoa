#!/bin/bash
# Remove memory/ directory from git history completely
# This rewrites ALL commits to exclude memory/* files

set -e

cd /mnt/e/git/thgtoa

echo "=== Removing memory/ from git history ==="
echo "This will rewrite ALL commit history. Back up first if needed!"

# Backup current HEAD state
export GIT_REPLACE_PREFIX="refs/original/"
git filter-branch --prune-empty --index-filter \
  'git rm -rf --cached --ignore-unmatch memory/' \
  "$(git rev-parse HEAD)"

echo "=== History rewritten ==="
echo "=== Cleaning up refs ==="
# Remove the backup ref
rm -f .git/refs/original/refs/stash 2>/dev/null || true
rmdir .git/refs/original 2>/dev/null || true

# Clean packed-refs
grep -v refs/original .git/packed-refs > .git/packed-refs.tmp || true
mv .git/packed-refs.tmp .git/packed-refs 2>/dev/null || true

echo "=== Verifying memory/ is removed ==="
git log --oneline | tail -5

echo ""
echo "Done! Memory/ directory has been completely removed from history."
echo "Run: git reflog expire --expire=now --all && git gc --aggressive --prune=now"
echo "Then force push to remote to remove traces from others' clones:"
echo "  git push --force-with-lease origin main"
