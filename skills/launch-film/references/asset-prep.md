# Asset preparation

## Contents
1. Folder layout in the project
2. HD upscales
3. Measuring objects and features
4. Solving aligned placements
5. Mirroring
6. Clean plates
7. Mocks
8. Graded direction variants
9. Video clips
10. Grain
11. Honesty notes for the README

## 1. Folder layout (`public/`)
```
public/
  vo/        voiceover files
  pack/      original images as delivered
  hd/        2× Lanczos upscales (+ clean plates)
  mock/      placeholders (replaceable by filename)
  clips/     transcoded H.264 video clips
  sfx/       prepared SFX + peaks.json
  brand/     logo SVG
  fx/        grain plates
```
Register every image in `src/assets.ts` with its **logical** size (the original pixel size);
the `hd/` file is 2× and the browser downsamples it. Crops and measurements are always in
logical pixels.

## 2. HD upscales
`bash scripts/upscale_hd.sh public/pack public/hd NAME1 NAME2 …` → 2× Lanczos + light unsharp,
JPEG q2. Use for any image shown larger than ~1.1× its logical size.

## 3. Measuring
`python3 scripts/gridify.py <img> <out.jpg>` draws a labelled 50/100 px grid. Read boxes
off the gridded proof: object body box `x, y, w, h` and centre. Measure the stable part of
the object (the body, the seat, the iris) — not parts that change between source and result.

## 4. Solving aligned placements
`python3 scripts/align_pair.py --a W,H,cx,cy,w --b W,H,cx,cy,w [--screen 1920x1080]
[--target X,Y] [--minscale 1.148]` prints scale and offset for image A and B so the measured
objects coincide on screen and both images still cover the frame. Use the output in a crop
camera (`lib/cropCamera.ts → makePair`) or as `<Placed scale x y>`.

## 5. Mirroring
If the source faces the other way (handle left vs right, chair facing), render it with
`flip` and give crops in mirrored coordinates (x' = W − x − w). Mention it in the README.

## 6. Clean plates
`python3 scripts/cleanplate.py in.jpg out.jpg --box x0,y0,x1,y1 [--from above|below]`
paints out baked-in text by feathering in the wall band directly above/below. Use when a
crop of a poster would show the original headline next to your re-typeset copy.

## 7. Mocks
`python3 scripts/mocks.py public/mock spec.json` renders studio-style placeholders (gradient
sweep, soft object, contact shadow, grain) with a small "MOCK" tag and name. Use
meaningful filenames (`mock_fashion.jpg`) so the user can replace them 1:1. Keep aspect
ratios standard (4:3 thumbnails, 16:9 frames).

## 8. Graded direction variants
`bash scripts/grade_variants.sh in.jpg public/mock prefix` → warm / cool / golden / mono / dusk
variants for "explore the possibilities" beats. Name them `mock_*` — they are illustrative.

## 9. Video clips
`bash scripts/prep_video.sh in.mp4 public/clips/out.mp4` → H.264 yuv420p, CRF 12, 1920×1080
cover crop, original fps. Use `<Video>` from `@remotion/media` with `trimBefore`,
`playbackRate`, `muted`. Measure feature points on the exact frame you will cut on:
`ffmpeg -ss T -i clip.mp4 -frames:v 1 frame.png` then `gridify.py`.

## 10. Grain
`python3 scripts/grain.py public/fx` → 8 plates of 960×540 mid-grey noise; `<Grain>` scales
and cycles them.

## 11. README honesty notes
List: every mock file, mirrored images, clean plates, illustrative generated outputs, and
any placeholder UI values (credits, user names).
