# Product Reveal: the prompt for each still and each clip

One prompt makes one shot. This style never uses one prompt for the whole film. A film made from one prompt drifts in shape, puts text on screen and looks flat. A typical failure: an open C-shaped clip turned into a stem earbud.

Every generated shot is made in two steps:
1. **Still** (an image model chosen with list_models, mode image_gen). Use the highest resolution offered and the film's aspect ratio. Reference images, in this order: image 1 is the real front photo, image 2 is the real angle photo that shows the tricky part, image 3 is the last approved still (for continuity). Never use a generated image as image 1.
2. **Clip** (a video model chosen with list_models, mode video_gen). The start frame is the approved still. Use the film's aspect ratio (the nearest one the model offers; for a 4:5 film, 3:4), the highest resolution offered, about 5 s, and no generated audio. One action and one camera move per clip.

Set these values in the terms the chosen model's entry uses. Get a quote for every item and the user's approval of the round before you generate (the SKILL.md section on generation).

Fill every {{SLOT}}. Before you quote, check the prompt: no "{{" may be left. Never write a brand, a product line, a person's name or a film title. The product is "the product in image 1". A look is described physically.

Prompt craft that holds for any model:
- Describe what IS there, in positive sentences. Name the parts and their shape. Do not list what to avoid.
- Keep the same light line, world line and camera line, word for word, in every still of the film.
- Change one thing per edit: "keep exactly the same set, light and product; change only X".
- For clips, give the time windows (calm start, one action, settle) and one camera move. Physics words (weight, motion blur) help. Several actions in one clip make it morph.
- Name a defect concretely when you prompt again ("the clip arm is a closed loop; it must be an open C"). Stronger adjectives do not help.

---

## 0. Shared blocks (paste into every still)

### 0.1 Identity and shape truth (first, filled)
```
Image 1 is the exact real product. Keep its silhouette, proportions (height to width {{RATIO}}), materials, colours
({{MAIN_COLOUR}} body, {{SECOND_COLOUR}} {{PART}}) and its printed label and logo exactly as photographed. Image 2 shows
the same product from {{ANGLE}}, so the {{TRICKY_PART}} is clear. The product has exactly these parts: {{PARTS_LIST}}.
{{SHAPE_SENTENCE}}. Small print stays as fine print in its exact place. The product is one rigid object.
```
- PARTS_LIST: every visible part, in order, from the photos. A perfume: "a rectangular glass body, a short metal neck, a ribbed cylindrical cap". Clip earbuds: "an open C-shaped clip arm, a round driver pod at one end, a small battery capsule at the other end, a curved bridge joining them".
- SHAPE_SENTENCE: the hard part, described positively. "The earpiece is an open C-shaped clip that wraps behind the ear; the round pod and the capsule are joined by a thin curved bridge, and the only parts are those three." Say what is there, attach the angle photo that shows it, then reject a wrong shape on sight.
- RATIO comes from the photo's bounding box. The colours come from palette_from_photo.py.

### 0.2 Realism and finish (last, word for word)
```
True-to-life materials with fine dust, faint handling marks and real micro-texture; crisp specular roll-off;
natural sensor noise, slightly underexposed. Looks like a frame grab from a real commercial shoot. Clean raw footage:
every surface is free of added writing, captions or graphics.
```

### 0.3 World and light lines, per sub-preset
| Sub-preset | World | Light |
|---|---|---|
| Dark Luxury Light-Sweep | a pure black void, a black lacquer floor holding a short soft reflection | one narrow strip softbox key from camera-left at 45 degrees, a cool rim from behind right, the shadow side falling to black, 8:1 contrast |
| Clean Studio | a seamless cyclorama, warm white at the top fading to light grey at the floor | a large soft key from top-left, a white bounce on the right, a soft contact shadow |
| Splash / Levitation | an infinite space in {{HUE_MID}} with a glossy floor of the same hue and a round pedestal with a thin glowing edge | a large soft top key, two thin vertical light lines far behind, a light haze |
| Exploded View | a pure black void with no floor | two cold rims left and right, one hard top key |
| Tech Launch | a dark graphite stage with a faint grid of light reflected in a glossy floor | a hard cool key from camera-right, a coloured edge light in {{ACCENT}} from behind left |
| Lifestyle | {{ROOM}} at golden hour, an oak table, linen | a soft window key from camera-left, a warm bounce, a practical lamp in the background bokeh |

### 0.4 Camera lines
- Hero: "medium-format camera, 85 mm, f/5.6, eye level with the product's centre".
- Macro: "medium-format camera, 100 mm macro, f/4, the focus plane on {{DETAIL}}".
- Lifestyle: "full-frame cinema camera, 50 mm, f/2.8, handheld height".

---

## 1. The stills (in chain order)

Block order: 0.1, then the shot body below, then 0.3, 0.4 and 0.2. Make S1 first, look at it at full size and get the user's approval. Every other still is an edit of S1 (or of the last approved still) with the real photos still attached: "keep exactly the same set, light and product; change only {{X}}".

| # | File | Shot body |
|---|---|---|
| S1 | plates/hero.jpg | The product stands upright on the floor, centred, turned 15 degrees toward camera-left, its base at {{BASE}} of the frame height and its height {{HEIGHT}} of the frame, generous dark space above it. |
| S7 | plates/set_empty.jpg | Edit of S1: the identical set, floor, reflection line and light with the floor empty. The product and its reflection are gone; the light pool stays where it was. |
| S2 | plates/hook.jpg | Edit of S1: the key light is switched off; only a thin cool rim traces the product's outer edge. The camera moves in so {{EDGE}} fills the upper half; the rest is near-black. |
| S3 | plates/anchor.jpg | Edit of S1: an extreme close-up of {{IDENTITY_ANCHOR}}, which fills the upper two thirds; the lower third falls off to dark (space for the counter). |
| S4 | plates/label.jpg | Edit of S1: an extreme close-up of the material around the print area, tilted 6 degrees, very shallow focus. The {{MATERIAL}} surface and its edge are sharp, and the printed text falls into soft focus behind the focus plane. |
| S5 | plates/material.jpg | Edit of S1: an extreme close-up of {{MATERIAL_DETAIL}} (the glass shoulder with the liquid behind it, the knit, the brushed edge), very shallow focus, a single specular streak across it. |
| S6 | plates/action.jpg | Edit of S1: the start state of the action, framed for it: {{ACTION_START}} (the cap seated, the product before the lid opens, the bottle before the pour). |

S1 sizes by format (they match the tl.PACK defaults in examples/dark_luxury/tl.py): on 9:16, BASE is 69% and HEIGHT is half. On 16:9 and 1:1, BASE is 83% and HEIGHT is 63%. On 4:5, BASE is 83% and HEIGHT is 59%.

Sub-preset extras (S8):
| Sub-preset | Extra still |
|---|---|
| Splash / Levitation | plates/float.jpg: an edit of S1, the product hovering 3 cm above the pedestal, tilted 12 degrees, its reflection following. |
| Exploded View | plates/exploded.jpg: an edit of S1 on black, the product separated along one vertical axis into exactly these parts, evenly spaced, each keeping its orientation: {{VERIFIED_PARTS}}. Use only parts the user or the maker's own teardown confirms. |
| Lifestyle | plates/hands.jpg: an edit of S1 moved to the room. Two hands with natural nails hold the product at chest height in window light; the face stays out of frame. |
| Clean Studio / Tech Launch | plates/row.jpg: five identical products staggered in depth on a diagonal, the front one sharp, the rest falling out of focus. |

**Reject on sight** (look at each still at full size next to the real photo):
- any part added, missing or reshaped (a stem where there is a clip, a round cap where it is square)
- a letter changed, moved or re-spelled; a logo redrawn
- colour drift on the product; a light direction different from S1
- a plastic, rubbery or over-smooth surface; extra objects; words anywhere in the frame

A rejected still is a retake. It goes into the next round with a new version in its key, a new quote and a new approval.

---

## 2. The clips (the start frame is the approved still)

Template for every clip:
```
Realistic locked-off commercial footage. The first frame is image 1: same product, same set, same light, same
composition. 0-1.5 s: {{CALM_START}}. 1.5-3.5 s: {{THE_ONE_ACTION}}. 3.5-5 s: {{SETTLE}}.
Camera: {{ONE_MOVE}}. Real weight and physics, natural motion blur on fast moves.
The product stays one rigid object; every part, label and logo stays exactly as in image 1.
One continuous shot with no cuts, text, extra people or new objects.
```

| Shot | From still | Calm start, the one action, settle | One move | Clean window to try first |
|---|---|---|---|---|
| Hook (rim crawl) | S2 | darkness with only the rim; the strip key travels left to right across the edge, revealing the surface; the band leaves the frame right | very slow push-in | 0.4-2.6 s |
| Anchor macro | S3 | the highlight rests at the left; one narrow specular band glides across the {{ANCHOR}}; it fades at the right edge | slow lateral slide right, 100 mm macro | 0.5-2.2 s |
| Print-area macro | S4 | still; the focus breathes along the material, the print staying soft behind it; hold | slow arc of about 10 degrees | 0.8-2.4 s |
| Material macro | S5 | still; the light shifts and the material catches a moving streak (glass refracts, the liquid inside sways gently); hold | slow push-in | 0.6-2.4 s |
| Hero | S1 | the product rests; one soft light band sweeps the product top to bottom; it settles, frontal | slow push-in, eye level | 0.6-2.0 s |
| Action: lid or cap opens | S6 | the cap is seated; the cap lifts straight up 4 cm and hangs, rotating 10 degrees; hold | locked camera | 1.0-3.0 s (play the lift at 0.5x in the edit) |
| Action: part separates | S6 | the product is whole; {{PART}} slides out along one axis by {{DISTANCE}} and stops; hold | slow orbit 15 degrees | 1.2-3.2 s |
| Action: liquid or mist | S6 | still; a fine mist cloud bursts from the atomiser, or a single crown of {{LIQUID}} rises at the base; it drifts and falls | locked camera | 1.4-3.0 s |
| Action: device lights up | S6 | the screen or LED is off; the {{LED_OR_SCREEN}} lights in its real colour; hold | slow push-in | 1.2-2.8 s |
| Levitation (Splash) | S8 float | resting on the pedestal; the product rises gently and turns 20 degrees; it hovers, breathing | slow half-orbit | 1.0-3.5 s |
| Separation (Exploded) | S8 exploded | whole; the listed parts separate along one axis in slow motion, every part keeping its orientation; they hold apart | slow orbit 20 degrees | 1.2-3.4 s |
| Hands (Lifestyle) | S8 hands | the hands are still; the hands turn the product toward the window light; hold | handheld, gentle | 0.5-2.5 s |
| Row (Clean, Tech) | S8 row | still; the focus pulls from the rear product to the front one; hold | slow lateral slide | 0.6-2.6 s |

The readable label is never a clip. It is the code shot from label_macro.py (the real cutout at 2 to 3x). For glass, add "the liquid level stays the same". For a shot with hands, add "hands anatomically correct, five fingers, natural grip".

**After each clip:** run python3 lib/sheets.py clip clips/<x>.mp4 (3 fps) in the film folder, then read the sheet:
- The shape and the parts match the stills in every frame you use. The label holds still.
- Pick the clean window (usually inside the first 60 to 70%). Write it into the cut list as the in-point.
- The action's key frame (the cap leaving, the mist burst) becomes a sync point in tl.py.

A clip that morphs the product is not trimmed around. Make it again in the next round (a new version in its key, a new quote and a new approval), or replace it with the still and code motion. If the service refused a clip, try the next round with the start still framed slightly wider. Only a transport failure of the same call reuses the same key (see the SKILL.md spending rules).

---

## 3. Counts and credit-light

| Variant | Stills | Clips |
|---|---|---|
| Default 15 s | 7 (S1 to S7) | 6 (hook, anchor, print-area macro, material, hero, one action); the readable label macro is code |
| Long 20 s | 8 (add S8) | 7 or 8 (a second action, or the S8 move) |
| Credit-light | 4 (S1, S3, S5, S7) | 2 (hero and one action). S3 and S5 play as stills with handheld and code sweeps; the hook is make_rim.py on S1 |
| Zero-video | 1 (S7) or 0 (a code stage) | 0. The real cutout carries the whole film in ui/packshot.html |

Rounds never mix images and videos, and each round has at most 8 items.
