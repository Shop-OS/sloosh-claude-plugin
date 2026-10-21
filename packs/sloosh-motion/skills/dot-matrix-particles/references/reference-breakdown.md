# Dot-matrix, halftone and particle references: craft notes

These notes come from a frame-by-frame study of eight short vertical, square and wide reference films (R1 to R8) and two longer motion presets (S1, a 3D motion scan, and S2, a monochrome glitch montage). The IDs below are only labels. Use the notes as craft guidance, not as material to copy.

## Per reference

### R1 "Copper LED face morph": 8 s, 9:16, 29 fps, zero cuts
- Effect: full-frame LED dot matrix of footage. Fixed square grid, pitch about 4.5 px on a 720-wide frame (about 160 columns x 285 rows). Dot brightness tracks luminance; dot size barely changes (LED, not halftone). Unlit dots stay faintly visible (the panel is always "there").
- Rows sit slightly further apart than columns, so the row gaps read as horizontal scanlines.
- Colour: copper/amber ink (about #E0874A highlights, #7A2E1C mids) on a near-black brown (#140604). Source colour leaks a little (lips go redder): it is "tinted source colour", not one flat ink.
- Content: one continuous face morph from one person into another. The grid never moves; only the image under it changes.
- Pacing: zero cuts, slow, hypnotic. All energy comes from the morph underneath.
- Quality lesson: a dense grid (150+ columns) on low-key footage reads as "a real LED wall, filmed", which feels premium. Never let the grid drift.

### R2 "Flower strobe triptych": 5 s, 9:16, 30 fps, 32 cuts (every 2-6 frames)
- Four states alternate on a strobe: (a) the real photo of a magenta flower (untreated); (b) a black frame with a tiny glowing gold wireframe scribble (about 8% of frame width, centred); (c) an ASCII render of the flower ONLY (background removed): the flower becomes a ring of mixed glyphs in pale lavender #E8C8F0 with a soft pink glow on black, the centre hole is the dark flower core; (d) an inverted LED mask: the background foliage as bright green dots (#22E06A) with sparse red dots (#E0303A) on the edges, while the flower is a pure black silhouette.
- Dot pitch in (d) about 8 px on 720 (about 90 columns); dots are small crosses or squares; ASCII cell about 10 px.
- Pacing: hard cuts on 1/8 notes, 3-5 frames each, never a dissolve. The real photo is the anchor that keeps returning.
- Lesson: the "photo and its data twin" strobe is the hype move. Each state is a different renderer of the SAME source frame. Subject isolation (a mask) is what makes (c) and (d) graphic.

### R3 "Painting -> LED -> light burst": 2.9 s, 16:9, 24 fps
- 0-0.55 s: a painted still of two hands reaching toward each other, untouched, slow push. 0.58 s: posterize/threshold flash (3 levels, black edges). 0.68-0.78 s: a dark grey edge-only version. 0.87 s: the background is gone; only the two hands remain as white/grey LED dots with a blue cast (#6E8CFF in shadows) on navy black (#0B0D16) with a soft vignette. Pitch about 7 px (about 100 columns).
- 0.9-1.95 s: the hands drift toward each other (the dot field moves as a unit; here the grid is attached to the image, not the screen).
- 1.85-2.5 s: at the touch point a light burst grows: a bright white core and 8 rays of dots, ray edges outlined in yellow (#F2E14A) and blue dots; additive bloom.
- 2.6-2.9 s: whiteout: the whole frame becomes a uniform grid of light-grey dots (the "all LEDs on" panel), with a faint blue shape behind.
- Lesson: a complete 3-act micro story in 3 s: real -> dematerialise into dots -> energy -> all-on panel. Use it as a transition or a product reveal.

### R4 "Photocopy runner": 12.9 s, 9:16, 30 fps, 70 cuts
- Black and white, crushed blacks, blown whites, photocopy halftone grain (a fine stochastic screen of 2-3 px, not a clean dot grid), heavy motion blur and ghosting (frame blend). Light leaks and white burn on the edges.
- Content: a runner in profile (0-6.2 s), then a hand pushing toward the lens with fingers spread (6.4-12.9 s). Jump cuts every 3-8 frames (same action, different takes) give a stuttered, chronophotography rhythm.
- Lesson: halftone as a texture on footage (print look), not as a graphic. Suits fashion and sport editorial. Bake it with ffmpeg/numpy rather than redraw it.

### R5 "Gold scan-line portrait split": 9 s, 4:5, 30 fps, zero cuts
- Split screen: the left third is a face rebuilt from HORIZONTAL WAVY LINES of light (row lines displaced by luminance, an oscilloscope look) in gold #FFC24A -> white-hot #FFF1C0, with strong bloom, over a dark radial ember gradient (#3A0A00 -> #000). Stray hair strands become loose glowing particles that float off the top edge.
- The right two thirds are the real footage (short haircut, dusk sky, wind in the hair) with an untreated cinematic grade. Both halves show the same moment: the data twin beside reality.
- Pacing: one slow editorial shot. Premium beauty/fashion feel.
- Lesson: luminance -> vertical displacement on row lines is a distinct, very premium style ("Scan Lines"). The split-screen twin reads instantly as "tech meets beauty".

### R6 "Face photomosaic recursion": 11.8 s, 9:16, 24 fps, a cut every 2 frames
- Archival black-and-white portraits in a grid with thin white gutters (about 2-3 px). Faces partly dissolve: noise/stipple particles eat the face, and some faces blur out to a white blank.
- Grid density grows 2x2 -> 4x4 -> 8x8 -> 16x16 -> about 40 across (the faces become pixels of a texture, 5.5-7.5 s), then reverses back to 2x2 at 11 s. Every cell swaps to a different face every 2 frames (a 12 fps flicker).
- Lesson: the "face as pixel" grid is the dot-matrix idea done with photos. Good for a fashion lookbook or a casting/UGC wall. Needs 12-40 source images.

### R7 "Cyan helmet LED": 10 s, 1:1, 30 fps, zero cuts
- True halftone on a fixed grid: pitch about 7 px (about 100 columns); dot DIAMETER tracks luminance (bright = touching dots, dark = pinpricks), one cyan ink #1FA8E0 -> #6FD8FF highlight on pure black.
- Content: a figure in a space helmet slowly lifts a hand to the visor. Continuous footage under a fixed grid.
- Lesson: the cleanest "LED billboard of footage" look. One ink on black. Slow, emotional pacing.

### R8 "Halftone eye glitch -> wordmark": 9.4 s, 9:16, 24 fps
- Black-and-white 1-bit halftone dither everywhere: grey is made by dot density (an ordered screen of about 4 px). Background: a halftoned collage of icons, coins and shapes in dark grey.
- 0-0.6 s: dotted rings (an iris drawn from scattered dots) with a horizontal smear glitch. 0.6-1.0 s: a vertical slit glitch; a black blob melts and drips. 1.25-5.3 s: a giant white eye; the iris is concentric rings that slice and rotate out of register, then lock clean at 2.2-3.1 s; the eye slides left and exits at 4.4-5.6 s. 5.6-6.0 s: a glitch drip to black.
- 6.26-9.4 s: end card: black with a faint grey dot grid (pitch about 20 px) and a short wordmark in a wide, bold, pixel-edged sans, white, centred low-middle; halftone 3D coins fall through; the wordmark gets 2-frame slice glitches.
- Lesson: a halftone and glitch hybrid. The dot-grid end card with a wide wordmark is reusable.

### S1 "3D motion scan" preset (20.7 s, 16:9)
- An athlete's head as a point cloud or scan-line head (dots on the surface, a scan band), a red particle-dust runner, glowing white silhouettes, a chronophotography strip with a small "MOTION STUDY" label, a huge outlined title, and HUD callout lines with small mono labels.

### S2 "Monochrome glitch montage" preset (13.6 s, 9:16)
- A black-and-white world with one colour accent; a figure dissolving into dots and particles (dust blown sideways), a clone grid, a negative flash, and a data-numeral overlay.

## Cross-reference grammar (what makes it read as premium dot-matrix, not a cheap filter)
1. The dots ARE the shot. The background goes to black (a masked subject or a low-key plate). A dot filter on a busy daylight plate reads as cheap (only R2-d does that, and only for 4 frames).
2. One ink on near-black (amber, cyan, green or white). A second colour appears only as a highlight or edge accent (R3 yellow ray edges, R2 red sparks, R5 white-hot core).
3. A fixed screen grid with the image moving underneath (R1, R7) reads as "a real LED wall". Attach the grid to the subject only when the subject itself travels (R3 hands).
4. Unlit dots stay faintly visible (5-10%) on LED looks. Pure halftone (R7) has no unlit dots.
5. Dots emit light: bloom/glow on LED, ASCII and line styles. Print styles (R4, R8) have no glow; they get grain and crushed contrast instead.
6. Pacing is bimodal: (a) one continuous slow shot (R1, R5, R7) where the motion comes from the footage; (b) a strobe of the real frame and its data twin on 1/8 notes (R2, R6). Mid-tempo slideshows do not appear.
7. Transition vocabulary: real -> posterize -> edges -> dots (R3); dots -> light burst -> all-on panel (R3); dissolve to particles blown sideways (S2); grid recursion (R6); dot drip/glitch to black (R8).
8. Type is rare and late. When present: a wide bold wordmark (pixel-edged) on a faint dot-grid black end card (R8), or tiny mono HUD labels (S1).
9. Grid density: 90-160 columns on a 720-wide frame. Scaled to 1080 wide: 90-140 columns (8-12 px pitch). Below 60 columns it reads as a toy; above 180 it stops reading as dots at phone size.

## Sub-presets derived
| Sub-preset | From | Core look |
|---|---|---|
| LED Billboard | R1, R7, R3 | fixed grid, luminance -> brightness, unlit dots, one ink + bloom, footage under the grid |
| Halftone Editorial | R7, R4, R8 | dot size by luminance, black and white or one ink, print grain, no bloom; fashion/print |
| ASCII Terminal | R2 | glyph ramp, isolated subject, pale ink + glow, strobe with the real photo |
| Point-Cloud Scan | S1, R5 | 3D point cloud with yaw + scan band, HUD mono labels; or row scan-lines (R5) |
| Particle Assemble / Dissolve | R3, S2, R8 end card | dots blow away or assemble into a wordmark or product, light burst, all-on panel |
| Dot Wave Product Reveal | R3 | product revealed through a radial dot wave, ripple shimmer, burst |
| Face Grid (photomosaic) | R6 | recursive grid of portraits, 12 fps cell flicker |
| Twin Split | R5, R2 | real footage beside, or alternating with, its dot twin |
