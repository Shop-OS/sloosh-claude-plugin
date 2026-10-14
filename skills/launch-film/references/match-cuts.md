# Match-cut catalogue

Every scene boundary should be one of these. Each entry: when to use, how to build it,
where a worked example lives (`examples/` = `references/examples/`).

## Contents
1. Rules that apply to every cut
2. Object-locked photo cut (crop camera)
3. In-frame swap (print / card)
4. Window expand
5. Tile expand (contact sheet)
6. Zoom-through
7. Graphic match (badge, icon, shape)
8. Colour / pixel-block wipe
9. Push-in hand-off between UI states
10. Whip pan
11. Flash / shutter
12. Feature match between different photos or clips (eye-to-eye, horizon, silhouette)
13. Continuous camera (no cut)
14. Sketch-to-photo reveal

## 1. Rules

- Cuts happen on integer frames. Put scene boundaries on the frame where the new picture
  should be first seen — 0–2 frames before the word that names it.
- Never let motion-blur samples straddle a cut: in `samplesAt`, return 1 on the first frame
  after any internal cut (`if (fr >= CUT && fr < CUT + 1) return 1`).
- Hero cuts get a 2-frame RGB split (`ChromaSplit amount 12 → 0`) and an SFX whose peak
  lands on the cut frame. Do not stack more than one "effect" on a cut.
- Overlays that track the object (bbox, crosshair, label) persist across the cut; change
  only the label text ("YOUR CAKE" → "ON THE MOON"). That continuity is what sells it.
- Verify with `scripts/blend_check.sh` (50 % blend of the frames either side of the cut):
  the shared object should look like one object.

## 2. Object-locked photo cut (crop camera)

Same object, same screen rectangle, different world (source photo → AI result).
1. Measure the object box in both images (`gridify.py`), using a stable sub-part (cake
   body, cup body, chair seat) rather than parts that differ.
2. `align_pair.py` gives scale/offset for each image so the boxes coincide *and* both
   images cover the frame. Typical: result at full-frame scale (1920/1672 ≈ 1.148), source
   scaled up to match.
3. Drive both with one view rectangle (`lib/cropCamera.ts`): the camera is a zoom `k`
   around the object's screen centre; image A renders `crop = viewA(k)`, image B
   `crop = mapAtoB(viewA(k))`. Continuing the same push across the cut makes it seamless.
4. If orientations differ (handle left vs right, chair facing), mirror the source and note it.
Example: `examples/scenes/HIJ_Cake.tsx`, `examples/lib/cakeView.ts`.

## 3. In-frame swap (print / card)

A photo print or UI card stays still; its content swaps from source to result with the
object at the same inner position. Solve crop rectangles so the object centre/width match
inside the card (same maths as §2 on the card's inner box). Then the card can unfold into a
grid (storyboard) or shrink into a layout. Example: `examples/scenes/KL_Cup.tsx`.

## 4. Window expand

Source shown through a window cut into a paper sheet, positioned at the result's aligned
placement. On the cut, the window becomes the full frame and the image swaps to the result.
Keep any zoom applied to the window content continuous in the next shot.
Example: `examples/scenes/M_Product.tsx` → `examples/scenes/NO_Finale.tsx`.

## 5. Tile expand

A contact-sheet tile grows to full frame while its crop rectangle interpolates from the
tile crop to the next scene's opening view (`lerpRect(tileCrop, nextView, p)`). Finish the
expansion 1–2 frames before the boundary so the last frame equals the next scene's first.
Example: `examples/scenes/G_Explore.tsx` (`Sheet`).

## 6. Zoom-through

Push into a dark (or solid) shape until it fills the frame, then start the next scene on
that colour. Zoom in log space (`k = K^p`), ease-in cubic, finish 1–2 frames before the
boundary so the last frame is solid. 24–28 motion-blur samples during the push.
Example: logo pupil in `examples/scenes/A_Logo.tsx`.

## 7. Graphic match

End a beat with a graphic (eye badge, icon, button) centred and large; start the next
scene with the camera extremely close on the same graphic inside the UI, then pull back.
Match position and size (perceived scale at focus = 1500 / (1500 − z)).
Example: `examples/scenes/D_Creative.tsx` → `examples/scenes/E_Spaces.tsx`.

## 8. Colour / pixel-block wipe

A clicked accent element triggers a stepped pixel-block wipe (`PixelWipe`, cell 80–100 px,
directional ramp + noise, a few ink accent cells mid-transition) that finishes on a solid
accent frame, which is the next scene's background. Example: `examples/scenes/C_Choose.tsx`.

## 9. Push-in hand-off between UI states

Push the camera into the element that was just clicked (card thumbnail, upload slot) until
it fills the frame; open the next scene on the same content at the same size (e.g. the
slot's image becomes a canvas node), then pull back. Example: E → F → G in `examples/`.

## 10. Whip pan

Outgoing content accelerates sideways (`inExpo`), incoming content arrives with the same
direction and decelerates (`outExpo`). Use 12–16 samples plus `smearAt` (axis-aligned
gaussian, up to 40–70 px) so it reads as a smear, not strobing copies.
Example: B → C, L → M.

## 11. Flash / shutter

For "photograph"/camera beats: white flash ramps to 1.0 on the last frame of the outgoing
shot and decays over ~6 frames in the new one; shutter SFX peak on the cut.

## 12. Feature match between different images or clips

Eye → eye, painted horizon → real horizon, printed vessel → photographed vessel, round
object → round object. Measure the feature point and size in both frames (for clips, on
the exact source frame you cut on), then place/zoom each so the feature shares a screen
position and size. Push in on the outgoing feature for a few frames and continue the push
on the incoming one. For video, pick `trimBefore` so the incoming clip starts on a frame
whose feature matches.

## 13. Continuous camera

Not a cut: a layout morphs into the next (campaign board spreading into the floating
cards of an end card). Interpolate each element's box between two layouts.
Example: `examples/scenes/NO_Finale.tsx`.

## 14. Sketch-to-photo reveal

A hand-drawn idea (SVG strokes drawn with `pathLength=1` dash offsets) is placed so its key
shape sits over the real object in a photo; the photo fades/wipes in under the strokes,
then the strokes fade. Pays off an earlier "idea" beat. Measure the photo object box and
fit the sketch's bounding box to it.
