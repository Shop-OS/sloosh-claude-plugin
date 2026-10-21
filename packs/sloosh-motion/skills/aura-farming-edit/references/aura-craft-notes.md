# Aura edit craft notes

Neutral craft numbers for beat-synced hype edits. All frame counts are at 30 fps unless a line says otherwise. These are working defaults, not rules from any one edit. Read this file when a brief needs a number that SKILL.md does not give.

## 1. Emotional grammar

- The subject is calm. The world around the subject moves fast.
- The subject does not perform. No smiles at the camera, no pointing, no hard sell.
- One small gesture lands exactly on the drop.
- Faces stay unreadable. Sets stay dramatic.
- The film ends when the subject looks into the lens and holds. The last frame can match the first, so the film loops.

## 2. Speed ramps

Two curve shapes:

- **Hit first (the default).** Fast through the approach, slowest exactly on the beat, then fast out.
- **Hit late.** Slow at the start of the shot, then a fast whip into the next cut. Use it in the build.

Defaults for the hit-first curve:

| Moment | Speed | Length |
|---|---|---|
| Approach | 150 to 250% | until 4 to 6 frames before the beat |
| Ease into the hit | ease in | 4 to 6 frames |
| Hit, on the beat | 15 to 25% | 8 to 16 frames (half a beat to one beat at 120 to 140 BPM) |
| Release | ease out | 6 to 10 frames |
| Exit | 120 to 200% | the rest of the beat |
| One long hold per film | 20%, drifting to 10% | 1.5 to 2.5 s, no cut |

- Use eased curves, never linear ones. A linear speed change looks like a cut.
- For a ramp across a cut, speed up at the end of shot A and slow down at the start of shot B.
- Keep generated footage at 25% speed or faster. Slower speeds warp hands and hair.
- Fake motion blur with a directional blur on the 2 to 4 fastest frames of a ramp.

## 3. Beat math

- Frames per beat = 60 / BPM x fps. At 120 BPM that is 15 frames. At 130 BPM it is 13.85 frames. At 140 BPM it is 12.86 frames.
- Round each cumulative beat position, not each step, so the cuts do not drift.
- Half a beat is an accent or flash cut. A quarter beat is for 2 to 4 frame stutters only. One bar is a phrase boundary.
- Cut 1 frame before the beat. The cut then reads as on the beat. Put the flash peak and the shake start on the beat frame itself.

## 4. Cut density

| Section | Cut interval |
|---|---|
| Hook | 2 to 4 beats |
| Build | 2, then 1, then half a beat (accelerating) |
| Tease before the drop | one hold of 2 to 3 beats |
| Breath | half a beat to one beat of black or near silence |
| Drop body | 1 beat or half a beat |
| Calm hold | 4 to 6 beats, no cut |
| End | one hold of 1.5 to 3 s |

- Do not cut on every beat at one pace. Vary the pattern, and put the biggest moments on the strongest beats.
- Build backward from the drop. A visual that lands half a beat late breaks the drop.
- Break the beat once for emphasis, not every time.
- Phonk is often felt in half time. Treat one cut per beat at 140 BPM (0.43 s) as the drop's fastest pace.

## 5. Hit frames

| Treatment | Use | Default |
|---|---|---|
| White flash | the drop, big accents | 1 to 2 frames, peak 0.85 to 1.0 |
| Black gap | between hits in dark edits | 1 to 3 frames; 6 to 14 frames before the drop |
| Strobe | the build into the drop | 2 frames on, 2 off, for 8 to 12 frames |
| Impact shake | hits and drops | 18 to 30 px, decaying over 6 to 10 frames |
| Zoom punch | accent beats in the build | 100 to 108% in 2 frames, back over 6 to 8 frames |
| Zoom blur cut | between fast shots | 6 to 8 frames, radial blur peak at the cut |
| Colour split | glitch hits | 6 to 14 px, decaying to 0 to 2 px in 6 frames |
| One-bit threshold | single accent frames | 1 to 3 frames at 45 to 55% luma; at most 3 per film |
| Negative | drop accent, reveal | 1 to 2 frames |
| Duotone | poster frames on bars | 2 to 4 frames, two colours |
| Bloom | lights, chrome, eyes | threshold 75 to 85% luma, blur 20 to 40 px at 1080 wide |
| Light leak | big hits | 12 to 24 frames, peak 60 to 80% at the cut |
| Grain | always on | subtle; heavier for black and white |
| Letterbox | cinema feel inside 9:16 | 120 to 260 px bars, in over 8 to 12 frames |
| Freeze card | hero moment | freeze 12 to 24 frames, white border, 100 to 104% scale |
| Exposure flash | eye reveal | ramp up over 4 frames, hold 2, back over 6 |
| Slices | car, fashion | 6 to 10 strips, staggered 1 frame each |
| Clone grid | flex, fashion | 2 x 2, then 3 x 3 or 4 x 4 on later beats |

Restraint, per 15 s film:

- One signature treatment, used 3 to 6 times.
- At most two secondary treatments.
- Flashes on 25 to 40% of cuts. More than half reads cheap.
- Shake only on accents, and it always decays.

## 6. Colour grades

| Grade | Settings |
|---|---|
| Teal and orange | shadows toward teal, skin and highlights toward orange, contrast up |
| Green-teal night | shadows toward green, skin kept warm, saturation 0.65 to 0.8, matte blacks |
| Crushed black and white | saturation 0, strong S-curve, 2 to 5% of blacks clipped, heavy grain, vignette |
| Cold blue night | blue shadows, exposure about -0.3 EV, bloom on lights, saturation 0.9 |
| Warm golden | warm highlights, brown shadows, saturation 1.05, soft red glow on highlights |
| Selective colour | one hue kept within about 15 degrees, the rest at saturation 0 |

Grade the subject and the background together. A shared grade and grain glue generated shots into one film.

## 7. Type

- One base colour and one accent per line. Never three colours.
- At most 2 words on screen per lockup. In the drop, at most one word per beat.
- A word appears on its beat, holds one beat and swaps on the next. Entry is 2 to 4 frames.
- Exit is a hard cut. Use fades only in the slow sections.
- Keep type off faces and off the action.
- Safe zone at 1080 x 1920: top 240 px, bottom 660 px, sides 120 px. Keep the right 180 px column clear from y = 840, except for centred slams.

## 8. Music

| Genre | BPM | Feel |
|---|---|---|
| Phonk | 130 to 160 | cowbell lead, distorted 808 slides, half-time feel |
| Drift phonk | 140 to 160 | aggressive, for cars, gym and games |
| Trap | 130 to 170 | half-time kick and snare, double-time hats |
| Techno | 120 to 128 | steady four on the floor, for fashion and daylight edits |
| Slowed and reverb | about 80% speed | soft edits |

- A phonk arrangement runs intro, main, breakdown, drop, outro, and repeats with small changes.
- Start a user track 1 to 2 bars before its first drop. Put the drop at 25 to 45% of the runtime.
- If the music peaks away from the story's main event, move the music, not the event.
- Use only music the user owns or has licensed. The default is the original score that the director's audio kit writes.

## 9. Shot types

| Shot | Purpose | Length |
|---|---|---|
| Eye close-up | hook | 0.4 to 1.0 s, slow push-in |
| Slow head turn | the aura gesture | 1.0 to 2.0 s at 20 to 40% speed |
| Walk to camera, low angle | power | 1.0 to 1.5 s |
| Backlit silhouette | mystery | 1.0 to 2.0 s |
| Detail inserts | density, status | 0.3 to 0.6 s each |
| Wide establishing shot | scale | 0.5 to 2.0 s |
| Calm against chaos | the emotional centre | 1.5 to 3.0 s |
| Gesture on the drop | the payoff | 0.8 to 1.5 s with a ramp |
| Profile with rim light | sculpted look | 0.6 to 1.2 s |
| Lens look | the ending | hold 1.5 to 3.0 s |

Generated footage:

- Skip the first 2 frames of each clip.
- Cut on action, not at rest. A still frame between two moves is the hardest seam to hide.
- Use the best 0.4 to 1.2 s window of each clip, inside its first 60 to 70%.
- Fix colour drift between clips with a small curve lift and a slight hue shift.

## 10. Cheap against strong

| Cheap | Strong |
|---|---|
| Many unrelated effects | One core effect, built on through the film |
| A transition on every cut | Mostly hard cuts |
| One pace from start to end | Hook, build, drop, resolve |
| Slow motion on the whole clip | Slow only the payoff |
| A hit half a beat late | The hit exactly on the beat |
| Sound effects on every cut | Sparse sound, only on hits |
| A logo on screen for a quarter of the runtime | The name on the end card only |
| Big smiles and a call to action | Deadpan and effortless |
| No grain on generated footage | Grain on every frame |

## 11. Category variants

| Variant | Music | Grade | Signature moves |
|---|---|---|---|
| Athlete | drift phonk, trap | teal and orange, or crushed black and white | eye close-up, impact slow motion, tunnel walk |
| Car | drift phonk | cold blue night | wheel macro, light sweep, headlight reveal, slices |
| Fashion | techno, funk | warm golden, or black and white | low-angle walk, turn, fabric inserts, freeze cards |
| Gym | phonk, trap | crushed contrast, hard top light | slow rep at peak, chalk puff, black hit frames |
| Luxury product | dark phonk, slowed trap | low key, heavy grain | the product as the calm subject, macro inserts, long end card |
| Couple or soft edit | slowed and reverb | warm golden, bloom | slow hair turns, freeze cards, soft crossfades |

For a product: the product is the calm subject in a fast world. The name appears only in the last 15 to 20% of the film.
