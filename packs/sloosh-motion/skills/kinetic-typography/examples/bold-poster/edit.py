"""edit.py: the compositor for a kinetic-typography film. A pure render(t): the same t, the same frame.

  python3 edit.py                          -> out/<NAME>_vN.mp4 (next free version; never overwrites)
  python3 edit.py out/sheet.jpg 0.5,2,6.4  -> stills only (a 12-16 still sheet covers every scene)

Layers, bottom to top (the same file works for every sub-preset; it reads tl.py):
  1. coded background: colour fields with beat-landed wipes + soft hazes (lib/ktfield.Fields), or the generated still plate (tl.PLATE),
     or the animated plate (tl.PLATE_CLIP: a generated video clip through the director CutList, slow push, no cut-out)
  2. type: the transparent PNG sequence of ui/<PAGE>.html (python3 lib/render_html.py ui/<PAGE>.html --dur <LEN> --out frames/<PAGE>)
  3. the plate's subject cut-out IN FRONT of the type (when tl.PLATE has a matte)
  4. composite punches + RGB split on bar downbeats (tl.PUNCH), zoom blur of type-as-camera scenes
  5. whole-frame hits that also hit the type (tl.HITS), then the finish (grain; no vignette on flat fields), flash frames
"""
import sys; sys.path.insert(0, "lib")
import filmkit as fk
import ktfield as kf
import tl

fk.setup(tl.W, tl.H, tl.FPS)
bg = kf.Fields(tl.FIELDS, getattr(tl, "HAZES", None))
plate = kf.Plate(**tl.PLATE) if getattr(tl, "PLATE", None) else None
PLATE_CLIP = getattr(tl, "PLATE_CLIP", None)            # animated plate: replaces Fields / the still plate for the whole film
cuts = fk.CutList([(0, tl.LEN, PLATE_CLIP, 0, 1, 1.0, 1.05, .5, .5, "hard")]) if PLATE_CLIP else None
TYPE = fk.Overlay("frames/" + tl.PAGE)                 # rendered from ui/<PAGE>.html
ZOOMS = kf.zooms(tl)
finish = fk.Finish(contrast=False, vignette=0.25 if (plate or cuts) else 0, bloom=0, grain=getattr(tl, "GRAIN", 4.0))

def render(t):
    if cuts: img = cuts.render(t)                         # animated plate (keep the type off the subject)
    else: img = plate.under(t) if plate and plate.on(t) else bg.render(t)
    img = TYPE.over(img, t)
    if not cuts and plate and plate.on(t): img = plate.front(img, t)     # type BEHIND the subject (still plate only)
    img = kf.camera_hits(img, t, getattr(tl, "PUNCH", []), ZOOMS)
    img = fk.hits(img, t, tl.HITS)
    img = finish(img, fk.frame_of(t))
    if kf.flash_now(t, ZOOMS, tl.FPS): img = fk.flash(img)
    return img

if __name__ == "__main__":
    fk.run(render, tl.LEN, tl.NAME)
