#!/usr/bin/env bash
# Word-level transcription of a voiceover with whisper.cpp, cross-checked against
# ffmpeg silencedetect, then merged into phrases.json + a timeline.ts block.
# usage: bash transcribe.sh <vo_audio> <out_dir> [offset_seconds=0.5] [model=small.en]
set -euo pipefail
VO="$1"; OUT="$2"; OFFSET="${3:-0.5}"; MODEL="${4:-small.en}"
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$OUT"
CLI="$(command -v whisper-cli || true)"
if [ -z "$CLI" ]; then
  echo "whisper-cli not found. Install whisper.cpp first (on macOS: brew install whisper-cpp)." >&2
  exit 2
fi
MDIR="${WHISPER_MODELS:-$HOME/.cache/whisper-cpp}"
MFILE="$MDIR/ggml-${MODEL}.bin"
if [ ! -s "$MFILE" ]; then
  echo "Speech model $MFILE not found. Download ggml-${MODEL}.bin from" >&2
  echo "https://huggingface.co/ggerganov/whisper.cpp into $MDIR first." >&2
  exit 2
fi
BASE="$(basename "${VO%.*}" | tr ' ' '_')"
WAV="$OUT/${BASE}_16k.wav"
ffmpeg -hide_banner -loglevel error -y -i "$VO" -ar 16000 -ac 1 -c:a pcm_s16le "$WAV"
"$CLI" -m "$MFILE" -f "$WAV" -ml 1 -sow -oj -of "$OUT/${BASE}_words" >/dev/null 2>&1
ffmpeg -hide_banner -i "$VO" -af silencedetect=noise=-35dB:d=0.18 -f null - 2>&1 \
  | grep -oE "silence_(start|end): [0-9.]+" > "$OUT/${BASE}_silences.txt" || true
DUR=$(ffmpeg -hide_banner -i "$VO" 2>&1 | grep -m1 -oE "Duration: [0-9:.]+" | sed 's/Duration: //' || true)
python3 "$HERE/vo_phrases.py" "$OUT/${BASE}_words.json" "$OUT/${BASE}_silences.txt" "$DUR" "$OFFSET" "$OUT/${BASE}_phrases.json"
