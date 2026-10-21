#!/usr/bin/env bash
# setup_film.sh: make a morph film folder from the director scaffold and this style's example.
#   bash scripts/setup_film.sh <film> chain [format] [fps]   # photoreal chain, 9x16 by default
#   bash scripts/setup_film.sh <film> code [format] [fps]    # code-only send morph, 16x9 by default
# format is 9x16, 16x9, 1x1 or 4x5. A whole number in the format place is read as the fps.
# On a folder that already has a director scaffold, a missing format or fps keeps the scaffold's.
# It runs the director's new_film.sh when the folder has no scaffold yet, then copies
# the example (tl.py, edit.py, audio.py, ui pages), morphkit.js, morphfx.py, morphsfx.py,
# logo_to_path.py and the vendored flubber build. It uses no network and installs nothing.
# It refuses to run twice on the same folder, so it never overwrites your edited tl.py,
# edit.py or audio.py. Set MORPH_FORCE=1 to copy the example again on purpose.
set -euo pipefail
FILM=${1:?usage: bash setup_film.sh <film> chain|code [9x16|16x9|1x1|4x5] [fps]}
KIND=${2:-chain}
FMT=${3:-}
FPS=${4:-}
case "$FMT" in
  ''|*[!0-9]*) ;;
  *) FPS=$FMT; FMT= ;;
esac
# an existing director scaffold keeps its own size and fps unless they are given here
if [ -f "$FILM/tl.json" ] && [ -f "$FILM/lib/filmkit.py" ]; then
  SCAF="$(python3 -c 'import json, sys; d = json.load(open(sys.argv[1], encoding="utf-8")); print("%dx%d %d" % (int(d.get("W", 0)), int(d.get("H", 0)), int(d.get("FPS", 0))))' "$FILM/tl.json")"
  if [ -z "$FMT" ]; then
    case "${SCAF% *}" in
      1080x1920) FMT=9x16 ;; 1920x1080) FMT=16x9 ;; 1080x1080) FMT=1x1 ;; 1080x1350) FMT=4x5 ;;
    esac
  fi
  [ -n "$FPS" ] || FPS=${SCAF#* }
fi
FPS=${FPS:-30}
HERE="$(cd "$(dirname "$0")/.." && pwd)"
CORE="$HERE/../sloosh-motion-director"
if [ ! -f "$CORE/scripts/new_film.sh" ]; then
  echo "sloosh-motion-director not found next to this skill. Install the full sloosh-motion plugin, then run this again." >&2
  exit 1
fi
case "$KIND" in
  chain) EX=morph-chain-15s-9x16; FMT=${FMT:-9x16} ;;
  code) EX=send-morph-12s-16x9; FMT=${FMT:-16x9} ;;
  *) echo "kind must be chain or code" >&2; exit 1 ;;
esac
case "$FMT" in
  9x16) W=1080; H=1920 ;; 16x9) W=1920; H=1080 ;; 1x1) W=1080; H=1080 ;; 4x5) W=1080; H=1350 ;;
  *) echo "format must be 9x16, 16x9, 1x1 or 4x5" >&2; exit 1 ;;
esac
case "$FPS" in
  ''|0*|*[!0-9]*) echo "fps must be a whole number from 1, for example 24 or 30" >&2; exit 1 ;;
esac
if [ -f "$FILM/.morph-shapeshift" ] && [ "${MORPH_FORCE:-0}" != "1" ]; then
  echo "$FILM already has the morph example ($(cat "$FILM/.morph-shapeshift")). Nothing copied, so your edits are safe." >&2
  echo "To copy the example again and overwrite tl.py, edit.py, audio.py and ui/*.html, run with MORPH_FORCE=1." >&2
  exit 1
fi
if [ ! -f "$FILM/lib/filmkit.py" ]; then
  bash "$CORE/scripts/new_film.sh" "$FILM" "$FMT" "$FPS"
fi
mkdir -p "$FILM/ui" "$FILM/vendor" "$FILM/lib" "$FILM/clips/locked"
cp "$HERE/examples/$EX/tl.py" "$HERE/examples/$EX/edit.py" "$HERE/examples/$EX/audio.py" "$FILM/"
cp "$HERE/examples/$EX/ui/"*.html "$FILM/ui/"
cp "$HERE/assets/morphkit.js" "$HERE/lib/morphfx.py" "$HERE/lib/morphsfx.py" "$FILM/lib/"
cp "$HERE/scripts/logo_to_path.py" "$FILM/lib/"
cp "$HERE/assets/vendor/flubber.min.js" "$HERE/assets/vendor/flubber.LICENSE" \
   "$HERE/assets/vendor/THIRD_PARTY_NOTICES.txt" "$FILM/vendor/"
NAME="$(basename "$FILM")"
# set the film name, the frame size and the fps in the example tl.py
python3 - "$FILM/tl.py" "$NAME" "$FPS" "$W" "$H" <<'PY'
import re, sys
path, name, fps, w, h = sys.argv[1:6]
with open(path, encoding="utf-8") as f:
    src = f.read()
src = re.sub(r"(?m)^NAME = .*$", lambda m: "NAME = " + repr(name), src, count=1)
src = re.sub(r"(?m)^W, H, FPS = (\d+), (\d+), \d+", lambda m: "W, H, FPS = %s, %s, %s" % (w, h, fps), src, count=1)
with open(path, "w", encoding="utf-8") as f:
    f.write(src)
PY
echo "$KIND $FMT $FPS" > "$FILM/.morph-shapeshift"
(cd "$FILM" && PYTHONDONTWRITEBYTECODE=1 python3 tl.py)
echo "morph-shapeshift ($KIND, $FMT, $FPS fps) ready in $FILM"
echo "next, inside $FILM:"
echo "  python3 '$HERE/scripts/make_placeholders.py' $KIND   (stand-ins until the real files land)"
echo "  python3 lib/logo_to_path.py refs/brand_logo.png --out ui/logo   (the user's real logo; then LOOK at ui/logo_check.png)"
echo "  python3 lib/render_html.py ui/type.html --dur <LEN> --out frames/type --jobs 1"
