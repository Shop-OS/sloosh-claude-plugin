"""edit.py (dot-matrix-particles "Data Twin"): the ONE editor script. A pure render(t).

  python3 edit.py                          -> out/<NAME>_vN.mp4
  python3 edit.py out/sheet.jpg 0.5,2,6.4  -> stills only, for fast checks

Sloosh made CLEAN footage only (realistic stills on pure black -> clips animated from them). Every dot is code:
  1 footage: cut list + camera + cut grammar (filmkit), then `dots:*` tags turn each shot into dots AFTER the camera,
    so the grid stays fixed to the screen and the image moves under it (dotskit.apply_tags)
  2 dots transitions on cuts (halftone wipe, dither cut); the assemble window replaces the footage with particles
  3 the LED board lockup (Python, same grid), the HTML type layer, the drop flash, the finish (light grain on dots)
"""
import glob, sys; sys.path.insert(0, "lib")
import numpy as np
import filmkit as fk
import dotskit as dk
import tl

fk.setup(tl.W, tl.H, tl.FPS)
B, D, BR, L, P = tl.B, tl.DROP, tl.T_BREATH, tl.LEN, tl.PAL
A0, END = tl.T_ASM, tl.T_END

# (start, end, source, in_point, speed, zoom_from, zoom_to, focus_x, focus_y, tags)
# Clean windows only (0.2-2 s each). Strobe rows are `hard` (no zoom-blur grammar on 1/8-note cuts).
SHOTS = [
    (0.0,      4 * B,   "clips/c1.mp4",        0.3, 1.0, 1.00, 1.04, 0.5, 0.36, "dots:led rv:radial:0.5:0.34"),  # HOOK: LEDs switch on from the eyes
    (4 * B,    4.5 * B, "clips/c1.mp4",        2.0, 1.0, 1.06, 1.06, 0.5, 0.36, "hard punch"),                   # twin strobe: real
    (4.5 * B,  5 * B,   "clips/c1.mp4",        2.2, 1.0, 1.06, 1.06, 0.5, 0.36, "hard dots:ascii"),              #   ASCII
    (5 * B,    5.5 * B, "clips/c1.mp4",        2.4, 1.0, 1.06, 1.06, 0.5, 0.36, "hard dots:led inv"),            #   negative LED
    (5.5 * B,  6 * B,   "clips/c1.mp4",        2.6, 1.0, 1.08, 1.08, 0.5, 0.36, "hard punch"),                   #   real
    (6 * B,    6.5 * B, "clips/c1.mp4",        2.8, 1.0, 1.08, 1.08, 0.5, 0.36, "hard dots:ascii"),
    (6.5 * B,  7 * B,   "clips/c1.mp4",        3.0, 1.0, 1.08, 1.08, 0.5, 0.36, "hard dots:led"),
    (7 * B,    11 * B,  "plates/portrait.jpg", 0.0, 1.0, 1.00, 1.00, 0.5, 0.45, "dots:cloud yaw:-0.7:0.6"),      # BUILD: point-cloud scan + labels
    (11 * B,   14 * B,  "clips/c2.mp4",        0.4, 1.0, 1.00, 1.05, 0.5, 0.50, "dots:thermal"),                 # thermal reveal of the product
    (14 * B,   BR,      "plates/product.jpg",  0.0, 1.0, 1.00, 1.00, 0.5, 0.50, "dots:cloud yaw:0.5:1.1 implode"), # the cloud implodes to a core
    (BR,       D,       "black",               0.0, 1.0, 1.00, 1.00, 0.5, 0.50, "hard"),                          # breath
    (D,        18 * B,  "plates/product.jpg",  0.0, 1.0, 1.10, 1.00, 0.5, 0.45, "dots:led burst:0.5:0.42 punch shake"),  # DROP: burst, all on
    (18 * B,   20 * B,  "clips/c2.mp4",        1.0, 1.0, 1.00, 1.04, 0.5, 0.50, "dots:half rv:radial:0.5:0.5 ripple:0.5:0.5:0.6"),  # dot-wave reveal
    (20 * B,   21 * B,  "clips/c2.mp4",        1.9, 1.0, 1.04, 1.00, 0.5, 0.50, "hard"),                          # the real product (halftone wipe in)
    (21 * B,   22 * B,  "clips/c1.mp4",        3.6, 1.0, 1.10, 1.04, 0.5, 0.36, "dots:half45"),                   # editorial 45 deg halftone
    (22 * B,   24 * B,  "clips/c2.mp4",        2.6, 1.0, 1.00, 1.06, 0.5, 0.55, "hard dots:dither resolve"),      # dither resolve; LED board MADE OF / LIGHT
    (24 * B,   END,     "plates/product.jpg",  0.0, 1.0, 1.00, 1.00, 0.5, 0.50, "dots:half"),                     # halftone -> particles -> wordmark
    (END,      L,       "black",               0.0, 1.0, 1.00, 1.00, 0.5, 0.50, "hard dots:grid"),                # END CARD: dot grid + scan sweep
]

cuts = fk.CutList(SHOTS, beats=tl.BEATS, beat_punch=0.04, downbeat_split=0, fx_from=D, fx_to=END)
footage = lambda t: dk.apply_tags(cuts.render(t), cuts, t, P)
TR = dk.Transitions(footage, tl.TRANS, P)
finish = fk.Finish(vignette=0.45, bloom=0.35, grain=2.5)                  # dots: light grain, black stays black
_type = {}
def type_layer():
    """the rendered HTML type (python3 lib/render_html.py ui/type.html --dur <LEN> --jobs 1 --out frames/type).
    Loaded on first use, so importing this file needs no rendered frames."""
    if "t" not in _type:
        if not glob.glob("frames/type/*.png"):
            sys.exit("edit.py: no type frames in frames/type. Render them first: "
                     "python3 lib/render_html.py ui/type.html --dur %.2f --jobs 1 --out frames/type" % tl.LEN)
        _type["t"] = dk.Layer("frames/type")
    return _type["t"]
PORTRAIT = tl.W / tl.H < 0.85; SC = min(tl.W, tl.H) / 1080                  # 9:16 and 4:5 are portrait; 1:1 and 16:9 use the wide layout
HALF = tl.W / 2 - 120 * SC if PORTRAIT else min(tl.W * 0.446, 540 * SC)   # the type safe zone; on 16:9 a centred board, not a full-width bar
SAFE = (tl.W / 2 - HALF, tl.W / 2 + HALF)
BOARD = dk.LEDText(tl.COPY["led"], p=12, cap=11 if PORTRAIT else 9, y=tl.H * (300 / 1920 if PORTRAIT else 0.08), safe=SAFE,
                   ramp=(P["BG"], P["MID"], P["INK"], P["HOT"]))           # the top band, over the subject's crown
_asm = {}
def assemble():
    """built once: sources = the halftone grid of the real frame at A0, targets = the rendered wordmark frame."""
    if "a" not in _asm:
        _asm["a"] = dk.Assemble(cuts.render(A0), type_layer().rgba(tl.TYPE["word"][0] + 0.5), A0 + 0.25, END - 0.05, p=12,
                                fade_from=END, fade=0.45, PAL=P)
    return _asm["a"]

def render(t):
    f = fk.frame_of(t)
    img = TR.apply(footage(t), t)                                          # dots footage + transitions
    if A0 + 0.25 <= t < END + 0.45:                                        # particles fly into the wordmark
        parts = assemble().render(img.shape, t)
        img = parts if t < END else np.maximum(img, parts)                 # over the end-card grid while they fade
    img = BOARD.over(img, t, *tl.TYPE["led"])                              # LED board lockup
    img = dk.over(img, type_layer(), t)                                    # crisp HTML type
    img = fk.hits(img, t, tl.HITS)                                         # the drop flash
    img = finish(img, f, grain=2.5)
    if cuts.flash_now(t): img = fk.flash(img)
    return img

if __name__ == "__main__":
    fk.run(render, L, tl.NAME)
