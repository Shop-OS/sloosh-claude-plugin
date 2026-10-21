"""edit.py: the product-reveal compositor. A pure render(t).

  python3 edit.py                          -> out/<NAME>_vN.mp4
  python3 edit.py out/sheet.jpg 0.5,2,6.4  -> stills only (QA sheet)
  FILMKIT_PLACEHOLDERS=1 python3 edit.py out/sheet.jpg   -> placeholder cards for missing sources

Layers, bottom to top:
  1. footage: the cut list (generated clips through clean windows, stills with handheld), cut grammar, beat FX
  2. packshot (T_PACK..LEN): ui/packshot.html = the type BEHIND the product, then shadow + reflection + the REAL cutout
     + masked sweep, over the empty set plate. This is the cut-out layering: footage -> type -> product.
  3. front type: ui/type.html (counter, two-line stack, slams, echo stack, end card)
  4. whole-frame hits (hit the type too) -> finish (contrast, vignette, bloom, light grain) -> flash frames
Render the pages first (until then the film renders without that layer, and says so):
  python3 lib/render_html.py ui/type.html --dur <LEN> --out frames/type --jobs 1
  python3 lib/render_html.py ui/packshot.html --from <T_PACK> --dur <LEN-T_PACK> --out frames/pack --jobs 1
audio.py imports SHOTS from this file, so nothing below SHOTS runs on import.
"""
import glob, os, sys; sys.path.insert(0, "lib")
import filmkit as fk
import tl

fk.setup(tl.W, tl.H, tl.FPS)
B, D = tl.B, tl.DROP

# ---- the cut list: (start, end, source, in_point, speed, zoom_from, zoom_to, focus_x, focus_y, tags)
# in_point = the start of each clip's CLEAN WINDOW (from `lib/sheets.py clip clips/x.mp4`). No row longer than 2.5 s
# except the packshot + end card. Focus (fx, fy) = where the product detail sits in that shot.
AX, AY = 0.50, 0.30               # where the identity anchor (the cap) sits in the hook frame: the push-in aims here
SHOTS = [
    # HOOK: rim light crawls along the edge on black; slow push, then the push accelerates into the anchor
    (0.0,          tl.T_PUSH,    "clips/hook.mp4",     0.40, 1.0, 1.00, 1.06, AX, AY, ""),
    (tl.T_PUSH,    tl.T_D1,      "clips/hook.mp4",     2.275, 1.0, 1.06, 1.42, AX, AY, "hard ramp"),   # same source, continuous
    # DETAILS: anchor (match cut: starts already pushed in), label, material; each ramps into its cut.
    # The READABLE label is a CODE shot: the real cutout at 2.8x with a masked sweep (scripts/label_macro.py); the row adds the push.
    (tl.T_D1,      tl.T_D2,      "clips/anchor.mp4",   0.50, 1.0, 1.12, 1.00, 0.5, 0.45, ""),
    (tl.T_D2,      tl.T_D3,      "clips/label_macro.mp4", 0.45, 1.0, 1.00, 1.08, 0.5, 0.50, "ramp"),
    (tl.T_D3,      tl.T_ACT,     "clips/material.mp4", 0.60, 1.0, 1.00, 1.08, 0.5, 0.50, "ramp"),
    # ACTION: one clean window at speed, then the money moment in slow motion
    (tl.T_ACT,     tl.T_ACT + B, "clips/action.mp4",   0.70, 1.0, 1.00, 1.04, 0.5, 0.40, ""),
    (tl.T_ACT + B, tl.T_BUILD,   "clips/action.mp4",   1.60, 0.5, 1.04, 1.10, 0.5, 0.40, "ramp"),
    # BUILD: half-beat windows from earlier clips, accelerating into the breath
    (tl.T_BUILD,           tl.T_BUILD + 0.5 * B, "clips/anchor.mp4",   2.40, 1.0, 1.10, 1.00, 0.5, 0.45, "ramp"),
    (tl.T_BUILD + 0.5 * B, tl.T_BUILD + 1.0 * B, "clips/label.mp4",    2.20, 1.0, 1.00, 1.12, 0.5, 0.50, "ramp"),   # S4: print area in soft focus
    (tl.T_BUILD + 1.0 * B, tl.T_BUILD + 1.5 * B, "clips/label_macro.mp4", 2.55, 1.0, 1.12, 1.00, 0.5, 0.50, "zblur"),
    (tl.T_BUILD + 1.5 * B, tl.T_BUILD + 2.0 * B, "clips/hook.mp4",     3.20, 1.0, 1.00, 1.15, AX, AY, "ramp"),
    (tl.T_BUILD + 2.0 * B, tl.T_BREATH,          "clips/action.mp4",   3.00, 1.0, 1.10, 1.20, 0.5, 0.40, "ramp"),
    # BREATH: black (a white strobe lands inside it from tl.HITS)
    (tl.T_BREATH,  D,            "black",              0.0, 1.0, 1.0, 1.0, 0.5, 0.5, "hard"),
    # HERO lands on the set: punch + leak
    (D,            tl.T_RUN,     "clips/hero.mp4",     0.60, 1.0, 1.16, 1.02, 0.5, 0.55, "hard punch leak"),
    # FEATURE RUN: a cut on every beat, a word on every beat (type.html)
    (tl.T_RUN,         tl.T_RUN + B,     "clips/material.mp4", 1.20, 1.0, 1.10, 1.00, 0.5, 0.50, ""),
    (tl.T_RUN + B,     tl.T_RUN + 1.5 * B, "clips/hook.mp4",   3.60, 1.0, 1.00, 1.08, AX, AY, ""),   # never a label shot under a slam
    (tl.T_RUN + 1.5 * B, tl.T_RUN + 2 * B, "clips/action.mp4", 2.20, 1.0, 1.08, 1.00, 0.5, 0.40, "ramp"),
    (tl.T_RUN + 2 * B, tl.T_PACK,        "clips/anchor.mp4",   1.40, 1.0, 1.15, 1.02, 0.5, 0.45, "punch"),
    # PACKSHOT + END CARD: the empty set plate, locked (no handheld: the code product must not slide on the floor)
    (tl.T_PACK,    tl.LEN,       "plates/set_empty.jpg", 0.0, 1.0, 1.00, 1.00, 0.5, 0.5, "hard locked"),
]

def overlay(folder, page, **kw):
    """the PNG sequence rendered from a page, or None (with a hint) while it is not rendered yet"""
    if glob.glob(os.path.join(folder, "*.png")):
        return fk.Overlay(folder, **kw)
    print(f"edit.py: no frames in {folder} yet, so the film renders without {page}. Run lib/render_html.py first.")
    return None

if __name__ == "__main__":
    cuts = fk.CutList(SHOTS, beats=tl.BEATS, beat_punch=0.06, downbeat_split=8, fx_from=D, fx_to=tl.T_PACK)
    finish = fk.Finish(vignette=0.5, bloom=0.45, grain=2.5)     # product films stay crisp: light grain
    PACK = overlay("frames/pack", "ui/packshot.html", start=tl.T_PACK)
    TYPE = overlay("frames/type", "ui/type.html")

    def render(t):
        img = cuts.render(t)
        if PACK is not None and t >= tl.T_PACK: img = PACK.over(img, t)   # type behind -> product on top (in the page)
        if TYPE is not None: img = TYPE.over(img, t)
        img = fk.hits(img, t, tl.HITS)
        img = finish(img, fk.frame_of(t))
        if cuts.flash_now(t): img = fk.flash(img)
        return img

    fk.run(render, tl.LEN, tl.NAME)
