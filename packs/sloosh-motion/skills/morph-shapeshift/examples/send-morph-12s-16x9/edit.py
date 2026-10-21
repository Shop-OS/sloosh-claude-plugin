"""edit.py: UI Shape-Shifter -> Send Morph -> Wordmark (code only), 12 s 16:9. A pure render(t).

  python3 edit.py out/sheet.jpg 0.3,1.2,...   -> stills sheet          python3 edit.py -> out/send_morph_vN.mp4
Layers: background (BG colour, or swap the row's source for a plate) -> ui/morph.html frames -> ui/type.html frames ->
camera (slow push + a punch on the drop, on the whole composite) -> whole-frame hits -> finish (UI grain 2.5, no vignette).
Render the pages first:  python3 lib/render_html.py ui/morph.html --dur 12 --out frames/morph --jobs 1   (same for type)
"""
import sys; sys.path.insert(0, "lib")
import math
import filmkit as fk
import tl

fk.setup(tl.W, tl.H, tl.FPS)
D = tl.DROP
SHOTS = [(0.0, tl.LEN, tl.BG, 0.0, 1.0, 1.0, 1.0, 0.5, 0.5, "hard")]    # (start, end, source, in, speed, z0, z1, fx, fy, tags)
cuts = fk.CutList(SHOTS, grammar=False)
MORPH, TYPE = fk.Overlay("frames/morph"), fk.Overlay("frames/type")
finish = fk.Finish(vignette=0, bloom=0.35, grain=2.5)

def render(t):
    img = cuts.render(t)
    img = MORPH.over(img, t)
    img = TYPE.over(img, t)
    z = 1.0 + 0.035 * t / tl.LEN                                          # one slow push: nothing is ever frozen
    if t >= D: z *= 1 + 0.045 * math.exp(-(t - D) / 0.12)                 # punch as the tile lands and the eyes pop
    if t >= tl.T_CLICK: z *= 1 + 0.02 * math.exp(-(t - tl.T_CLICK) / 0.08)
    img = fk.camera(img, z, 0.5, 0.44)
    img = fk.hits(img, t, tl.HITS)
    return finish(img, fk.frame_of(t), vignette=False)

if __name__ == "__main__":
    fk.run(render, tl.LEN, tl.NAME)
