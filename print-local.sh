#!/usr/bin/env bash
#
# Render Brother-calibrated PRINT copies of the booklets, for local printing only.
#
# The published PDFs (release.sh) are printer-neutral, so anyone can print them. But an
# auto-duplex printer lands the front side a few millimetres off the back, which shows as a
# left/right jog between facing pages. This script bakes in a duplex-shift correction tuned to
# OUR printer (Brother MFC-L3720CDW: the front lands ~4 mm right of the back) so our own
# hand-out copies come out aligned. It writes <name>-print.pdf; the plain <name>.pdf and the
# GitHub release stay uncorrected.
#
# Do NOT publish the -print.pdf copies — the shift is wrong for any other printer.
#
# Usage: ./print-local.sh            # uses DUPLEX_SHIFT (default 4mm)
#        DUPLEX_SHIFT=3mm ./print-local.sh
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEXISH_DIR="${TEXISH_DIR:-$HOME/dev/texish}"
SHIFT="${DUPLEX_SHIFT:-4mm}"
SCRIPTS=(en fr es pt it zh-Hans zh-Hant ar he)

# Build a temporary copy of each script with the duplex correction injected into its \arrange
# directive. The arrange line is the only non-comment use of two-up-booklet (comment mentions are
# inert), so a plain text substitution is safe. The temp lives beside the script so the \usfm
# relative paths still resolve.
runs=()
temps=()
for name in "${SCRIPTS[@]}"; do
  tmp="$REPO_DIR/$name-print.script"
  content="$(cat "$REPO_DIR/$name.script")"
  printf '%s\n' "${content//\\arrange two-up-booklet/\\arrange two-up-booklet duplexshift:$SHIFT}" > "$tmp"
  runs+=("texishCli/run \"$tmp\"")
  temps+=("$tmp")
done

echo "Rendering ${#SCRIPTS[@]} calibrated print copy(ies) (duplexshift:$SHIFT)..."
( cd "$TEXISH_DIR" && sbt -error "${runs[@]}" )

rm -f "${temps[@]}"

for name in "${SCRIPTS[@]}"; do
  [ -f "$REPO_DIR/$name-print.pdf" ] || { echo "error: $name-print.pdf was not produced" >&2; exit 1; }
done

echo "Wrote calibrated print copies: ${SCRIPTS[*]/%/-print.pdf}"
echo "These are for our printer only — do not publish them."
