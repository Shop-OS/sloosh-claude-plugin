#!/usr/bin/env bash
# new_aura_film.sh: scaffold an aura edit on top of the director toolchain.
#   bash <aura-farming-edit>/scripts/new_aura_film.sh <folder> [9x16|16x9|1x1|4x5] [fps] [--placeholders]
# Runs the director's new_film.sh (it copies the vendored fonts into <folder>/fonts/), then copies the
# velocity_hype example (tl.py, edit.py, audio.py, ui/type.html) and lib/aurakit.py into the film.
# With --placeholders it also writes stand-in plates and clips, so the edit runs before the real shots land.
# No network. Nothing is installed.
set -euo pipefail

PLACEHOLDERS=0
ARGS=()
for a in "$@"; do
  if [ "$a" = "--placeholders" ]; then PLACEHOLDERS=1; else ARGS+=("$a"); fi
done
if [ "${#ARGS[@]}" -lt 1 ]; then
  echo "usage: bash new_aura_film.sh <folder> [9x16|16x9|1x1|4x5] [fps] [--placeholders]" >&2
  exit 1
fi
DIR=${ARGS[0]}
FMT=${ARGS[1]:-9x16}
FPS=${ARGS[2]:-30}

HERE="$(cd "$(dirname "$0")/.." && pwd)"
CORE="$HERE/../sloosh-motion-director"
if [ ! -f "$CORE/scripts/new_film.sh" ]; then
  echo "new_aura_film.sh: the sloosh-motion-director skill was not found next to this skill ($CORE)." >&2
  echo "Install the sloosh-motion plugin, which ships both skills, then run this again." >&2
  exit 1
fi

case "$FMT" in
  9x16) W=1080; H=1920; PW=540; PH=960;;
  16x9) W=1920; H=1080; PW=960; PH=540;;
  1x1)  W=1080; H=1080; PW=540; PH=540;;
  4x5)  W=1080; H=1350; PW=540; PH=676;;
  *) echo "format must be 9x16|16x9|1x1|4x5" >&2; exit 1;;
esac
case "$FPS" in
  ''|0*|*[!0-9]*) echo "fps must be a whole number from 1" >&2; exit 1;;
esac

if [ -e "$DIR/tl.py" ]; then
  echo "new_aura_film.sh: $DIR already holds a film. Pick a new folder; never overwrite a film." >&2
  exit 1
fi

bash "$CORE/scripts/new_film.sh" "$DIR" "$FMT" "$FPS"

EX="$HERE/examples/velocity_hype"
mkdir -p "$DIR/lib" "$DIR/ui" "$DIR/plates" "$DIR/clips" "$DIR/frames" "$DIR/out" "$DIR/audio"
cp "$HERE/lib/aurakit.py" "$DIR/lib/"
cp "$EX/edit.py" "$EX/audio.py" "$DIR/"
cp "$EX/ui/type.html" "$DIR/ui/type.html"

NAME="$(basename "$DIR")"
# set size, fps and name in the copied tl.py (a python edit: any folder name is safe, and it works on every system)
python3 - "$EX/tl.py" "$DIR/tl.py" "$W" "$H" "$FPS" "$NAME" <<'PY'
import re, sys
src_path, dst_path, w, h, fps, name = sys.argv[1:7]
with open(src_path, encoding="utf-8") as f:
    src = f.read()
src = re.sub(r"(?m)^W, H, FPS = .*$", lambda m: "W, H, FPS = %s, %s, %s" % (w, h, fps), src, count=1)
src = re.sub(r'(?m)^NAME = "[^"]*"', lambda m: "NAME = %r" % name, src, count=1)
with open(dst_path, "w", encoding="utf-8") as f:
    f.write(src)
PY
(cd "$DIR" && PYTHONDONTWRITEBYTECODE=1 python3 tl.py)

if [ "$PLACEHOLDERS" = "1" ]; then
  PYTHONDONTWRITEBYTECODE=1 python3 "$HERE/scripts/make_placeholders.py" "$DIR" --n 14 --w "$PW" --h "$PH"
fi

echo "aura film ready: $DIR ($FMT, $FPS fps). Next: write COPY, VO and cue times in tl.py, then"
echo "  cd $DIR && python3 tl.py"
echo "  python3 edit.py out/sheet.jpg <times>    (a picture-only sheet until the type is rendered)"
echo "  python3 lib/render_html.py ui/type.html --dur <LEN> --out frames/type --jobs 1    (needs Playwright)"
