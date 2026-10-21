# Glitch reference breakdown (craft notes from seven reference edits, Ref A to Ref G)

Use this when a user describes one of these looks or shares a similar reference. Each entry gives the effect in technical terms, when it fires, how long, the palette and the lesson. The SKILL.md moves cite these by their Ref letter.
In glitch videos most "cuts" a scene detector finds are the glitch hits themselves, so cut clusters = hit rhythm.

Two families exist and must not be confused:
- **HIT glitch**: 1 to 6 frame bursts locked to beats or cuts, clean footage between (Ref B, C, D; also the "kinetic tech" and "mono montage" notes below).
- **SUSTAINED texture glitch**: one treatment rides a whole shot for 2 to 4 s (wave warp, block smear, pixel-sort drips, tracking HUD), and the CUT between treatments is the event (Ref A, E, F, G).

---

## Per reference

### Ref A (16.4 s, 720x1280 split-screen effect showcase, 29.97 fps)
Two stacked 16:9 panels of graded street footage (teal-green, crushed blacks, lifted mids; skin desaturated). Each panel cycles a sustained treatment for 2.7 to 3.3 s.
- **Sine wave displacement** (0.5 to 2.7 s top): rows shifted horizontally by a sine of y; amplitude about 4% of width (about 30 px at 720), wavelength about 1/6 of frame height, phase drifting about 1 cycle/s. A jacket zipper becomes a zig-zag. The face stays partly intact, so the amplitude is masked or lower near the top. Reads "liquid".
- **Scan-band colour bleed** (0.5 to 3 s bottom): background replaced by horizontal pink-red #E0566E bands 4 to 10 px tall with 2 to 3 px gaps (like a mis-synced CRT), subject untouched. In effect a luma-keyed background replaced by scanline stripes.
- **Vertical white line wipe** (3.8, 7.1, 10.4, 12.0 s): a single 2 px white line sweeps left to right over 4 to 6 frames; to its left the new treatment, to its right the old. This is the transition marker between treatments. Signature move.
- **Tracking HUD on inverted mono** (3.8 to 6.0 s bottom): footage desaturated, darkened and flipped; neon yellow-green #C8FF3C 6x6 px squares in 2x2 clusters, thin white "X" crosshair marks, short white horizontal dashes. Computer-vision look.
- **Horizontal white dash streaks / slice tears** (7.1 to 9.3 s top): white and pale pink rectangles 2 to 4 px tall, 30 to 120 px long scattered along rows, plus the subject region sliced (rows displaced 10 to 40 px).
- **Vertical pixel-sort drips** (7.6 to 9.3 s bottom): bright pixels smeared downward in thin vertical streaks 60 to 300 px long, plus 2 to 3 blue #2030FF block bars at the bottom edge. Classic luminance pixel sort, direction down.
- **Full-frame RGB block noise overlay** (10.9 to 12.6 s top): rows of tiny rainbow pixels (R/G/B/Y/M confetti 2 to 4 px) in horizontal bands every ~20 px, about 40% coverage, footage visible below.
- **Hue/chroma shift** (14.2 to 15.8 s top): whole frame drifts magenta-violet (#7A4AA0 cast) with faint vertical banding = hue rotate 40 to 60 degrees + chroma shift.
- **Vertical repeat smear** (14.2 to 15.8 s bottom): a railing stretched vertically by edge-pixel repeat to the bottom of frame.
Quality: high. Real cinematic plates, one grade; the effects are strong but each one lives alone for ~3 s. Lesson: one treatment at a time, swap the treatment on a hard event (line wipe).

### Ref B (14.2 s, 736x414 landscape, 24 fps) title sting
Black background, dark heavy display title with a permanent red/blue chroma offset (anaglyph shadow: red layer +6 px x, blue -6 px x, about 1% of width). A small white condensed subtitle in a tight box.
- 0 to 1.4 s: the title flickers in as fragments (letters appear in blue/cyan only, partial, opacity stutter); mostly black = tease.
- **Hit inserts**: 1.42 s and 3.79 s, a full-frame neon line-pattern insert (white line mesh, magenta #FF2D7A and cyan #39E6FF triangles) for 2 to 6 frames each, the title sliced over it with horizontal rainbow scanlines.
- 4.74 s: horizontal slice displacement + white dotted lines + red/blue pixel squares (block noise) over the title, 3 frames. 5.22 s: a white/green/blue posterised block-mosh frame with a geometric mark, 2 frames.
- 5.7 to 9.0 s: the title holds stable with its chroma offset; the subtitle pops in under it; a tiny 1 to 2 px jitter keeps it alive.
- 9.49 to 11.4 s: purple #8B2BFF / magenta #C21BD8 flat geometric shapes and line work, one shot per beat, then a fade to black from 11.4 s.
Cut times (hits): 1.625, 1.917, 2.0, 2.667, 3.625, 3.75, 3.833, 3.917, 5.208, 5.292, 9.875, 10.042. Rhythm: single hits, then a 4-hit stutter burst at 3.625 to 3.917 (every 2 frames at 24 fps = 12 Hz strobe), then two 2-frame pairs. Burst = 4 changes in 0.3 s, followed by > 1.3 s calm.
Quality: good title-sting grammar. Lesson: the title is legible 60% of the time; glitch only on hits; a permanent subtle chroma offset gives "glitch identity" without noise.

### Ref C (6.4 s, 736x414 landscape, 30 fps) surreal cyber montage
A fast montage of abstract inserts: an orange sun with an x-ray anatomical silhouette, a chrome pill stretched into horizontal streaks, a bloodshot iris, a blue glitched eye (horizontal RGB scan streaks), a red-orange accretion disc, a white-violet light burst, a falling white silhouette, a ring of green eyes, a white-line technical diagram that INVERTS to black-on-white (4.72 to 5.15 s), scan-slice brain images, a particle swirl, a cyan-white flower.
- **Pixel stretch** (0.21 to 0.43 s): the pill's right half smeared horizontally into streaks (edge-pixel repeat, 70% of frame).
- **Horizontal scan streaks** on the eye (0.86, 1.5 s): RGB lines 1 to 2 px across the iris.
- **White bloom flash** 1.72 to 1.93 s: the frame washes to white over 4 frames, then cuts to black (white-out transition).
- **Invert strobe** 4.73 to 5.4 s: the diagram flips black/white every 2 frames (cuts at 4.733, 4.8, 4.9, 4.967, 5.067, 5.133, 5.233, 5.3, 5.4 = every 2 to 3 frames, 9 hits in 0.67 s).
Cut times: 0.267, 0.3, 0.433, 0.6, 1.967, 4.733 ... 5.4, 5.8, 5.9, 6.067, 6.4. Rhythm: an opening stutter (4 cuts in 0.33 s), a long 2.7 s calm (the falling figure and the eye ring build), then a 0.67 s invert strobe, then 3 quick cuts to the end.
Quality: high craft. Lesson: CALM between bursts is what makes the bursts hit. An invert strobe on line art = the cheapest strongest hit.

### Ref D (29.4 s, 720x1280, 30 fps) hard cyber / datamosh face loop
One low-angle face looking up into a bright light (eyes closed), re-treated endlessly. Treatments, each 2 to 15 frames:
- RGB fringe with a vertical rainbow drip below the chin (pixel sort down, red/green/blue streaks).
- Halftone dot screen on the sky (0 to 0.7 s), posterised B/W.
- **Horizontal slice displacement / tearing**: big bands 40 to 200 px tall shifted 20 to 300 px, with white blown bands.
- **Mirror / kaleidoscope** (5.9 to 7.8 s, 17.6 to 19.6 s): the left half mirrored = a symmetric totem face.
- **VHS / analog static**: full-frame grey snow with horizontal tracking lines (2.9 s, 13.7 s, 24.5 s).
- **Thermal / pseudocolour** posterised rainbow (0.8, 8.8, 9.8, 20.6 s): magenta/green/yellow false colour.
- **Cyan duotone + HUD target ring** (12.7, 23.5 s): a circle reticle, small mono UI blocks top-left.
- **ERROR card**: red #D0182A full frame, an outlined warning triangle, spaced caps "ERROR" (16.6 s).
- **White blowout** (14.7 s, 20.6 s) and B/W solarised (11.8 s).
Cut clusters (hits): 1.1 to 2.83 (9 hits), 4.03 to 4.47 (5), 5.17 to 5.87 (4), 8.5 to 8.93, 9.67 to 10.83 (9), 12.2 to 14.3 (10), 15.13 to 16.97 (9), 19.6 to 21.83 (9), 23.2 to 25.27 (10), 26.1 to 28.0 (8). The 12.2 to 14.3 block repeats exactly at 23.2 to 25.27 (+11.0 s): the edit is loop-built on an 11 s phrase (about 22 beats at 120 BPM, 0.5 s beat). Inside a cluster the gaps are 0.07 to 0.47 s (8th and 16th notes); between clusters 0.6 to 2.6 s of continuous textured motion.
Quality: maximalist, music-visualiser grade; it would cheapen a brand film if used fully. Lesson for "Cyber Hard": clusters of 4 to 10 hits on 16ths, then 1 to 2 s calm; hit families rotate (slice, static, thermal, mirror), never the same one twice in a row; one recurring motif (the face) keeps it coherent.

### Ref E (12.8 s, 720x1280 split, 29.97 fps) flash-photo nostalgia glitch
Top panel: night point-and-shoot footage (direct flash, yellow-green #C8C25A cast, blown highlights). Bottom: an interior with an older person, teal/maroon.
- **Motion-smear ghosting** (0.86, 1.9 to 2.2, 7.3 to 9.5, 10.7 to 12.4 s): heavy frame blend / echo, double-exposed trailing figures, like a 6 to 10 frame tmix + directional blur. Dreamlike, "lost memory".
- **Macroblock datamosh smear** (bottom, 0.4 to 2.6 s, 4.3 to 7.3 s): the image breaks into 8 to 16 px blocks that drag sideways and up (P-frames applied to the wrong reference); colours from the previous shot bleed into the next. The true datamosh look.
- **Vertical pixel-sort drips** from hair and a sofa (9.8 to 12.4 s bottom): bright pixels streak down 100 to 400 px.
- A vertical white line wipe as the transition marker (0.43, 3.85, 7.28, 10.7 s), exactly like Ref A; cadence about 3.4 s per treatment.
Quality: high-end music-video feel. Lesson: datamosh + smear works with photographic, nostalgic content; keep one grade (yellow-green flash).

### Ref F (13.1 s, 720x960, 30 fps) cyan blob-tracking flower
A single continuous shot: a time-lapse lily opening, monochrome cyan duotone (#03080A black, #7FE3F0, #EFFFFF highlights), a fine vertical LED/scanline texture (1 px dark lines every 3 px, vertical), slight posterise.
- **Blob-tracking HUD** throughout: 15 to 60 thin (1 px) white rectangles of varying sizes (8 to 200 px) locked to bright features, each with a tiny 6 to 8 px number label; boxes appear and disappear frame to frame; density follows detail. A current generative-art "blob track" look.
No cuts. Quality: very clean, premium tech-nature. Lesson: glitch can be quiet: a data overlay + mono tint + scan texture reads "tech" without any destruction. The SaaS-safe and product-safe variant.

### Ref G (16.0 s, 720x1280, 25 fps) holographic butterfly + coordinate HUD
A neon iridescent butterfly on near-black #07060C with sparse star noise. The colour state FLIPS between magenta/pink (#FF3FC8, #FF8AD8) and cyan/blue (#40F0FF, #3A4BFF) about every 0.5 to 0.55 s (about 1 beat at 110 to 115 BPM); the shape also jumps pose (stop-motion feel, 2 to 3 frame holds).
- Tracking labels "x: 395 y: 510" in 8 px white mono, thin red #FF3A3A rectangles and dashed white ellipses around the wing on the cyan states only; the magenta states are clean.
- Bloom on highlights, slight RGB fringe.
No detected cuts (the state flips are colour, not scene). Quality: high, very youth-tech. Lesson: a palette swap on the beat + coordinate labels is a complete glitch language with zero destruction; it works for products (a bottle, a sneaker) shot on black.

### Preset-pack notes (generic looks seen in editing-app glitch presets)
- **Mono glitch montage** (13.6 s 9:16): a B/W world + ONE colour accent (a green jacket = the product), dot dissolve, invert, film-strip repeat, a 4x4 clone grid, giant data numerals. = our "Mono Fashion".
- **Noir glitch edit** (17.7 s 16:9): B/W fashion, very sparse glitch: a picture-in-picture detail inset, a motion-blur walk-past; glitch only on 2 to 3 cuts. = the layer-mode rules.
- **Kinetic tech edit** (13.6 s 16:10): a red posterised cut-out head, rounded video frames, horizontal slice glitch on the face, a pixel-mosaic gold transition, a white flash, a tiny italic lower-case caption. = "Clean Tech Glitch" for launches.
- Other common preset looks: cinematic glitch action, VHS memory, Y2K edit, photocopy texture, 1-bit monochrome illustration.

---

## Common grammar (what all good glitch edits share)
1. **Clean > broken ratio.** Hit family: footage is clean 70 to 90% of the runtime; each hit 1 to 6 frames. Sustained family: one treatment per shot, swapped at a hard event. Never stack two destructive treatments on the same frames for more than 2 frames.
2. **Bursts, not sprinkles.** Hits come as a single hit (2 to 4 frames) or a stutter burst (3 to 5 changes every 2 frames = 12 to 15 Hz), followed by >= 1 s calm. Ref B: 4 changes in 0.3 s, then 1.3 s calm. Ref C: 9 in 0.67 s, then a cut. Ref D: 4 to 10 per cluster, clusters every 1 to 3 s.
3. **Locked to music.** Hits on beats, 8ths and 16ths; bursts on fills and phrase ends; the biggest burst on the drop. Loop-built edits repeat the cluster pattern every phrase (Ref D, 11 s).
4. **Restricted palette.** One grade per film (teal-green, yellow-green flash, cyan mono, B/W) + at most 2 neon accents (magenta/cyan, red/blue). RGB rainbow only inside 1 to 2 frame hits.
5. **Transition markers.** A 2 px white vertical line wipe (Ref A, E), a white bloom-out (C), a static frame (D), an invert strobe (C).
6. **Data/HUD layer** = the modern quiet glitch: tracking boxes, coordinate labels, crosshairs, mono 8 to 12 px numerals (Ref A, D, F, G; the mono-montage numerals).
7. **Text treatment.** The title is legible >= 60% of its screen time; a permanent small chroma offset (red/blue +-1% of width) as identity; slice + RGB burst only on the entrance and on 1 to 2 beats.
8. **Physical artefact vocabulary** (each has an exact technical meaning):
   - RGB split / CA: R and B channels offset +-0.5 to 2% of width (5 to 20 px at 1080), G fixed. Radial CA for a lens feel.
   - Slice displacement: 6 to 16 horizontal bands, 30 to 45% of bands move, offset 2 to 15% of width, 2 to 4 frames.
   - Block noise / macroblock: 16 to 64 px blocks copied from offset positions + channel swap, 10 to 25% of the frame area.
   - Scanlines: a 1 px dark line every 3 to 4 px at 15 to 35% opacity (CRT); the vertical variant = LED.
   - Pixel sort: luminance-thresholded streaks along one axis, 60 to 400 px.
   - Datamosh: the motion vectors of clip B applied to the last frame of clip A (bloom/smear), 8 to 20 frames.
   - VHS: half-res chroma, chroma shift 4 to 8 px, a tracking band, noise, soft.
   - Posterise / thermal: 3 to 4 levels per channel, or pseudocolour (turbo) for "heat".
   - Invert / threshold strobe: alternate every 2 frames.
   - Static: full-frame luma noise with horizontal roll lines.

## Named sub-presets derived
| Sub-preset | Source refs | Family | Palette | Density per 15 s |
|---|---|---|---|---|
| Clean Tech Glitch | kinetic tech notes, Ref F, Ref G | hit + HUD | #0A0A0A / #F5F5F0 + 1 brand accent | 3 to 5 hits, <= 4 frames |
| VHS Nostalgia | VHS memory notes, Ref E | sustained | warm faded, chroma bleed | 2 to 3 tracking events + constant texture |
| Cyber / Datamosh Hard | Ref D, Ref B, Ref C | clusters | black + magenta #FF2D7A + cyan #39E6FF | 4 to 6 clusters of 3 to 8 hits |
| Monochrome Glitch Fashion | mono montage and noir notes | hit | B/W + one product hue | 4 to 6 hits |
| Glitch Transitions Layer | Ref A, Ref E (line wipe), the director's transitions section | transitions only | host palette | one per scene change, 3 to 5 |
| Glitch Logo Sting | Ref B | hit + hold | black + 2 neon | 4 to 6 s total, 2 bursts |
| Data Bloom (HUD) | Ref F, Ref G | sustained overlay | mono tint + white labels | constant, no destruction |
