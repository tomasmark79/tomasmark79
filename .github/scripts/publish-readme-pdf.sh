#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/../.."

git config user.name 'github-actions[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'

# This script runs only in the disposable Actions checkout. Each retry must
# render the latest sources again, rather than rebase a stale binary PDF.
for attempt in 1 2 3; do
  git fetch origin main
  git reset --hard origin/main
  bash .github/scripts/readme-pdf.sh
  git add -- cv/README.pdf
  if git diff --cached --quiet; then
    exit 0
  fi
  git commit -m 'docs: regenerate cv/README.pdf'
  if git push origin HEAD:main; then
    exit 0
  fi
  echo "Publication push failed; retrying with current sources ($attempt/3)"
done

echo 'Could not publish README PDF after three attempts' >&2
exit 1
