#!/usr/bin/env bash
# use_example.sh: lay one of this skill's example films over a fresh film folder, ready to edit.
#   bash <director>/scripts/new_film.sh <film> <format> [fps]      # first: makes the folder, lib/ and fonts/
#   bash <this-skill>/scripts/use_example.sh <film> [walkthrough|feature] [--placeholders] [--force]
# walkthrough (the default) = examples/ui-walkthrough-30s, the 30 s product film.
# feature = examples/feature-announcement-12s, the 12 s single-feature film.
# Copies tl.py edit.py audio.py, ui/*.html, ui/logo.svg and lib/saaskit.py, keeps the W, H, FPS and NAME that
# new_film.sh wrote into tl.py, then runs tl.py. With --placeholders it
# also makes free stand-in plates and clips, so the pages and contact sheets can be checked before real shots exist.
# It refuses a folder whose edit.py or audio.py differs from the new_film.sh templates (a film in progress),
# unless you pass --force.
# It downloads nothing and installs nothing.
set -euo pipefail

usage() { echo "usage: bash use_example.sh <film-folder> [walkthrough|feature] [--placeholders] [--force]" >&2; exit 2; }

FILM="${1:-}"; [ -n "$FILM" ] || usage
shift
MODE="walkthrough"; PLACEHOLDERS=0; FORCE=0
for a in "$@"; do
  case "$a" in
    walkthrough|feature) MODE="$a" ;;
    --placeholders) PLACEHOLDERS=1 ;;
    --force) FORCE=1 ;;
    *) usage ;;
  esac
done

HERE="$(cd "$(dirname "$0")/.." && pwd)"
CORE="$HERE/../sloosh-motion-director"
if [ ! -d "$CORE" ]; then
  echo "The sloosh-motion-director skill was not found beside this skill ($CORE)." >&2
  echo "Install the whole sloosh-motion plugin, then run this again." >&2
  exit 1
fi
if [ ! -d "$FILM" ]; then
  echo "No film folder at $FILM. Make it first: bash $CORE/scripts/new_film.sh $FILM <format> [fps]" >&2
  exit 1
fi
# never lay an example over a film in progress: the copy replaces tl.py, edit.py, audio.py and the ui pages
if [ "$FORCE" != "1" ]; then
  for f in edit.py audio.py; do
    if [ -e "$FILM/$f" ] && ! cmp -s "$CORE/templates/$f" "$FILM/$f"; then
      echo "$FILM/$f differs from the new_film.sh template, so this folder holds a film in progress. Nothing was changed." >&2
      echo "Use a fresh folder, or pass --force to replace tl.py, edit.py, audio.py and the ui pages." >&2
      exit 1
    fi
  done
fi

if [ "$MODE" = "feature" ]; then
  EX="$HERE/examples/feature-announcement-12s"; SHOTS="desk phone"
else
  EX="$HERE/examples/ui-walkthrough-30s"; SHOTS="desk phone world"
fi

# keep the frame size, fps and name that new_film.sh wrote, so the example takes the film's format
mkdir -p "$FILM/ui" "$FILM/lib"
TLJSON=""
[ -f "$FILM/tl.json" ] && TLJSON="$(cd "$FILM" && pwd)/tl.json"
cp "$EX/tl.py" "$EX/edit.py" "$EX/audio.py" "$FILM/"
if [ -n "$TLJSON" ]; then
  python3 - "$FILM/tl.py" "$TLJSON" <<'PY'
import json, re, sys
path, src_json = sys.argv[1:3]
try:
    with open(src_json, encoding="utf-8") as f:
        d = json.load(f)
    w, h, fps = int(d["W"]), int(d["H"]), int(d["FPS"])
except Exception as e:
    print("tl.py: could not read the film's tl.json (%s); the example's own format is used" % e)
    sys.exit(0)
name = str(d.get("NAME") or "")
with open(path, encoding="utf-8") as f:
    src = f.read()
src = re.sub(r"(?m)^W, H, FPS = [^#\n]*", "W, H, FPS = %d, %d, %d   " % (w, h, fps), src, count=1)
if name:
    src = re.sub(r'(?m)^NAME = "[^"]*"', lambda m: "NAME = %r" % name, src, count=1)
with open(path, "w", encoding="utf-8") as f:
    f.write(src)
print("tl.py: kept the film's format and name (%d x %d @ %d fps, %s)" % (w, h, fps, name or "example name"))
PY
fi
cp "$EX"/ui/* "$FILM/ui/"
cp "$HERE/lib/saaskit.py" "$FILM/lib/"

cd "$FILM"
for f in archivo-latin-wdth-italic.woff2 inter-tight-latin-wght-normal.woff2 instrument-serif-latin-400-italic.woff2; do
  if [ ! -f "fonts/$f" ]; then
    echo "warning: fonts/$f is missing. new_film.sh copies the vendored fonts; run it on this folder first." >&2
  fi
done
if [ ! -f lib/filmkit.py ]; then
  echo "warning: lib/filmkit.py is missing. Make the folder with new_film.sh first." >&2
fi

python3 tl.py
if [ "$PLACEHOLDERS" = "1" ]; then
  # shellcheck disable=SC2086
  python3 "$HERE/scripts/make_placeholders.py" $SHOTS
fi
echo "ready: $FILM ($MODE). Next: edit tl.py COPY and the page CONFIG, render the pages, then python3 edit.py out/sheet.jpg <t1,t2,...>"
