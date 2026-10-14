#!/usr/bin/env bash
# Scaffold a Remotion project with the launch-film engine.
# usage: bash new_project.sh <project_dir>
set -euo pipefail
DIR="$1"
HERE="$(cd "$(dirname "$0")" && pwd)"
TPL="$HERE/../assets/template"
if [ -e "$DIR" ] && [ -n "$(ls -A "$DIR" 2>/dev/null)" ]; then
  echo "refusing to scaffold into non-empty $DIR" >&2; exit 1
fi
PARENT="$(dirname "$DIR")"; NAME="$(basename "$DIR")"
mkdir -p "$PARENT"
( cd "$PARENT" && npx --yes create-video@latest --yes --blank --no-tailwind "$NAME" >/dev/null )
( cd "$DIR" && npm i >/dev/null 2>&1 && npx remotion add @remotion/media @remotion/google-fonts @remotion/transitions @remotion/motion-blur @remotion/effects >/dev/null 2>&1 )
rm -f "$DIR/src/Composition.tsx"
cp -R "$TPL/src/." "$DIR/src/"
cp "$TPL/remotion.config.ts" "$DIR/remotion.config.ts"
mkdir -p "$DIR/src/scenes" "$DIR/public/fx" "$DIR/public/sfx" "$DIR/public/vo" "$DIR/public/pack" "$DIR/public/hd" "$DIR/public/mock" "$DIR/public/clips" "$DIR/public/brand"
# The grain plates are generated, not shipped, to keep the plugin package small.
if ! python3 "$HERE/grain.py" "$DIR/public/fx" >/dev/null; then
  echo "grain plates not generated: install numpy and Pillow, then run: python3 $HERE/grain.py $DIR/public/fx" >&2; exit 1
fi
( cd "$DIR" && npx tsc --noEmit -p . && echo "typecheck ok" )
echo "scaffolded $DIR"
