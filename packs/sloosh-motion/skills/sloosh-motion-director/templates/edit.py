"""edit.py: the film's ONE editor script. A pure render(t): the same t always gives the same frame.

  python3 edit.py                          -> out/<NAME>_vN.mp4 (next free version; never overwrites)
  python3 edit.py out/sheet.jpg 0.5,2,6.4  -> stills only, for fast checks (a 16-still sheet covers every section)
  FILMKIT_PLACEHOLDERS=1 python3 edit.py out/sheet.jpg   -> preview the cut with placeholder cards for missing shots

Layers, bottom to top:
  1. footage: the cut list (Sloosh stills and clips, or the user's own), with zoom paths, tags and the cut grammar
  2. type/UI: transparent PNG sequences rendered from ui/*.html by lib/render_html.py
  3. whole-frame hits that also hit the type, then the finish (contrast, vignette, bloom, grain), then flash frames
"""
import glob, os, sys; sys.path.insert(0, "lib")
import filmkit as fk
import tl

fk.setup(tl.W, tl.H, tl.FPS)
B, D = tl.B, tl.DROP

# ---- the cut list. REPLACE sources with the approved clips/stills and their clean windows.
# (start, end, source, in_point, speed, zoom_from, zoom_to, focus_x, focus_y, tags)
SHOTS = [
    (0.0,        2 * B,      "plates/hook.jpg",   0.0, 1.0, 1.00, 1.08, 0.5, 0.42, ""),          # hook: still + handheld
    (2 * B,      4 * B,      "clips/c1.mp4",      0.6, 1.0, 1.05, 1.00, 0.5, 0.45, "ramp"),
    (4 * B,      6 * B,      "clips/c2.mp4",      1.2, 1.0, 1.00, 1.06, 0.5, 0.40, ""),
    (6 * B,      8 * B,      "clips/c3.mp4",      0.4, 1.0, 1.10, 1.00, 0.5, 0.50, "smear"),
    (8 * B,      10 * B,     "plates/detail.jpg", 0.0, 1.0, 1.12, 1.00, 0.5, 0.50, "bwflick"),
    (10 * B,     12 * B,     "clips/c1.mp4",      2.0, 1.0, 1.00, 1.10, 0.5, 0.45, "glitch"),
    (12 * B,     tl.T_BREATH, "clips/c2.mp4",     2.6, 1.0, 1.00, 1.04, 0.5, 0.45, "ramp"),
    (tl.T_BREATH, D,          "black",             0.0, 1.0, 1.00, 1.00, 0.5, 0.50, "hard"),      # the breath
    (D,          D + 4 * B,  "clips/c3.mp4",      1.0, 0.6, 1.14, 1.00, 0.5, 0.45, "punch shake leak"),   # THE DROP
    (D + 4 * B,  D + 5 * B,  "clips/c1.mp4",      3.0, 1.0, 1.00, 1.05, 0.5, 0.45, "red"),
    (D + 5 * B,  D + 6 * B,  "plates/hook.jpg",   0.0, 1.0, 1.20, 1.05, 0.5, 0.40, "negative"),
    (D + 6 * B,  D + 7 * B,  "clips/c2.mp4",      3.4, 1.0, 1.00, 1.06, 0.5, 0.45, ""),
    (D + 7 * B,  D + 8 * B,  "plates/detail.jpg", 0.0, 1.0, 1.08, 1.00, 0.5, 0.50, "duo"),
    (D + 8 * B,  D + 10 * B, "clips/c3.mp4",      2.6, 1.0, 1.00, 1.08, 0.5, 0.45, "ramp"),
    (D + 10 * B, D + 12 * B, "clips/c1.mp4",      4.0, 1.0, 1.06, 1.00, 0.5, 0.45, "zblur"),
    (D + 12 * B, tl.LEN,     "plates/hook.jpg",   0.0, 1.0, 1.00, 1.05, 0.5, 0.42, ""),            # end card plate
]

if __name__ == "__main__":
    cuts = fk.CutList(SHOTS, beats=tl.BEATS, beat_punch=0.07, downbeat_split=14, fx_from=D, fx_to=tl.T_END)
    finish = fk.Finish(vignette=0.6, bloom=0.55, grain=6)          # grain 6 on footage; the type gets the same grain lightly
    # python3 lib/render_html.py ui/type.html --dur <LEN> --out frames/type   (until then the film renders without type)
    TYPE = fk.Overlay("frames/type") if glob.glob(os.path.join("frames", "type", "*.png")) else None

    def render(t):
        img = cuts.render(t)                   # footage + camera + look tags + cut grammar + leaks
        if TYPE is not None: img = TYPE.over(img, t)   # type on top of the picture
        img = fk.hits(img, t, tl.HITS)         # whole-frame hits that also hit the type
        img = finish(img, fk.frame_of(t))      # contrast, vignette, bloom, grain
        if cuts.flash_now(t): img = fk.flash(img)
        return img

    fk.run(render, tl.LEN, tl.NAME)
