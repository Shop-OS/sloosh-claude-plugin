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
  echo "installing whisper-cpp via Homebrew…" >&2
  HOMEBREW_NO_AUTO_UPDATE=1 brew install whisper-cpp >/dev/null
  CLI="$(command -v whisper-cli)"
fi
MDIR="${WHISPER_MODELS:-$HOME/.cache/whisper-cpp}"
mkdir -p "$MDIR"
MFILE="$MDIR/ggml-${MODEL}.bin"
if [ ! -s "$MFILE" ]; then
  echo "downloading ggml-${MODEL}.bin…" >&2
  curl -L --fail -s -o "$MFILE" "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-${MODEL}.bin"
fi
BASE="$(basename "${VO%.*}" | tr ' ' '_')"
WAV="$OUT/${BASE}_16k.wav"
ffmpeg -hide_banner -loglevel error -y -i "$VO" -ar 16000 -ac 1 -c:a pcm_s16le "$WAV"
"$CLI" -m "$MFILE" -f "$WAV" -ml 1 -sow -oj -of "$OUT/${BASE}_words" >/dev/null 2>&1
ffmpeg -hide_banner -i "$VO" -af silencedetect=noise=-35dB:d=0.18 -f null - 2>&1 \
  | grep -oE "silence_(start|end): [0-9.]+" > "$OUT/${BASE}_silences.txt" || true
DUR=$(ffmpeg -hide_banner -i "$VO" 2>&1 | grep -m1 -oE "Duration: [0-9:.]+" | sed 's/Duration: //' || true)
python3 "$HERE/vo_phrases.py" "$OUT/${BASE}_words.json" "$OUT/${BASE}_silences.txt" "$DUR" "$OFFSET" "$OUT/${BASE}_phrases.json"
