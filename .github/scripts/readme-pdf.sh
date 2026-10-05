#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/../.."
build_dir=$(mktemp -d)
trap 'rm -rf "$build_dir"' EXIT

pandoc README.md --from=gfm --to=html5 --standalone \
  --metadata pagetitle="Tomáš Mark — Projects" \
  --css=.github/scripts/readme-pdf.css --embed-resources \
  --output="$build_dir/README.html"

"${CHROME_BIN:-google-chrome}" --headless --no-sandbox --disable-gpu \
  --user-data-dir="$build_dir/chrome" --no-pdf-header-footer \
  --print-to-pdf="$build_dir/README.pdf" "file://$build_dir/README.html"

test -s "$build_dir/README.pdf"
cp "$build_dir/README.pdf" README.pdf
