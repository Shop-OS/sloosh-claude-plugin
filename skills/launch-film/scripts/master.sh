#!/usr/bin/env bash
# Render a composition, master its audio (two-pass loudnorm -14 LUFS / -1 dBTP) and mux.
# usage: bash master.sh <project_dir> <CompositionId> <out_basename> [--4k]
# Produces <project>/out/<out_basename>_1080p.mp4 (and _4K.mp4 with --4k).
set -euo pipefail
PROJ="$1"; COMP="$2"; NAME="$3"; FOURK="${4:-}"
cd "$PROJ"
mkdir -p out
npx remotion render "$COMP" "out/_${NAME}_mix.wav" --codec=wav >/dev/null
J="out/_${NAME}_ln.json"
ffmpeg -hide_banner -nostats -i "out/_${NAME}_mix.wav" -af "loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json" -f null - 2>&1 | sed -n '/{/,/}/p' > "$J"
rd() { python3 -c "import json;print(json.load(open('$J'))['$1'])"; }
MI=$(rd input_i); MTP=$(rd input_tp); MLRA=$(rd input_lra); MTH=$(rd input_thresh); OFF=$(rd target_offset)
AF="loudnorm=I=-14:TP=-1.0:LRA=11:measured_I=${MI}:measured_TP=${MTP}:measured_LRA=${MLRA}:measured_thresh=${MTH}:offset=${OFF}:linear=true,aresample=48000"
ffmpeg -hide_banner -v error -y -i "out/_${NAME}_mix.wav" -af "$AF" -c:a pcm_s24le "out/_${NAME}_master.wav"
render_mux() { # $1 suffix, $2 extra flags
  npx remotion render "$COMP" "out/_${NAME}_${1}_video.mp4" --codec=h264 --crf="$3" --x264-preset=slow --color-space=bt709 --concurrency=8 $2 >/dev/null
  ffmpeg -hide_banner -v error -y -i "out/_${NAME}_${1}_video.mp4" -i "out/_${NAME}_master.wav" -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 320k -ar 48000 -movflags +faststart -shortest "out/${NAME}_${1}.mp4"
  rm -f "out/_${NAME}_${1}_video.mp4"
  echo "out/${NAME}_${1}.mp4"
}
render_mux 1080p "" 14
if [ "$FOURK" = "--4k" ]; then render_mux 4K "--scale=2" 16; fi
ffmpeg -hide_banner -nostats -i "out/${NAME}_1080p.mp4" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
