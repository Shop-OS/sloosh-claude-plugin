#!/usr/bin/env bash
# Blend the frames either side of a cut 50/50 (with a grid) to verify a match cut.
# usage: bash blend_check.sh <seq_dir|video.mp4> <cut_frame> <out.jpg>
set -euo pipefail
SRC="$1"; F="$2"; OUT="$3"
A=$((F-1))
if [ -d "$SRC" ]; then
  pick() { for pad in 3 4 5; do p=$(printf "%s/element-%0${pad}d.jpeg" "$SRC" "$1"); [ -f "$p" ] && { echo "$p"; return; }; done; }
  IA=$(pick "$A"); IB=$(pick "$F")
  ffmpeg -hide_banner -v error -y -i "$IA" -i "$IB" -filter_complex "[0]scale=1280:720[a];[1]scale=1280:720[b];[a][b]blend=all_mode=average,drawgrid=w=128:h=72:t=1:c=red@0.35" "$OUT"
else
  ffmpeg -hide_banner -v error -y -i "$SRC" -vf "select='eq(n\,$A)+eq(n\,$F)',scale=1280:720,tile=2x1" -frames:v 1 "${OUT%.jpg}_pair.jpg"
  ffmpeg -hide_banner -v error -y -i "$SRC" -filter_complex "[0]select='eq(n\,$A)',scale=1280:720,setpts=N[a];[0]select='eq(n\,$F)',scale=1280:720,setpts=N[b];[a][b]blend=all_mode=average,drawgrid=w=128:h=72:t=1:c=red@0.35" -frames:v 1 "$OUT"
fi
echo "$OUT"
