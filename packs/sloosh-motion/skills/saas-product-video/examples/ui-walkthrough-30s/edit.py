"""edit.py: the ONE editor script of the default SaaS film. A pure render(t): the same t gives the same frame.

  python3 edit.py                          -> out/<NAME>_vN.mp4 (next free version; never overwrites)
  python3 edit.py out/sheet.jpg 0.5,2,6.4  -> stills only, for fast checks (a 16-still sheet covers every section)

Layers, bottom to top:
  1. footage: the cut list. AI camera shots (approved stills -> AI clips) in short clean windows, plus rows
     whose tag "page:<name>" says an opaque HTML page owns that span (intro, ui, build)
  2. the toggle overlay (ui/toggle.html) and the type layer (ui/type.html), transparent PNG sequences
  3. whole-frame hits that also hit the type, then the finish (footage: contrast/vignette/bloom/grain 6;
     UI pages: grain 2.5 only, no vignette, no bloom), then flash frames on cuts
"""
import sys; sys.path.insert(0, "lib")
import filmkit as fk
import saaskit as sk
import tl

fk.setup(tl.W, tl.H, tl.FPS)
B, D, C = tl.B, tl.DROP, tl.T_CLICK

# (start, end, source, in_point, speed, zoom_from, zoom_to, focus_x, focus_y, tags)
# REPLACE sources with the approved clips and set each in_point from its clip sheet (clean windows, first 60-70%).
SHOTS = [
    # HOOK: the problem, AI camera shots, one per beat or two
    (0.00,         1.25,         "clips/c1.mp4", 0.40, 1.0, 1.00, 1.05, 0.45, 0.45, ""),            # desk, wide (lockup 1)
    (1.25,         2.00,         "clips/c2.mp4", 1.10, 1.0, 1.08, 1.00, 0.55, 0.50, ""),            # hand on the phone (lockup 2)
    (2.00,         tl.T_INTRO,   "clips/c1.mp4", 1.80, 1.0, 1.10, 1.90, 0.56, 0.40, "rush"),        # push into the screen -> white
    # PAGES: the gradient intro, the breath, THE DROP (UI walkthrough), the results build
    (tl.T_INTRO,   tl.T_BREATH,  "black",        0.0,  1.0, 1.00, 1.00, 0.50, 0.50, "page:intro"),
    (tl.T_BREATH,  D,            "black",        0.0,  1.0, 1.00, 1.00, 0.50, 0.50, "hard"),        # 3 frames of black + silence
    (D,            tl.T_BUILD,   "black",        0.0,  1.0, 1.00, 1.00, 0.50, 0.50, "page:ui"),
    (tl.T_BUILD,   tl.T_TOG,     "black",        0.0,  1.0, 1.00, 1.00, 0.50, 0.50, "page:build"),
    # BEFORE: one clip, deliberately flat, OFF toggle centred
    (tl.T_TOG,     C,            "clips/c3.mp4", 0.50, 1.0, 1.00, 1.03, 0.50, 0.55, "flat hard"),
    # AFTER: switched on the click frame (same clip, same moment), then every beat effect on
    (C,            C + 2 * B,    "clips/c3.mp4", 1.50, 1.0, 1.16, 1.00, 0.50, 0.55, "punch shake leak"),
    (C + 2 * B,    C + 3 * B,    "clips/c1.mp4", 2.90, 1.0, 1.00, 1.08, 0.45, 0.45, "ramp"),
    (C + 3 * B,    C + 4 * B,    "clips/c2.mp4", 2.40, 1.0, 1.12, 1.00, 0.55, 0.50, ""),
    (C + 4 * B,    C + 5 * B,    "clips/c3.mp4", 2.70, 1.0, 1.00, 1.10, 0.50, 0.55, "zblur"),
    (C + 5 * B,    C + 6 * B,    "clips/c1.mp4", 0.10, 1.0, 1.12, 1.00, 0.45, 0.45, "bwflick"),
    (C + 6 * B,    C + 7 * B,    "clips/c2.mp4", 0.30, 1.0, 1.00, 1.10, 0.55, 0.50, "smear"),
    (C + 7 * B,    tl.T_END,     "clips/c3.mp4", 3.00, 1.0, 1.05, 1.15, 0.50, 0.55, "whiteout"),
    # END CARD on the brand's dark (the type page draws logo, line, CTA and the cursor click)
    (tl.T_END,     tl.LEN,       "#0B0B0F",      0.0,  1.0, 1.00, 1.00, 0.50, 0.50, "card"),
]

cuts = fk.CutList(SHOTS, beats=tl.BEATS, beat_punch=0.07, downbeat_split=14, fx_from=C, fx_to=tl.T_END)
FOOT = fk.Finish(vignette=0.6, bloom=0.55, grain=6)                    # footage
UIF = fk.Finish(contrast=False, vignette=0, bloom=0, grain=2.5)        # UI pages and the end card: grain only
def V(u, fx, fy, w):   # a Reframe key in UI time that keeps w (a fraction of the page width) in view; below zoom 1 a blurred copy fills
    return (tl.ui2t(u), fx, fy, min(1.0, 0.5625 * tl.W / tl.H / w))
# 9:16, 1:1 and 4:5: the 16:9 UI seen through a moving crop. Focus points were measured on the rendered page (ui.html time)
REFRAME = [V(0.0, .50, .60, .85), V(0.9, .52, .50, .85), V(1.3, .22, .72, .34), V(1.7, .40, .40, .36), V(2.45, .42, .60, .36),
           V(2.7, .38, .50, .40), V(3.3, .32, .55, .36), V(3.8, .46, .45, .40), V(4.8, .46, .35, .40), V(5.1, .50, .42, .56),
           V(7.2, .40, .50, .62), V(8.6, .42, .55, .62), V(9.0, .58, .56, .40), V(9.7, .50, .50, .40), V(10.2, .50, .50, .62)]
_L = {}
def layers():
    """Load the rendered page frames on first use, so audio.py can import SHOTS before the pages exist."""
    if not _L:
        _L["PAGES"] = {
            "intro": fk.Overlay("frames/intro", start=tl.T_INTRO),             # render_html.py ui/intro.html --dur 4
            "ui":    fk.Overlay("frames/ui", start=tl.T_UI, speed=tl.UI_SP) if abs(tl.W / tl.H - 16 / 9) < 0.05 else
                     sk.Reframe("frames/ui", REFRAME, start=tl.T_UI, speed=tl.UI_SP),   # --dur 11.2 --w 1920 --h 1080 --scale 2
            "build": fk.Overlay("frames/build", start=tl.T_BUILD),             # --dur 4
        }
        _L["TOG"] = fk.Overlay("frames/toggle", start=tl.T_TOG)               # --dur (T_END - T_TOG)
        _L["TYPE"] = fk.Overlay("frames/type")                                # --dur LEN
    return _L

def render(t):
    L = layers(); PAGES, TOG, TYPE = L["PAGES"], L["TOG"], L["TYPE"]
    s = cuts.shots[cuts.index(t)]
    img = cuts.render(t)                                               # footage + camera + look tags + cut grammar
    if s.has("rush"): img = sk.rush(img, (t - s.start) / s.dur, s.fx, s.fy)
    page = (s.arg("page") or [None])[0]
    if page: img = PAGES[page].over(img, t, zoom=sk.punch_in(t, D, 0.06) if page == "ui" else 1.0)   # the drop punches the UI
    img = TOG.over(img, t)
    img = TYPE.over(img, t)
    img = fk.hits(img, t, tl.HITS)                                     # hits AFTER the type: they hit the text too
    img = sk.whip_at(img, t, [tl.T_BUILD])                             # whip out of the UI into the build
    img = (UIF if page or s.has("card") else FOOT)(img, fk.frame_of(t))
    if cuts.flash_now(t): img = fk.flash(img)
    return img

if __name__ == "__main__":
    fk.run(render, tl.LEN, tl.NAME)
