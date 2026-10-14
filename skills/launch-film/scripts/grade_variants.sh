#!/usr/bin/env bash
# Graded "direction" variants of one image (warm, cool, golden, mono, dusk) — illustrative.
# usage: bash grade_variants.sh <in.jpg> <out_dir> <prefix> [width=1280]
set -euo pipefail
IN="$1"; OUT="$2"; P="$3"; WID="${4:-1280}"
mkdir -p "$OUT"
g() { ffmpeg -hide_banner -v error -y -i "$IN" -vf "scale=${WID}:-2,$2" -q:v 3 "$OUT/${P}_$1.jpg"; echo "$OUT/${P}_$1.jpg"; }
g warm   "colorbalance=rs=0.18:gs=0.02:bs=-0.16:rm=0.14:gm=0.03:bm=-0.12:rh=0.08:bh=-0.08,eq=contrast=1.06:saturation=1.15:gamma=0.97"
g cool   "colorbalance=rs=-0.12:bs=0.2:rm=-0.08:bm=0.14:rh=-0.04:bh=0.06,eq=contrast=1.08:saturation=0.9:brightness=-0.02"
g golden "colorbalance=rs=0.08:bs=-0.05:rm=0.22:gm=0.1:bm=-0.2:rh=0.16:gh=0.08:bh=-0.14,eq=contrast=1.12:saturation=1.25:gamma=1.04"
g mono   "hue=s=0,eq=contrast=1.28:brightness=0.01"
g dusk   "colorbalance=rs=0.14:gs=-0.06:bs=0.22:rm=0.12:gm=-0.05:bm=0.12:rh=0.05:bh=0.05,eq=contrast=1.1:saturation=1.2:gamma=0.95"
