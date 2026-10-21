"""edit.py (glitch-fx "Signal Lost"): the ONE editor script. A pure render(t): the same t always gives the same frame.

  python3 edit.py                          -> out/<NAME>_vN.mp4 (prints the glitch budget first)
  python3 edit.py out/sheet.jpg 0.5,2,6.4  -> stills only, for fast checks
Render the type and HUD frames first (frames/type, frames/hud); the layers load on the first render() call.

Sloosh made CLEAN footage only (realistic stills -> clips animated from them). Every glitch below is code:
  1 footage: cut list + camera + cut grammar (filmkit), sustained gl:* treatments (glitchkit.apply_tags)
  2 glitch transitions on cuts (line wipe, slice cut), then the HUD and the type (the type tears on its entrances)
  3 whole-frame hits AFTER the type (it tears with the frame), scanlines, finish, flash frames
"""
import sys; sys.path.insert(0, "lib")
import filmkit as fk
import glitchkit as gk
import tl

fk.setup(tl.W, tl.H, tl.FPS)
B, D, BR, END, L = tl.B, tl.DROP, tl.T_BREATH, tl.T_END, tl.LEN

# (start, end, source, in_point, speed, zoom_from, zoom_to, focus_x, focus_y, tags)
# Clean windows only (0.3-2 s each); `hard` on every row that a transition wipes in.
SHOTS = [
    (0.0,     2 * B,  "clips/c1.mp4",      0.4, 1.0, 1.00, 1.06, 0.5, 0.40, ""),              # HOOK: under the light, SIGNAL / LOST
    (2 * B,   4 * B,  "plates/hero.jpg",   0.0, 1.0, 1.08, 1.13, 0.5, 0.42, "gl:xray"),       # x-ray scan reveal + radiograph flicker
    (4 * B,   6 * B,  "plates/street.jpg", 0.0, 1.0, 1.00, 1.06, 0.5, 0.50, "hard"),          # line wipe in; HUD tracking
    (6 * B,   7 * B,  "clips/c2.mp4",      0.3, 1.0, 1.00, 1.04, 0.5, 0.55, ""),
    (7 * B,   9 * B,  "clips/c3.mp4",      0.6, 1.0, 1.05, 1.00, 0.5, 0.50, "gl:sort:0.4"),   # product turns, bright pixels drip
    (9 * B,   10 * B, "plates/macro.jpg",  0.0, 1.0, 1.10, 1.00, 0.5, 0.30, ""),
    (10 * B,  12 * B, "clips/c1.mp4",      1.8, 1.0, 1.12, 1.18, 0.5, 0.42, "hard"),          # slice cut in; eyes tracked
    (12 * B,  15 * B, "clips/c2.mp4",      1.2, 1.0, 1.00, 1.08, 0.5, 0.55, "ramp"),          # build, REBOOTING typed
    (15 * B,  BR,     "plates/hero.jpg",   0.0, 1.0, 1.15, 1.30, 0.5, 0.42, "hard"),          # psych strobe + tape stop
    (BR,      D,      "black",             0.0, 1.0, 1.00, 1.00, 0.5, 0.50, "hard"),          # the breath (noise confetti)
    (D,       18 * B, "clips/mosh.mp4",    1.75, 1.0, 1.12, 1.00, 0.5, 0.50, "punch shake"),  # DROP: datamosh blooms at D + 0.25
    (18 * B,  19 * B, "clips/c3.mp4",      2.2, 1.0, 1.00, 1.06, 0.5, 0.50, "punch"),         # NEW
    (19 * B,  20 * B, "plates/street.jpg", 0.0, 1.0, 1.25, 1.10, 0.5, 0.60, ""),              # BUILD (slices hit)
    (20 * B,  21 * B, "clips/c1.mp4",      3.0, 1.0, 1.10, 1.00, 0.5, 0.42, ""),              # LIVE
    (21 * B,  22 * B, "clips/c2.mp4",      3.2, 1.0, 1.00, 1.10, 0.5, 0.55, "gl:wave:0.03"),
    (22 * B,  24 * B, "clips/c1.mp4",      3.6, 1.0, 1.04, 1.12, 0.5, 0.42, ""),              # invert strobe x3
    (24 * B,  END,    "clips/c3.mp4",      3.0, 1.0, 1.08, 1.00, 0.5, 0.48, "hard"),          # line wipe in; the product holds
    (END,     L,      "#07070A",           0.0, 1.0, 1.00, 1.00, 0.5, 0.50, "hard"),          # END CARD: slice-stamp wordmark
]

cuts = fk.CutList(SHOTS, beats=tl.BEATS, beat_punch=0.05, downbeat_split=0, fx_from=D, fx_to=END)  # RGB split comes from hits only
footage = lambda t: gk.apply_tags(cuts.render(t), cuts, t)   # cut list + sustained gl:* treatments
TR = gk.Transitions(footage, tl.TRANS)                       # wipes hold the outgoing shot's last treated frame
GH = gk.Hits(tl.GLITCH, palette=(tl.ACCENT, tl.FRINGE[0], "#FFFFFF"))
finish = fk.Finish(vignette=0.5, bloom=0.45, grain=4)
TYPE = HUD = None   # made on the first render() so importing edit.py needs no rendered frames

def layers():
    global TYPE, HUD
    if TYPE is None:
        import os
        for d, page in (("frames/type", "ui/type.html"), ("frames/hud", "ui/hud.html")):
            if not os.path.isdir(d): sys.exit(f"!! {d} is missing: render {page} with lib/render_html.py first (see the header of {page}).")
        TYPE = gk.Layer("frames/type")                            # python3 lib/render_html.py ui/type.html --dur <LEN> --jobs 1 --out frames/type
        HUD = gk.Layer("frames/hud", start=tl.HUD["frame"][0])  # python3 lib/render_html.py ui/hud.html --dur <T_END> --jobs 1 --out frames/hud

def render(t):
    layers()
    f = fk.frame_of(t)
    img = footage(t)                              # footage + camera + cut grammar + sustained gl:* (x-ray scan, drips, wave)
    img = TR.apply(img, t)                        # line wipes / slice cuts on the cuts
    img = gk.over(img, HUD, t)                    # mono HUD
    img = gk.over(img, TYPE, t, tears=tl.TEARS)   # type, torn on its entrances
    img = GH.apply(img, t)                        # whole-frame hits: the type tears with the frame
    img = gk.scan(img, 4, 0.16)                   # CRT texture, 1 px every 4 px
    img = finish(img, f, grain=4)
    if cuts.flash_now(t): img = fk.flash(img)
    return img

if __name__ == "__main__":
    gk.budget(tl.GLITCH, L, B, tl.PRESET, drop=D)
    fk.run(render, L, tl.NAME)
