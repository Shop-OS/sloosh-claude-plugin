#!/usr/bin/env bash
# 2x Lanczos upscale + light unsharp for images shown larger than ~1.1x.
# usage: bash upscale_hd.sh <src_dir> <out_dir> NAME [NAME…]   (NAME = file name without extension)
set -euo pipefail
SRC="$1"; OUT="$2"; shift 2
mkdir -p "$OUT"
for n in "$@"; do
  f=$(ls "$SRC/$n".* 2>/dev/null | head -1)
  [ -z "$f" ] && { echo "missing $n" >&2; continue; }
  ffmpeg -hide_banner -v error -y -i "$f" -vf "scale=iw*2:ih*2:flags=lanczos+accurate_rnd+full_chroma_int,unsharp=5:5:0.55:5:5:0.0" -q:v 2 "$OUT/$n.jpg"
  echo "$OUT/$n.jpg"
done
