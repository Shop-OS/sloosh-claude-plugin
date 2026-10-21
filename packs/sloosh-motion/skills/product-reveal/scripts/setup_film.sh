#!/usr/bin/env bash
# setup_film.sh: start a product-reveal film from the Dark Luxury example.
#
#   bash <this skill>/scripts/setup_film.sh <film_dir> [9x16|16x9|1x1|4x5] [fps]
#
# 1. runs the director's new_film.sh (folders, lib/, vendored fonts; no network)
# 2. copies the example tl.py, edit.py, audio.py, ui/type.html and ui/packshot.html over the scaffold
# 3. copies assets/reveal.js into the film's lib/
# 4. sets the frame size, fps and film name in tl.py (tl.py picks the packshot box for that format), then runs it
# It downloads and installs nothing. It refuses a folder that already exists.
set -eu

HERE="$(cd "$(dirname "$0")/.." && pwd)"
CORE="$HERE/../sloosh-motion-director"

if [ ! -f "$CORE/scripts/new_film.sh" ]; then
    echo "The sloosh-motion-director skill is missing next to this skill." >&2
    echo "Install the full sloosh-motion plugin pack, then run this again." >&2
    exit 1
fi

if [ $# -lt 1 ]; then
    echo "usage: bash $0 <film_dir> [9x16|16x9|1x1|4x5] [fps]" >&2
    exit 2
fi

FILM="$1"
FMT="${2:-9x16}"
FPS="${3:-30}"

case "$FMT" in
    9x16) W=1080; H=1920 ;;
    16x9) W=1920; H=1080 ;;
    1x1) W=1080; H=1080 ;;
    4x5) W=1080; H=1350 ;;
    *) echo "unknown format: $FMT (use 9x16, 16x9, 1x1 or 4x5)" >&2; exit 2 ;;
esac

case "$FPS" in
    ''|0*|*[!0-9]*) echo "fps must be a whole number from 1: $FPS" >&2; exit 2 ;;
esac

case "$FILM" in
    -*) echo "the folder name must not start with -" >&2; exit 2 ;;
esac

if [ -e "$FILM" ]; then
    echo "$FILM already exists. Choose a new folder name; nothing was changed." >&2
    exit 1
fi

if ! OUT="$(bash "$CORE/scripts/new_film.sh" "$FILM" "$FMT" "$FPS")"; then
    printf '%s\n' "$OUT" >&2; exit 1
fi
printf '%s\n' "$OUT" | grep '^!!' >&2 || true    # keep the director's missing-module and ffmpeg hints

EX="$HERE/examples/dark_luxury"
cp "$EX/tl.py" "$EX/edit.py" "$EX/audio.py" "$FILM/"
cp "$EX/ui/type.html" "$EX/ui/packshot.html" "$FILM/ui/"
cp "$HERE/assets/reveal.js" "$FILM/lib/"

python3 - "$FILM/tl.py" "$W" "$H" "$FPS" "$(basename "$FILM")" <<'PY'
import re, sys
path, w, h, fps, name = sys.argv[1:6]
with open(path, encoding="utf-8") as f:
    src = f.read()
src = re.sub(r"(?m)^W, H, FPS = \d+, \d+, \d+", "W, H, FPS = %s, %s, %s" % (w, h, fps), src, count=1)
src = re.sub(r'(?m)^NAME = "[^"]*"', lambda m: "NAME = %r" % name, src, count=1)
with open(path, "w", encoding="utf-8") as f:
    f.write(src)
PY

(cd "$FILM" && PYTHONDONTWRITEBYTECODE=1 python3 tl.py)
echo "product-reveal film ready: $FILM ($W x $H @ $FPS fps)"
echo "next, inside $FILM: python3 '$HERE/scripts/make_placeholders.py' ."
