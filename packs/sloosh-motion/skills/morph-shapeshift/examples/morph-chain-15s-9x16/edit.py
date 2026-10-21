"""edit.py: Morph Chain (photoreal), 15 s 9:16. ONE editor script with a pure render(t).

  python3 edit.py out/sheet.jpg 0.5,1.7,2.7,...   -> stills sheet (QA by looking)      python3 edit.py -> out/morph_chain_vN.mp4
Sources: plates/locked/k0..k7.jpg = generated keyframes, each EDITED from the previous (same pose, camera, light),
figure-locked with `python3 lib/morphfx.py lock plates/k*.jpg --ref plates/k0.jpg`. clips/t1..t3.mp4 = generated
transition clips with a start AND an end frame (hold 0-1.2 s, morph 1.2-2.8 s, hold 2.8-5 s). A figure-locked clip in
clips/locked/tN.mp4 replaces clips/tN.mp4 when it exists. flow_* and shatter_* are code morphs.
Layers: footage cut list -> end shade -> type (frames/type) -> whole-frame hits (hit the type too) -> finish -> flash.
"""
import os, sys; sys.path.insert(0, "lib")
import numpy as np
import filmkit as fk, morphfx as mx
import tl

fk.setup(tl.W, tl.H, tl.FPS)
B, D, BR = tl.B, tl.DROP, tl.T_BREATH
K = lambda i: f"plates/locked/k{i}.jpg"
C = lambda i: f"clips/locked/t{i}.mp4" if os.path.exists(f"clips/locked/t{i}.mp4") else f"clips/t{i}.mp4"
mx.shatter("shatter_k2_k3", K(2), K(3), 0.5)              # SLICED SHATTER between two keys (code)
mx.flow("flow_k0_k6", K(0), K(6), 0.5)                    # CODE MORPH (optical flow) hero -> navy knit
mx.flow("flow_k7_k0", K(7), K(0), 0.5)                    # ... denim -> hero, landing on the end-card frame

# (start, end, source, in_point, speed, zoom_from, zoom_to, focus_x, focus_y, tags)   focus y 0.27 = the eyes
SHOTS = [
    (0.00, 1.00, K(0),            0.0, 1.0, 1.00, 1.06, .5, .27, ""),                 # HOOK: hero still (handheld + push)
    (1.00, 2.50, C(1),            0.9, 1.3, 1.06, 1.00, .5, .27, ""),                 # transition k0 -> k1 (wireframe), clean window
    (2.50, 3.00, K(1),            0.0, 1.0, 1.10, 1.02, .5, .27, "punch"),            # FORM 02 lands
    (3.00, 3.25, K(1),            0.0, 1.0, 1.02, 1.00, .5, .27, "negative smear"),   # hit between keys
    (3.25, 4.25, C(2),            1.0, 1.6, 1.00, 1.05, .5, .27, "ramp"),             # transition k1 -> k2 (reptile)
    (4.25, 4.75, K(2),            0.0, 1.0, 1.08, 1.00, .5, .27, "red:0.5"),          # FORM 03 + duo hit (tl.HITS)
    (4.75, 5.25, "shatter_k2_k3", 0.0, 1.0, 1.00, 1.00, .5, .27, "hard"),             # sliced shatter into the x-ray
    (5.25, BR,   K(3),            0.0, 1.0, 1.00, 1.08, .5, .27, "bwflick"),          # FORM 04
    (BR,   D,    "black",         0.0, 1.0, 1.00, 1.00, .5, .50, "hard"),             # the breath
    # DROP: outfit match-cuts, 0.25 s each, figure-locked, so only the clothes change (hard = no zoom grammar)
    (D + 0.00, D + 0.25, K(4), 0, 1, 1.10, 1.03, .5, .27, "punch shake leak"),
    (D + 0.25, D + 0.50, K(5), 0, 1, 1.03, 1.03, .5, .27, "hard"),
    (D + 0.50, D + 0.75, K(6), 0, 1, 1.03, 1.03, .5, .27, "hard red:0.45"),
    (D + 0.75, D + 1.00, K(7), 0, 1, 1.03, 1.03, .5, .27, "hard"),
    (D + 1.00, D + 1.25, K(4), 0, 1, 1.03, 1.05, .5, .27, "hard negative"),
    (D + 1.25, D + 1.50, K(5), 0, 1, 1.05, 1.05, .5, .27, "hard smear"),
    (D + 1.50, D + 1.75, K(6), 0, 1, 1.05, 1.05, .5, .27, "hard duo"),
    (D + 1.75, D + 2.00, K(7), 0, 1, 1.05, 1.08, .5, .27, "hard glitch"),
    (tl.T_BACK, 9.50, C(3),       0.9, 1.3, 1.08, 1.00, .5, .27, "ramp"),           # transition k7 -> k0, back to the hero
    (9.50, 10.0, "flow_k0_k6",   0.0, 1.0, 1.00, 1.03, .5, .27, "hard"),             # code morph into the payoff
    (10.0, 10.5, K(6),           0.0, 1.0, 1.10, 1.02, .5, .27, "punch"),            # SHAPE / SHIFT echo lands
    (10.5, 11.0, K(5),           0.0, 1.0, 1.02, 1.04, .5, .27, "hard"),
    (11.0, 11.5, K(7),           0.0, 1.0, 1.04, 1.06, .5, .27, "hard red:0.4"),
    (11.5, 12.0, "flow_k7_k0",   0.0, 1.0, 1.06, 1.06, .5, .27, "hard"),
    (12.0, tl.LEN, K(0),         0.0, 1.0, 1.06, 1.12, .5, .27, "hard"),             # END CARD on the hero (shaded)
]

cuts = fk.CutList(SHOTS, beats=tl.BEATS, beat_punch=0.05, downbeat_split=14, fx_from=D, fx_to=tl.T_END)
finish = fk.Finish(vignette=0.6, bloom=0.5, grain=6)
TYPE = fk.Overlay("frames/type")

def render(t):
    img = cuts.render(t)
    if t >= tl.T_END:                                       # end-card shade: 0 -> 55% black over 0.8 s
        img = (img * (1 - 0.55 * fk.ease_out((t - tl.T_END) / 0.8, 3))).astype(np.uint8)
    img = TYPE.over(img, t)
    img = fk.hits(img, t, tl.HITS)                          # negatives / duo / white hit the type too
    img = finish(img, fk.frame_of(t))
    if cuts.flash_now(t): img = fk.flash(img)
    return img

if __name__ == "__main__":
    fk.run(render, tl.LEN, tl.NAME)
