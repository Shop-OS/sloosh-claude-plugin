#!/usr/bin/env bash
# Analyse a reference video: contact sheets, scene-cut times, average shot length.
# usage: bash ref_analyze.sh <ref.mp4> <out_dir> [threshold=0.25]
set -euo pipefail
REF="$1"; OUT="$2"; TH="${3:-0.25}"
mkdir -p "$OUT"
NAME="$(basename "${REF%.*}")"
DUR=$(ffmpeg -hide_banner -i "$REF" 2>&1 | grep -m1 -oE "Duration: [0-9:.]+" | sed 's/Duration: //' || true)
SECS=$(python3 -c "h,m,s='${DUR}'.split(':');print(float(h)*3600+float(m)*60+float(s))")
# ~48 frames across the clip, 6 per row
FPS=$(python3 -c "print(max(0.5, min(8, 48/${SECS})))")
ffmpeg -hide_banner -v error -y -i "$REF" -vf "fps=${FPS},scale=360:-2,tile=6x8:padding=4:color=white" -frames:v 1 "$OUT/${NAME}_sheet.jpg"
CUTS=$(ffmpeg -hide_banner -i "$REF" -vf "select='gt(scene,${TH})',showinfo" -f null - 2>&1 | grep -oE "pts_time:[0-9.]+" | sed 's/pts_time://' | tr '\n' ' ')
N=$(echo "$CUTS" | wc -w | tr -d ' ')
python3 - "$SECS" "$N" "$CUTS" > "$OUT/${NAME}_cuts.txt" <<'PY'
import sys
secs = float(sys.argv[1]); n = int(sys.argv[2]); cuts = [float(x) for x in sys.argv[3].split()]
print(f"duration: {secs:.2f}s  cuts: {n}  avg shot: {secs / (n + 1):.2f}s  shots/sec: {(n + 1) / secs:.2f}")
print("cut times:", " ".join(f"{c:.2f}" for c in cuts))
PY
cat "$OUT/${NAME}_cuts.txt"
echo "sheet: $OUT/${NAME}_sheet.jpg"
