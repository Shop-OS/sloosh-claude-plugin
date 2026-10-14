#!/usr/bin/env bash
# Fast JPEG sequence render for visual review.
# usage: bash render_review.sh <project_dir> <CompositionId> <out_dir> [from-to]
set -euo pipefail
PROJ="$1"; COMP="$2"; OUT="$3"; RANGE="${4:-}"
mkdir -p "$OUT"; OUT="$(cd "$OUT" && pwd)"
# Clear only the frames an earlier review render wrote, never other files in the folder.
find "$OUT" -maxdepth 1 -type f -name 'element-*.jpeg' -delete
cd "$PROJ"
if [ -n "$RANGE" ]; then FR="--frames=$RANGE"; else FR=""; fi
npx remotion render "$COMP" "$OUT" --sequence --image-format=jpeg --jpeg-quality=85 --concurrency=8 $FR 2>&1 | grep -E "Rendered [0-9]+/[0-9]+$|rror" | tail -2
echo "frames: $(find "$OUT" -maxdepth 1 -name 'element-*.jpeg' | wc -l | tr -d ' ') in $OUT"
