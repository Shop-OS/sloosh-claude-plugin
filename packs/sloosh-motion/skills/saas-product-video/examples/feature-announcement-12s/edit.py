"""edit.py: the ONE editor script of the default feature film. A pure render(t).

  python3 edit.py                          -> out/<NAME>_vN.mp4 (next free version; never overwrites)
  python3 edit.py out/sheet.jpg 0.5,2,6.4  -> stills only, for fast checks

Layers: 1 footage cut list (AI windows + "page:feat" rows owned by the opaque feature page), 2 the type layer,
3 hits that also hit the type, the finish (footage vs page), flash frames on cuts.
"""
import sys; sys.path.insert(0, "lib")
import filmkit as fk
import saaskit as sk
import tl

fk.setup(tl.W, tl.H, tl.FPS)
B, D, P = tl.B, tl.DROP, tl.T_PAY

# (start, end, source, in_point, speed, zoom_from, zoom_to, focus_x, focus_y, tags)
SHOTS = [
    (0.00,        0.75,        "clips/c1.mp4", 0.40, 1.0, 1.00, 1.06, 0.45, 0.45, ""),           # the pain: desk
    (0.75,        tl.T_RUSH,   "clips/c2.mp4", 1.10, 1.0, 1.10, 1.00, 0.55, 0.50, ""),           # hand on the phone
    (tl.T_RUSH,   tl.T_NAME,   "clips/c1.mp4", 1.80, 1.0, 1.10, 1.90, 0.56, 0.40, "rush"),       # into the screen -> white
    (tl.T_NAME,   tl.T_BREATH, "black",        0.0,  1.0, 1.00, 1.00, 0.50, 0.50, "page:feat"),  # NEW pill + name + benefit
    (tl.T_BREATH, D,           "black",        0.0,  1.0, 1.00, 1.00, 0.50, 0.50, "hard"),       # the breath
    (D,           P,           "black",        0.0,  1.0, 1.00, 1.00, 0.50, 0.50, "page:feat"),  # THE DROP: the feature in the UI
    (P,           P + B,       "clips/c2.mp4", 2.40, 1.0, 1.14, 1.00, 0.55, 0.50, "punch shake"),
    (P + B,       P + 2 * B,   "clips/c1.mp4", 2.90, 1.0, 1.00, 1.08, 0.45, 0.45, "ramp"),
    (P + 2 * B,   tl.T_END,    "clips/c2.mp4", 0.30, 1.0, 1.00, 1.10, 0.55, 0.50, "zblur whiteout"),
    (tl.T_END,    tl.LEN,      "#0B0B0F",      0.0,  1.0, 1.00, 1.00, 0.50, 0.50, "card"),
]

cuts = fk.CutList(SHOTS, beats=tl.BEATS, beat_punch=0.07, downbeat_split=14, fx_from=P, fx_to=tl.T_END)
FOOT = fk.Finish(vignette=0.6, bloom=0.55, grain=6)
UIF = fk.Finish(contrast=False, vignette=0, bloom=0, grain=2.5)
_L = {}
def layers():
    """Load the rendered page frames on first use, so audio.py can import SHOTS before the pages exist."""
    if not _L:
        _L["PAGES"] = {"feat": fk.Overlay("frames/feature", start=tl.T_NAME)}   # render_html.py ui/feature.html --dur FEAT_NAT --scale 2
        _L["TYPE"] = fk.Overlay("frames/type")                                 # --dur LEN
    return _L

def render(t):
    L = layers(); PAGES, TYPE = L["PAGES"], L["TYPE"]
    s = cuts.shots[cuts.index(t)]
    img = cuts.render(t)
    if s.has("rush"): img = sk.rush(img, (t - s.start) / s.dur, s.fx, s.fy)
    page = (s.arg("page") or [None])[0]
    if page: img = PAGES[page].over(img, t, zoom=sk.punch_in(t, D, 0.06))     # the drop punches the window
    img = TYPE.over(img, t)
    img = fk.hits(img, t, tl.HITS)
    img = sk.whip_at(img, t, [P])                                           # whip out of the UI into the payoff
    img = (UIF if page or s.has("card") else FOOT)(img, fk.frame_of(t))
    if cuts.flash_now(t): img = fk.flash(img)
    return img

if __name__ == "__main__":
    fk.run(render, tl.LEN, tl.NAME)
