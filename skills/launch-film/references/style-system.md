# Style system

How to turn reference videos + a brand into a consistent visual language.

## Contents
1. Palette roles
2. Typography roles
3. The editorial specimen system (reference style A)
4. The 3D website fly-over (reference style B)
5. Kinetic typography
6. Photo and clip moments
7. Finishing (grain, vignette, flashes)
8. Rhythm

## 1. Palette roles

References come with their own colours (a red/black/white botanical film, a blue/white SaaS
fly-over). Keep their *structure* and swap the colours into brand roles:

| Role | What it does | Sloosh example |
|---|---|---|
| Dominant dark | main canvas, UI background | `#0A0A0A` (site neutral-950) |
| Surface layers | cards, panels | `#141414 / #1C1C1C / #262626 / #303030` |
| Accent | CTAs, highlights, tags, punctuation frames | `#FECC15` (gradient `#FDD943→#FAC01A`) |
| Paper | light editorial frames (specimen sheets) | `#EEECE6` warm off-white |
| Ink on paper | hairlines, labels | `rgba(10,10,10,0.2)` lines, `rgba(10,10,10,0.6)` labels |
| Warning (sparingly) | failures, "wrong" annotations | site destructive red `#DC2626` |

Punctuation frames alternate accent → dark → paper in 3–6 frame bursts. A reference's red
becomes the brand accent; its black stays the dark; its pale grey becomes paper.

## 2. Typography roles

| Role | Use | Sloosh |
|---|---|---|
| Display | headlines, giant kinetic words | Bowlby One (site headline face) |
| Script | handwritten idea notes, arrows | Caveat 700 |
| UI | rebuilt interface, buttons | SF Pro Text → Inter fallback |
| Mono | technical annotations, tags, labels | JetBrains Mono 500/700, uppercase, +0.06em |

Load with `@remotion/google-fonts` (blocks rendering until loaded). Keep annotation text
tiny (12–18 px) but never essential to the story; essential text is display or UI size.

## 3. Editorial specimen system (style A)

Borrowed from experimental "specimen" films: technical construction around a subject.
- **Guides**: hairlines spanning the frame, drawn outward from the subject's centre,
  with solid accent squares (10–14 px) at intersections. Component: `Guides`.
- **Crosshair** on the subject centre (`Crosshair`), optional construction circle.
- **Bounding boxes** with square corner handles and a tag label (`BBox`, `Tag`).
- **Mono labels** in corners: section id, figure name, coordinates (`MonoLabel`).
  Use descriptive or structural text ("SPECIMEN SHEET / 03", "X 673 Y 627"), never
  invented facts or dates.
- **Rulers** along window edges (`Ruler`).
- **Windows**: a photo seen through a rectangular cut in a paper sheet; windows open from
  the subject centre outward.
- **Contact sheets**: a row of square crops with labels above, handles on corners and thin
  connecting arcs below from the source tile to each variant.
- **Detail windows**: rectangles opened over details of a photo, everything else dimmed
  ~55 %, each with a tag and a small "KEEP"/lock chip, plus a readout panel listing them.

## 4. The 3D website fly-over (style B)

The product's site laid in perspective, the camera travelling over it.
- Stage perspective 1500 px; page rotated `rx 30–48°`, `rz −4…−15°`.
- Distance: keep the page *close* (`z` between −100 and +500 at the focus point; scale at
  focus ≈ 1500/(1500−z)). Only one shot per film should show the whole page small.
- Floating objects above the page with `translateZ(h)` and contact shadows on the page;
  billboard them (`rotateZ(-rz) rotateX(-rx*0.85)`) so they face the camera. Use brand
  chips (accent, white, dark glass) with real category names as "choices".
- A cursor (≥ 40 px) projected onto the page with `project()` performs the key action;
  ripple + click SFX on the word.
- Tilt-shift: blur bands top 24–30 %, bottom 10–15 %, 7–9 px.
- Transitions out of a fly-over: push into the clicked element (hand-off), pixel-block
  wipe in the accent colour, or whip pan.

## 5. Kinetic typography

- **Split word around a window**: a giant word split in two halves that slide apart
  around a square image window cycling outputs every 2 frames ("CREA [img] TIVE").
- **Rail word**: a giant word with a node rail under it; a signal fills the rail and each
  letter lights as it passes (shows a workflow running).
- **Punctuation word**: one word filling the frame on accent or paper (e.g. "YOURS."),
  3–6 frames, slight scale-down settle, hit SFX.
- **Cropped giant type**: words wider than the frame, cropped at the edges, sliding with
  tracking; alternate dark/light/accent backgrounds per beat.

## 6. Photo and clip moments

- Full-bleed hero photos are viewed through a **crop camera** (a view rectangle in image
  pixels animated over time) so overlays stay pinned to image features.
- Generated clips play full-bleed with editorial overlays (labels, a crosshair on the
  subject) and are cut on motion (the stroke direction or object position continues).
- Photo prints (white border, slight rotation, drop shadow) make "your photograph" beats
  tangible and let content swap inside the frame.

## 7. Finishing

- Film grain overlay at 6–9 % (overlay blend), cycling plates every 2 frames.
- Vignette 0.3–0.45 on photographic frames.
- White flash only for shutter beats; 2-frame RGB split only on hero match cuts.

## 8. Rhythm

- Average shot 0.6–1.2 s for montage passages, 1.5–2.5 s for hero moments.
- Inside a shot, something should resolve every ~0.3 s (a label types, a box snaps).
- After a dense passage, give one calm beat (a slow push on a photo) so the next cut lands.
