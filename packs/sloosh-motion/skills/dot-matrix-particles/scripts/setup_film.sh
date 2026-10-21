#!/usr/bin/env bash
# setup_film.sh: start a dot-matrix-particles film from the "Data Twin" example.
#
#   bash <this skill>/scripts/setup_film.sh <film_dir> [9x16|16x9|1x1|4x5] [fps]
#
# 1. runs the director's new_film.sh (folders, lib/, vendored fonts; no network)
# 2. copies the example tl.py, edit.py, audio.py and ui/type.html over the scaffold
# 3. copies lib/dotskit.py into the film's lib/
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

if [ -e "$FILM" ]; then
    echo "$FILM already exists. Choose a new folder name." >&2
    exit 1
fi

bash "$CORE/scripts/new_film.sh" "$FILM" "$FMT" "$FPS"

EX="$HERE/examples/data-twin"
mkdir -p "$FILM/lib" "$FILM/ui"
cp "$EX/tl.py" "$EX/edit.py" "$EX/audio.py" "$FILM/"
cp "$EX/ui/type.html" "$FILM/ui/type.html"
cp "$HERE/lib/dotskit.py" "$FILM/lib/dotskit.py"

# The example is written for 1080x1920 at 30 fps; set the chosen size, rate and the film's name.
TMP="$FILM/tl.py.tmp"
awk -v w="$W" -v h="$H" -v f="$FPS" -v n="$(basename "$FILM")" '
    /^W, H, FPS = / { print "W, H, FPS = " w ", " h ", " f; next }
    /^NAME = / { print "NAME = \"" n "\""; next }
    { print }
' "$FILM/tl.py" > "$TMP"
mv "$TMP" "$FILM/tl.py"

echo "Film ready in $FILM ($FMT, $FPS fps)."
if [ "$FMT" != "9x16" ]; then
    echo "The type, the LED board and the placeholders adapt to $FMT. Make the stills at $FMT, then check the focus points in edit.py on them."
fi
echo "Next: cd '$FILM' && python3 tl.py"
