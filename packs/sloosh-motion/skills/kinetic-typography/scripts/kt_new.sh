#!/usr/bin/env bash
# kt_new.sh: scaffold a kinetic-typography film on top of the director toolchain, ready to render.
#   bash <kinetic-typography>/scripts/kt_new.sh <folder> <poster|swiss|editorial|lyric|stretch|list> [9x16|16x9|1x1|4x5] [fps]
# Runs the director's new_film.sh (it copies the vendored fonts into <folder>/fonts/), then copies lib/ktkit.js lib/kt.css
# lib/ktfield.py, the preset's tl.py and ui page, and the shared edit.py / audio.py. No network.
# Then: edit tl.py (copy, beats, fields), python3 tl.py, render the page.
set -euo pipefail
DIR=${1:?folder}; PRESET=${2:-poster}; FMT=${3:-9x16}; FPS=${4:-30}
HERE="$(cd "$(dirname "$0")/.." && pwd)"; CORE="$HERE/../sloosh-motion-director"
if [ ! -f "$CORE/scripts/new_film.sh" ]; then
  echo "kt_new.sh: the sloosh-motion-director skill was not found next to this skill ($CORE)." >&2
  echo "Install the sloosh-motion plugin, which ships both skills, then run this again." >&2
  exit 1
fi
case "$PRESET" in
  poster) EX=bold-poster; PG=kt_poster;; swiss) EX=swiss-clean; PG=kt_swiss;; editorial) EX=editorial-serif; PG=kt_editorial;;
  lyric) EX=lyric-beat; PG=kt_lyric;; stretch) EX=variable-stretch; PG=kt_stretch;; list) EX=scroll-list; PG=kt_list;;
  *) echo "preset must be poster|swiss|editorial|lyric|stretch|list" >&2; exit 1;;
esac
case "$FMT" in
  9x16) W=1080; H=1920;; 16x9) W=1920; H=1080;; 1x1) W=1080; H=1080;; 4x5) W=1080; H=1350;;
  *) echo "format must be 9x16|16x9|1x1|4x5" >&2; exit 1;;
esac
if [ -e "$DIR/tl.py" ]; then
  echo "kt_new.sh: $DIR already holds a film (tl.py exists). Choose a new folder; nothing was changed." >&2
  exit 1
fi
if ! OUT="$(bash "$CORE/scripts/new_film.sh" "$DIR" "$FMT" "$FPS")"; then
  printf '%s\n' "$OUT" >&2; exit 1
fi
printf '%s\n' "$OUT" | grep '^!!' >&2 || true     # keep the director's missing-module and ffmpeg hints
cp "$HERE"/lib/ktkit.js "$HERE"/lib/kt.css "$HERE"/lib/ktfield.py "$DIR/lib/"
cp "$HERE/examples/bold-poster/edit.py" "$HERE/examples/bold-poster/audio.py" "$DIR/"
cp "$HERE/examples/$EX/ui/$PG.html" "$DIR/ui/"; rm -f "$DIR/ui/type.html"     # the kinetic page replaces the director type layer
NAME="$(basename "$DIR")"
# set size, fps and name in the copied tl.py (a python edit: portable, and safe for any folder name)
python3 - "$HERE/examples/$EX/tl.py" "$DIR/tl.py" "$W" "$H" "$FPS" "$NAME" <<'PY'
import re, sys
src_path, dst_path, w, h, fps, name = sys.argv[1:7]
with open(src_path, encoding="utf-8") as f:
    src = f.read()
src = re.sub(r"(?m)^W, H, FPS = .*$", "W, H, FPS = %s, %s, %s" % (w, h, fps), src, count=1)
src = re.sub(r'(?m)^NAME = "[^"]*"', lambda m: "NAME = %r" % name, src, count=1)
with open(dst_path, "w", encoding="utf-8") as f:
    f.write(src)
PY
(cd "$DIR" && PYTHONDONTWRITEBYTECODE=1 python3 tl.py)
echo "kinetic film ready: $DIR ($PRESET, $FMT). Next: write COPY/TYPE/FIELDS in tl.py, then"
echo "  python3 '$HERE/scripts/kt_sheet.py' '$DIR' ui/$PG.html            # two measured stills per scene of the page over its fields, in seconds"
echo "  python3 lib/render_html.py ui/$PG.html --dur <LEN> --out frames/$PG --jobs 1 && python3 edit.py out/sheet.jpg <times>"
