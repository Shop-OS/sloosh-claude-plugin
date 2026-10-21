# Photoreal morph recipes: keyframe chain, start+end transition clips, edit.py

Read this with SKILL.md, section "Route C: the keyframe chain". The spending rules in SKILL.md apply to every
generation here: quote first, one approval per round of at most 8 generations, a stable idempotency key per item.

Pick models by capability with `list_models`, every time. Model names and limits change.

| Job | Capability to look for | Settings |
|---|---|---|
| Hero keyframe and every variant | image edit with reference images and a 4K output | aspect = film aspect; refs = the previous approved still + identity photos (JPG under 2 MB) |
| Transition A to B (faces included) | video with a start frame AND an end frame | start = still A, end = still B, aspect = film format, 1080p, 5 s, no audio |
| Hero hold with life (blink, breath, fabric) | video with a start frame | start = the hero, aspect = film format, 1080p, 5 s, no audio, one micro-action |

If no listed video model takes an end frame, use start-only clips and land each one on the next still with a 0.25 s
match cut (see "Refusals" below).

## 1. The keyframe chain: the morph is decided here

Make the hero first and get it approved. Every later key is an **edit of the previous approved key**, so pose,
camera, lens and light are inherited. Never generate a variant from scratch.

**1.1 Hero (k0).** Write the prompt in positive terms, block by block:
```
Identity: Image 1 is the exact real {{person / product}}: {{identity lock}}.
Shot: {{subject}} faces the camera square-on, centred on the vertical centre line, eyes at 26% of the frame height,
shoulders at 38%, the chest and torso filling the middle of the frame; {{pose}}. Camera height at the eyes, perfectly level.
World and light: a seamless {{backdrop colour}} studio sweep; one large soft key 45 degrees camera-left, a white bounce
right at 3:1, a narrow cool rim from behind right; the backdrop falls off gently toward the floor.
Camera: cinema camera, 85 mm, f/2.8, ISO 800, locked tripod.
Realism: natural unretouched skin with visible pores and slight oil shine, flyaway hairs, real fabric weave and creases,
fine sensor noise, slightly underexposed shadows.
Finish: a frame grab from a real fashion campaign shoot; clean raw footage, every surface free of added writing or graphics.
```
For a product: "the product stands centred, its vertical axis on the frame's centre line, filling 62% of the frame
height (top edge at 19%, bottom edge at 81%)", medium format 100 mm, true-to-life materials with fine handling marks.

**1.2 Variant key (k1 to kN).** Refs = the previous approved key (image 1) + the identity photo (+ a garment photo):
```
Image 1 is the composition master: recreate it exactly, with identical camera position, angle, crop, lens, subject
position and scale, pose, eye line, and identical lighting and backdrop. Change only {{THE ONE CHANGE}}.
{{part-by-part truth, e.g. "the jacket in image 3: oxblood leather, notch lapels, two flap pockets, silver zip"}}.
The face is the person in image 2: the exact face, hairline, skin tone and texture, build and age.
```
THE ONE CHANGE, safest first:
1. **Colourway or material**: "the jacket becomes deep navy wool knit with a visible rib". Same garment, new surface.
2. **Outfit**: same model, pose and light; the garment from image 3.
3. **Look or creature skin**: "the skin and clothes become a fine glowing wireframe mesh of thin cyan lines over a black
   body, the face's exact shape preserved in the mesh"; "the skin becomes small dark-green reptile scales with a soft
   sheen, eyes unchanged"; "an x-ray radiograph of the same pose: pale blue translucent body, bones visible, dark
   blue background"; "the head becomes a polished ghost-white skull with the same proportions, same jacket".
4. **Scene behind a locked subject**: "the backdrop becomes a night street with soft neon bokeh; the subject and the key
   light stay exactly the same".
5. **Different silhouette** (bottle to sneaker): add an intermediate key that shares A's silhouette and B's material.

**1.3 Pair check before any video round.** Look at both keys at the same size with `view_asset`:

| Check | Pass |
|---|---|
| Eye line or product top | same y, within 2% of H |
| Centre line | same x, within 2% of W |
| Scale (shoulder width or product height) | within 5% (the figure lock fixes the rest) |
| Key-light side, shadow direction, lens feel | identical |
| Face identity | the same person at full size; no new jaw, nose or hairline |
| Printed text and labels | identical to the real product, or the key is redone |

## 2. Transition clip (start AND end frame), one per hop
```
Realistic {{fashion campaign / product commercial}} footage. The first frame is image 1 and the last frame is image 2:
same {{person / product}}, same studio, same light, locked-off camera.
0-1.2 s: hold on image 1, only a breath and a blink.
1.2-2.8 s: {{MECHANISM}}, one continuous physical transformation across the whole {{subject}}.
2.8-5 s: hold on image 2, a slow breath.
Camera: locked-off on a tripod, perfectly still (the push is added in the edit).
The change happens on the subject itself, in steady light. {{Person: The face stays the same person throughout; natural blinking; hands anatomically correct.}}
{{Product: The product stays one rigid object; every part, label and logo stays exactly as in image 1 or image 2.}}
One continuous shot with no cuts, text, extra people or new objects.
```
Mechanisms (the verb matters as much as the subjects):

| From and to | Mechanism |
|---|---|
| Colourway | "the colour flows through the fabric from the collar down like dye soaking into the weave" |
| Outfit to outfit | "the fabric ripples and re-weaves itself, seams sliding into the new cut and colour" |
| Skin to wireframe | "glowing lines draw themselves across the skin and clothes from the forehead down until the body is mesh" |
| Skin to scales | "small scales rise through the skin from the neck outward, catching the key light" |
| Look to x-ray | "a cool light passes down the body and turns it translucent, revealing the bones" |
| Bottle to bottle | "the glass softens like molten glass and flows into the new silhouette, the cap stretching upward" |
| Scene behind | "the backdrop melts away like paint and the new location paints itself in behind the still subject" |

**Refusals.** Some video models refuse a face job. A refusal is not a retry case. Plan a changed job instead: start
frame only, JPG under 2 MB, framed slightly wider, the mechanism unchanged. It is a new item, so it needs a new
quote, a new approval and a new idempotency key. Tell the user and wait for the user before you run it. In the edit,
a start-only clip lands on still B with a 0.25 s match cut.

## 3. After every clip
1. `python3 lib/sheets.py clip clips/tN.mp4` (3 fps). Find where the transformation starts and lands.
2. Clean window: in_point about 0.9 s, 1.0-1.5 s of film time at speed 1.3-1.6 (or the `ramp` tag), so the whole
   morph plays and the warped tail never does. No clip runs more than 2.5 s without a cut.
3. Write the landing time into `tl.MORPHS` (the shimmer peaks there) and the next FORM word cue.
4. Drift? `python3 lib/morphfx.py lock clips/tN.mp4 --ref plates/k0.jpg` writes `clips/locked/tN.mp4`. edit.py uses
   the locked clip when it exists.

## 4. Failure and fix

| Symptom | Fix |
|---|---|
| Hard pop mid-clip | The keys failed the pair check: redo B as an edit of A with the numbers spelled out; add an intermediate key |
| Looks like a cross-dissolve | Name a physical mechanism (section 2) and "one continuous physical transformation" |
| Morph starts at 0 s or never holds | Put the hold and morph seconds in the prompt; trim with the clean window |
| Face or identity drifts | Shorter morph window (1.2-2.4 s), "the face stays the same person", start and end both pass the identity check |
| Camera drifts or zooms | "locked-off on a tripod"; the push comes from the cut list zoom |
| Background or grade shifts | Same backdrop words in every key; one `teal` or `warm` tag, or no tag, on all transition rows |
| Text or logo appears | Remove any brand words from the prompt; describe the look physically; generate it again as a new item |
| Seam pops at a cut | Cut inside the holds (identical frames), or cover it with a `negative` or `smear` hit, or a sliced shatter |

Every "generate it again" is a new item: a new quote, a new approval and a new key with a higher version.

## 5. Generation counts (quote before spending)

| Film | Stills (4K) | Clips (5 s, start+end frame) |
|---|---|---|
| Morph Chain 15 s (default) | 8 keys (plan 2 redos) | 3 transitions |
| Light chain | 8 keys | 1 transition (the hero one); the rest are code (flow morph, shatter, match cuts) |
| Face Morph Run 6 s | 5 keys | 1-2 transitions |
| Photoreal Product Morph 8 s | 2 keys | 1 transition |
| Code films (UI, logo, liquid, shards) | 0 | 0 |
