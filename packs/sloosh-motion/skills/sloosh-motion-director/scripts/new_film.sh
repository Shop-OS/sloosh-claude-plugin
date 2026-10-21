#!/usr/bin/env bash
# new_film.sh: scaffold one film folder (Python compositor, HTML type/UI pages, synthesised audio).
#   bash <director>/scripts/new_film.sh <folder> [9x16|16x9|1x1|4x5] [fps]
# Creates: tl.py edit.py audio.py ui/type.html lib/ (filmkit, audiokit, render_html, sheets, kit.js)
#          fonts/ (the vendored OFL fonts and their licences) refs/ plates/ clips/ frames/ out/ audio/
# It installs nothing and downloads nothing.
set -euo pipefail
NAME=${1:?usage: bash new_film.sh <folder> [9x16|16x9|1x1|4x5] [fps]}; FMT=${2:-9x16}; FPS=${3:-30}
CORE="$(cd "$(dirname "$0")/.." && pwd)"
case "$FMT" in
  9x16) W=1080; H=1920;; 16x9) W=1920; H=1080;; 1x1) W=1080; H=1080;; 4x5) W=1080; H=1350;;
  *) echo "format must be 9x16|16x9|1x1|4x5" >&2; exit 1;;
esac
case "$FPS" in
  ''|0*|*[!0-9]*) echo "fps must be a whole number from 1, for example 24 or 30" >&2; exit 1;;
esac
case "$NAME" in
  -*) echo "the folder name must not start with -" >&2; exit 1;;
esac
# never scaffold over a film in progress: cp would replace the user's tl.py, edit.py, audio.py and ui pages
if [ -e "$NAME/tl.py" ] || [ -e "$NAME/edit.py" ]; then
  echo "$NAME already holds a film (tl.py or edit.py). Pick a new folder name; nothing was changed." >&2; exit 1
fi
mkdir -p "$NAME"/{lib,ui,fonts,refs,plates,clips,frames,out,audio}
cp "$CORE"/lib/*.py "$CORE"/lib/kit.js "$NAME/lib/"
cp "$CORE"/templates/tl.py "$CORE"/templates/edit.py "$CORE"/templates/audio.py "$NAME/"
cp "$CORE"/templates/type.html "$NAME/ui/"
# fonts: every vendored OFL face and its licence text, so the pages load them from /fonts/
cp "$CORE"/assets/fonts/*.woff2 "$CORE"/assets/fonts/OFL-*.txt "$NAME/fonts/"
# set the frame size, fps and film name in tl.py (a python edit works the same on every system)
python3 - "$NAME/tl.py" "$W" "$H" "$FPS" "$(basename "$NAME")" <<'PY'
import re, sys
path, w, h, fps, name = sys.argv[1:6]
with open(path, encoding="utf-8") as f:
    src = f.read()
src = re.sub(r"(?m)^W, H, FPS = .*$", "W, H, FPS = %s, %s, %s" % (w, h, fps), src, count=1)
src = re.sub(r'(?m)^NAME = "film"', lambda m: "NAME = %r" % name, src, count=1)
with open(path, "w", encoding="utf-8") as f:
    f.write(src)
PY
(cd "$NAME" && PYTHONDONTWRITEBYTECODE=1 python3 tl.py)
python3 - <<'PY' || true
import importlib
PKG = {"cv2": "opencv-python-headless", "numpy": "numpy", "scipy": "scipy", "playwright": "playwright"}
for m, p in PKG.items():
    try:
        importlib.import_module(m)
    except Exception:
        print(f"!! missing python module {m} (pip package {p}). Ask the user before installing it; prefer a virtual environment.")
PY
command -v ffmpeg >/dev/null || echo "!! ffmpeg missing. Ask the user to install it."
echo "film scaffold ready: $NAME ($W x $H @ $FPS fps). Next: write tl.py (the story on the beat grid), then plan the Sloosh rounds."
ls "$NAME" "$NAME/fonts"
