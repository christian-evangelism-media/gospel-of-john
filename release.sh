#!/usr/bin/env bash
#
# Render the booklet PDFs and publish them as a dated GitHub release.
#
# The version is today's date (YYYY.MM.DD). Re-running on the same day replaces
# that day's release, so the date version stays idempotent.
#
# Requires:
#   - the texish CLI (the sbt project at $TEXISH_DIR, default ~/dev/texish)
#   - the GitHub CLI `gh`, authenticated with write access to this repo
#
# Usage: ./release.sh
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEXISH_DIR="${TEXISH_DIR:-$HOME/dev/texish}"
VERSION="$(date +%Y.%m.%d)"

# Each name renders <name>.script to <name>.pdf and ships as a release asset.
# Add a language edition by adding its name here.
SCRIPTS=(en fr)

runs=()
assets=()
for name in "${SCRIPTS[@]}"; do
  runs+=("texishCli/run $REPO_DIR/$name.script")
  assets+=("$REPO_DIR/$name.pdf")
done

echo "Rendering ${#SCRIPTS[@]} booklet(s) with texish ($TEXISH_DIR)…"
( cd "$TEXISH_DIR" && sbt -error "${runs[@]}" )

for f in "${assets[@]}"; do
  [ -f "$f" ] || { echo "error: $f was not produced" >&2; exit 1; }
done

echo "Publishing release $VERSION…"
cd "$REPO_DIR"
gh release delete "$VERSION" --yes --cleanup-tag 2>/dev/null || true
gh release create "$VERSION" "${assets[@]}" \
  --title "$VERSION" \
  --notes "Gospel of John pocket booklets, rendered $VERSION."

echo "Released $VERSION with: ${SCRIPTS[*]}"
