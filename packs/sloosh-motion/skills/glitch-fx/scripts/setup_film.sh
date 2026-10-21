#!/usr/bin/env bash
# setup_film.sh: start a glitch-fx film from the "Signal Lost" example.
#   bash <glitch-fx>/scripts/setup_film.sh <film_dir> [9x16|16x9|1x1|4x5] [fps] [--placeholders]
# 1. runs the director's new_film.sh (folders, lib/, vendored fonts)
# 2. copies the example tl.py, edit.py, audio.py, ui/type.html, ui/hud.html and lib/glitchkit.py into the film
# 3. sets the chosen frame size, fps and the film's name in tl.py, then runs tl.py
# 4. with --placeholders, makes the free stand-in plates and clips (scripts/make_placeholders.py)
# It downloads and installs nothing. new_film.sh refuses a folder that already holds a film.
set -euo pipefail
usage() { echo "usage: bash setup_film.sh <film_dir> [9x16|16x9|1x1|4x5] [fps] [--placeholders]" >&2; exit 2; }
HERE="$(cd "$(dirname "$0")/.." && pwd)"
CORE="$(cd "$HERE/.." && pwd)/sloosh-motion-director"
if [ ! -f "$CORE/scripts/new_film.sh" ]; then
  echo "The sloosh-motion-director skill was not found beside this skill ($CORE)." >&2
  echo "Install the full sloosh-motion plugin, then run this again." >&2; exit 1
fi
FILM=""; FMT="9x16"; FPS="30"; PH=0; N=0
for a in "$@"; do
  case "$a" in
    --placeholders) PH=1 ;;
    -*) usage ;;
    *) N=$((N + 1)); case "$N" in 1) FILM="$a" ;; 2) FMT="$a" ;; 3) FPS="$a" ;; *) usage ;; esac ;;
  esac
done
[ -n "$FILM" ] || usage
case "$FMT" in
  9x16|16x9|1x1|4x5) ;;
  *) echo "format must be 9x16, 16x9, 1x1 or 4x5 (got $FMT)" >&2; exit 2 ;;
esac
case "$FPS" in
  ''|0*|*[!0-9]*) echo "fps must be a whole number from 1, for example 24 or 30 (got $FPS)" >&2; exit 2 ;;
esac
bash "$CORE/scripts/new_film.sh" "$FILM" "$FMT" "$FPS"
EX="$HERE/examples/signal-lost"
cp "$EX/tl.py" "$EX/edit.py" "$EX/audio.py" "$FILM/"
cp "$EX/ui/type.html" "$EX/ui/hud.html" "$FILM/ui/"
cp "$HERE/lib/glitchkit.py" "$FILM/lib/"
# the example is written at 1080x1920: keep the size, fps and name that new_film.sh wrote into tl.json
python3 - "$FILM/tl.py" "$FILM/tl.json" <<'PY'
import json, re, sys
path, tlj = sys.argv[1:3]
with open(tlj, encoding="utf-8") as f: d = json.load(f)
with open(path, encoding="utf-8") as f: src = f.read()
src = re.sub(r"(?m)^W, H, FPS = [^#\n]*", "W, H, FPS = %d, %d, %d" % (int(d["W"]), int(d["H"]), int(d["FPS"])), src, count=1)
src = re.sub(r'(?m)^NAME = "[^"]*"', lambda m: "NAME = %r" % str(d.get("NAME") or "glitch"), src, count=1)
with open(path, "w", encoding="utf-8") as f: f.write(src)
PY
(cd "$FILM" && PYTHONDONTWRITEBYTECODE=1 python3 tl.py)
if [ "$PH" = "1" ]; then PYTHONDONTWRITEBYTECODE=1 python3 "$HERE/scripts/make_placeholders.py" "$FILM" --core "$CORE"; fi
echo "glitch film ready: $FILM ($FMT, $FPS fps). Next: edit tl.py (NAME, COPY, ACCENT, the hit list), then run python3 tl.py again."
