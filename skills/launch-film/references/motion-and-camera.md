# Motion and camera

## Contents
1. Timing model
2. Easing vocabulary
3. Camera paths
4. 3D distances that read well
5. Motion blur policy
6. Common durations

## 1. Timing model

- Author everything in **scene-relative frames**, derived from seconds:
  `const t = useCurrentFrame() / fps`. Scene boundaries live in `src/timeline.ts`.
- VO phrase times come from `phrases.json` (transcription). Film time = VO time + offset.
  Keep a `VO` object (start/end per phrase plus key words) and a `SCENES` table in frames.
- A cut for a phrase sits 0–2 frames before `phrase.start`. Actions named by a word
  ("click", "drop", "flash") land on that word's start ± 1 frame.
- `interpolate` must be clamped (`prog`, `kf`, `path` in `lib/anim.ts` do this) — motion-blur
  samples evaluate fractional and negative frames.

## 2. Easing vocabulary (`lib/anim.ts → E`)

| Curve | Use |
|---|---|
| `outExpo` | arrivals, snaps, labels, whip-in settle |
| `inExpo` | departures, whip-out, zoom-through |
| `inOutCubic` | default camera glide, draw-ons |
| `inOutQuart/Quint` | designed camera moves, layout morphs |
| `outBack` (subtle) | chips, nodes, badges popping in — never on big moves |
| `inCubic` | push-ins that end on a cut |

Avoid elastic/bouncy curves on anything large; overshoot only on small UI elements.

## 3. Camera paths

`path(t, keys, field)` chains keyframes, each segment with its own easing (`e` on the
destination key). Typical 3D page shot:

```ts
const KEYS: Key<"tx"|"ty"|"z"|"rx"|"rz"|"sx">[] = [
  { t: 0,    tx: 760, ty: 430,  z: 60,  rx: 40, rz: -14, sx: 1900 },            // whip in from right
  { t: 0.24, tx: 760, ty: 470,  z: 110, rx: 40, rz: -13, sx: 0, e: E.outExpo },  // settle on hero
  { t: 0.72, tx: 640, ty: 1560, z: 40,  rx: 40, rz: -10, sx: 0, e: E.inOutCubic },// swoop down page
  { t: 1.0,  tx: 330, ty: 1795, z: 520, rx: 30, rz: -6,  sx: 0, e: E.outCubic },  // close on target
  { t: 1.47, tx: 215, ty: 1812, z: 930, rx: 16, rz: -3,  sx: 0, e: E.inCubic },   // push in → cut
];
```

`tx,ty` = page point at frame centre, `z` = translateZ at the focus point, `rx/rz` = tilt and
roll, `sx/sy` = screen offset (whips). Use `pathSpeed` to drive motion-blur sample counts.

Flat photo moves use a crop camera instead (`lib/cropCamera.ts`): zoom `k` around a screen
point; zoom in **log space** for long pushes (`k = K ** p`).

## 4. 3D distances that read well (perspective 1500)

| Shot | z at focus | perceived scale | notes |
|---|---|---|---|
| Badge/element extreme close-up | 1200–1300 | 5–7× | start of a graphic-match pull-back |
| Push-in to end a shot | 800–1000 | 2.1–3× | hand-off to next scene |
| Working distance (readable UI) | 100–500 | 1.07–1.5× | most of the screen time |
| Overview | −100 … −300 | 0.83–0.94× | one "whole page" beat only |
| Too far (avoid) | < −400 | < 0.79× | page floats small in a void |

Tilt `rx` 30–42° reads as "page on a table"; > 48° gets steep and wastes the top of frame.

## 5. Motion blur policy

- Use the engine's `<MotionBlur samplesAt={...} smearAt={...}>` (sub-frame `Freeze`
  samples blended with plus-lighter). `HtmlInCanvasMotionBlur` may fail in some renderer
  builds.
- Samples: 1 when still; 3–4 for gentle glides; 6–8 for fast camera moves; 10–12 for
  swoops; 16 for whips; 24–28 for zoom-throughs.
- `smearAt` adds an axis-aligned gaussian for whips so steps don't strobe.
- Drive samples from camera speed (`pathSpeed`) to keep render time low.
- Return 1 sample on the first frame after any internal cut.
- Every element with an SVG `id` (mask, filter, clipPath, gradient) needs an id unique per
  sample: create ids with a module counter inside `useMemo`.

## 6. Common durations (30 fps)

| Beat | Frames |
|---|---|
| Punctuation word / colour frame | 3–6 |
| Label typewriter | 6–12 |
| Bbox draw-in | 5–7 |
| Card stagger step | 2–3 |
| Whip in/out | 6–8 |
| Pixel wipe | 8–10 |
| Zoom-through | 7–8 |
| Hold on a readable UI action | ≥ 15 |
