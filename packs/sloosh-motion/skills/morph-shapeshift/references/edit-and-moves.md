# The edit, the signature moves and the fixes

Read this with SKILL.md when you write or change `edit.py`. The default film is
`examples/morph-chain-15s-9x16/edit.py`; the code film is `examples/send-morph-12s-16x9/edit.py`.

## 1. Default cut list (Morph Chain, 15 s, 9:16)

```python
K = lambda i: f"plates/locked/k{i}.jpg"                    # figure-locked keys
C = lambda i: f"clips/locked/t{i}.mp4" if os.path.exists(f"clips/locked/t{i}.mp4") else f"clips/t{i}.mp4"
mx.shatter("shatter_k2_k3", K(2), K(3), 0.5); mx.flow("flow_k0_k6", K(0), K(6), 0.5); mx.flow("flow_k7_k0", K(7), K(0), 0.5)
SHOTS = [  # (start, end, source, in_point, speed, zoom_from, zoom_to, focus_x, focus_y, tags); focus y .27 = the eyes
    (0.00, 1.00, K(0), 0, 1, 1.00, 1.06, .5, .27, ""),
    (1.00, 2.50, C(1), 0.9, 1.3, 1.06, 1.00, .5, .27, ""),
    (2.50, 3.00, K(1), 0, 1, 1.10, 1.02, .5, .27, "punch"),
    (3.00, 3.25, K(1), 0, 1, 1.02, 1.00, .5, .27, "negative smear"),
    (3.25, 4.25, C(2), 1.0, 1.6, 1.00, 1.05, .5, .27, "ramp"),
    (4.25, 4.75, K(2), 0, 1, 1.08, 1.00, .5, .27, "red:0.5"),
    (4.75, 5.25, "shatter_k2_k3", 0, 1, 1.00, 1.00, .5, .27, "hard"),
    (5.25, BR, K(3), 0, 1, 1.00, 1.08, .5, .27, "bwflick"),
    (BR, D, "black", 0, 1, 1, 1, .5, .5, "hard"),
    (D + 0.00, D + 0.25, K(4), 0, 1, 1.10, 1.03, .5, .27, "punch shake leak"),
    (D + 0.25, D + 0.50, K(5), 0, 1, 1.03, 1.03, .5, .27, "hard"),
    (D + 0.50, D + 0.75, K(6), 0, 1, 1.03, 1.03, .5, .27, "hard red:0.45"),
    (D + 0.75, D + 1.00, K(7), 0, 1, 1.03, 1.03, .5, .27, "hard"),
    (D + 1.00, D + 1.25, K(4), 0, 1, 1.03, 1.05, .5, .27, "hard negative"),
    (D + 1.25, D + 1.50, K(5), 0, 1, 1.05, 1.05, .5, .27, "hard smear"),
    (D + 1.50, D + 1.75, K(6), 0, 1, 1.05, 1.05, .5, .27, "hard duo"),
    (D + 1.75, D + 2.00, K(7), 0, 1, 1.05, 1.08, .5, .27, "hard glitch"),
    (8.00, 9.50, C(3), 0.9, 1.3, 1.08, 1.00, .5, .27, "ramp"),
    (9.50, 10.0, "flow_k0_k6", 0, 1, 1.00, 1.03, .5, .27, "hard"),
    (10.0, 10.5, K(6), 0, 1, 1.10, 1.02, .5, .27, "punch"),
    (10.5, 11.0, K(5), 0, 1, 1.02, 1.04, .5, .27, "hard"),
    (11.0, 11.5, K(7), 0, 1, 1.04, 1.06, .5, .27, "hard red:0.4"),
    (11.5, 12.0, "flow_k7_k0", 0, 1, 1.06, 1.06, .5, .27, "hard"),
    (12.0, LEN, K(0), 0, 1, 1.06, 1.12, .5, .27, "hard"),     # end card, shaded 0 to 55% in render(t)
]
cuts = fk.CutList(SHOTS, beats=tl.BEATS, beat_punch=0.05, downbeat_split=14, fx_from=D, fx_to=tl.T_END)
```
25 cuts, 13 distinct sources, no clip window over 1.5 s. The layers in `render(t)`: cut list, end shade, type
overlay, `fk.hits` (the hits strike the type too), `fk.Finish(vignette=.6, bloom=.5, grain=6)`, then a flash on cuts.

## 2. Effect budget (per 15 s)

- Before the drop: the director's cut grammar on every cut; at most 2 whole-frame hits (one negative, one duo or red).
- Match cuts: `hard` (no zoom grammar, so the figure does not jump), one look tag on every other cut, beat punch 0.05.
- At most 3 visible photoreal transitions, at most 2 code morphs (flow, shatter) and one breath.
- Code films: grain at most 2.5, no vignette, no glitch; one negative frame on the click; a 0.045 punch on the drop.

## 3. Signature moves

| Move | What you see | How it is built |
|---|---|---|
| Keyframe edit chain | every look shares the exact pose, camera and light | each key is an edit of an approved key under the composition-master rule |
| Start+end transition clip | a physical transformation that lands exactly on the next key | the transition template in `references/photoreal-morph-recipes.md`; clean window 1.0-1.5 s at speed 1.3-1.6, or `ramp` |
| Face morph run | hero to wireframe to reptile to x-ray in about 5 s, a word per form | stills 0.5 s + transitions 1.0-1.5 s + hits between keys; the FORM tag rolls on each landing |
| Hits between keys | a 1-2 frame negative, smear, duo or red frame between looks | cut-list tags `negative smear`, `red:0.5`, `duo`; `tl.HITS` for hits that also strike the type |
| Outfit match cut (0.25 s) | eight outfits flash past, the face stays put | figure-locked keys, `hard` rows of 0.25 s on half-beats, a shutter tick per cut |
| Figure lock | the figure sits at the same spot and size in every look | `python3 lib/morphfx.py lock plates/k*.jpg --ref plates/k0.jpg`: upper-body centroid and square root of the area (or box centre + height for a full figure), scaled and moved onto k0. Look at `out/lock_check.jpg`. Put overrides in `lock.json` |
| Sliced shatter | the frame splits into vertical slices that fly apart centre-out; the next key settles from 1.08x | `mx.shatter(name, A, B, 0.5)`, row tag `hard` |
| Flow morph (code) | one key warps into the next with no generation | `mx.flow(name, A, B, 0.5)`: dense optical flow both ways at quarter size, warp and blend. It works when the keys share the pose |
| Box morph | a rounded rect changes size and radius; every in-between is a true rounded rect | `MK.chain(t, KEYS)` with `MK.box` keys, so it uses `MK.boxAt`; squash 0.04-0.08 |
| Twist-free path morph | any outline into any other, with no inside-out flip | `MK.ptsAt(A, B, u, {rotate: 8})` (128 aligned points); `{via: 'flub'}` for very different silhouettes |
| Content handoff | old content is gone in the first 30%, new content comes in over the last 40% | `MK.handoff(t, at, dur)` |
| One micro-action per state | the button presses, the loader spins, the bars grow | each in the middle of its hold, pure in t (see `ui/morph.html`) |
| OKLCH colour lag | colour arrives through the shape, never as a flash | `MK.colorLag(from, to, t, at, dur)` (20% to 90% of the morph) |
| Anticipation + overshoot | a squash before the first stretch, a 4% swell on landings | `MK.anticipate(t, at)`, `MK.overshoot(t, land, .04)`, `MK.press(t, at)` |
| Send, rings, eyes, wordmark | the send click squashes, rounded-square rings radiate, the bar collapses into the send button and grows into a dark glossy tile with an accent border, the logo's eyes pop in, glance and blink, then the full wordmark grows out of the tile with its eyes exactly over the tile's eyes | `ui/morph.html`: the cursor flies to the measured send button; `MK.rings`; chain keys SEND and TILE; the traced logo is drawn twice with ONE transform (the tile copy clipped to the icon box, the full copy revealed by a clip that grows from the icon box to the full box), so the eyes match by construction |
| Goo split and merge | one drop splits into three with live necks, orbits, and merges with one wobble | the `MK.goo()` filter on circles; children park 175 px out; one `MK.E.elastic` |
| Blob to letters | the blob becomes a crisp circle, which separates into the real letters | a same-frame hand-off outside the filter; `MK.separate(circle, letterRings)`; the layered logo fades in over it (`ui/liquid.html`) |
| Shards to mark | slate facets fly in from a ring, a warm blade slices, they fold into the letters | `MK.shards` + `MK.flub(tri, letter[i % n])`, a 2-frame key flash (`ui/shards.html`) |

The logo is ALWAYS the real file traced by `scripts/logo_to_path.py`. Never redraw it. Never ask a model to draw it.

## 4. Looks generated or amateur: concrete fixes

| Symptom | Fix |
|---|---|
| The figure jumps between outfits | Run the figure lock; make the key whose eye line is off by more than 2% again; tag match cuts `hard` |
| The face changes identity across keys | Edit each key from an approved key with the identity photo as image 2; judge it at full size |
| A transition looks like a cross-dissolve | Name a physical mechanism; write "one continuous physical transformation"; or use a sliced shatter |
| Plastic skin, glowing rim, hazy grade | Prompt the still with pores, oil shine, flyaways, fine noise and a practical key; one grade for all keys |
| A transition pops mid-way | The keys fail the pair check: make B again as an edit of A, or cut inside the holds and add a hit |
| A shape twists mid-morph | `MK.ptsAt` (aligned) instead of flubber; go via a circle; split it into parts |
| A rect morph bulges like a pillow | Box keys (`MK.box`), so `MK.chain` uses the parameter morph |
| It feels like a screensaver | Holds, one micro-action per state, a FORM word per state, at most 7 UI states |
| Muddy colour at the midpoint | `MK.colorLag` (OKLCH) |
| The eyes do not line up when the wordmark grows | Both logo copies must use the same transform; check the icon box in `ui/logo_check.png` (fix it with `--icon`) |
| The logo looks rounded or soft | It was inside the goo filter: hand off to crisp paths outside it |
| A seam between stills and clips | Use the same locked key as the clip's start or end frame; cut inside the hold; one hit at the seam |

Every new generation in a fix is a new item: a new quote, a new approval and a new idempotency key.
