#!/usr/bin/env bash
# Transcode a clip to renderer-friendly H.264 8-bit 1920x1080 (cover crop), keep fps, no audio.
# usage: bash prep_video.sh <in> <out.mp4> [crf=12]
set -euo pipefail
IN="$1"; OUT="$2"; CRF="${3:-12}"
mkdir -p "$(dirname "$OUT")"
ffmpeg -hide_banner -v error -y -i "$IN" -an \
  -vf "scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,crop=1920:1080,format=yuv420p" \
  -c:v libx264 -preset slow -crf "$CRF" -profile:v high -pix_fmt yuv420p -movflags +faststart "$OUT"
ffmpeg -hide_banner -i "$OUT" 2>&1 | grep -E "Duration|Video:" | sed 's/^ *//'
