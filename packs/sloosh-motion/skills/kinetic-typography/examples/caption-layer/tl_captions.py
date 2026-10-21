# ---- KINETIC CAPTION LAYER (kinetic-typography skill). Paste this block into a BASE film's tl.py, below COPY.
# Contract: captions live ONLY in TYPE["kt"] + COPY[<id>] (the director ui/type.html never reads them, so nothing clashes).
#   1. cp <kinetic-typography>/lib/{ktkit.js,kt.css,ktfield.py} lib/ ; cp <kinetic-typography>/examples/caption-layer/ui/kt_caption.html ui/
#      (fonts: new_film.sh already copied Archivo and Instrument Serif into fonts/; nothing is fetched)
#   2. python3 tl.py ; python3 lib/render_html.py ui/kt_caption.html --dur <LEN> --out frames/kt_caption --jobs 1
#   3. edit.py:  CAP = fk.Overlay("frames/kt_caption")   and in render(t), right after the director type layer:  img = CAP.over(img, t)
#      (before fk.hits, so whole-frame hits also hit the captions)
#   4. audio.py: import ktfield as kf ; for t0, n, g in kf.sfx_cues(tl, layer=True): place tick/impact/shutter (see SKILL.md, "Sound")
# Rules: captions sit in the 9:16 middle band (y 900-1260, left of the rail), never over a face, never in the same beats as a
# director lockup / echo / slam (start >= 1 beat after its out: lockups take 0.25 s to wipe out), max 3 words per row, holds +25% over footage. Word times = beats, or VO word timestamps - 0.05 s.
def _kt(id, move, a, b, beats=None, **o):
    return dict(id=id, move=move, t=[round(a, 4), round(b, 4)], beats=[round(x, 4) for x in (beats or [])], **o)

CAPTION_BOX = [0.11, 0.47, 0.84, 0.656]          # 9:16 middle band; 16:9 use [0.06, 0.62, 0.94, 0.9]
TYPE["kt"] = [
    _kt("cap1", "lyric", 7 * B, 10 * B - 1 / 30, [7 * B, 7.5 * B, 8 * B, 9 * B], box=CAPTION_BOX, size=150, inv=[3]),   # starts 1 beat after lockA_1 has wiped out
    _kt("cap2", "lyric", 10 * B, T_BREATH, [10 * B, 11 * B, 12 * B], box=CAPTION_BOX, size=150),
]
COPY.update({
    "cap1": ["THIS IS", "*your*", "^EDIT^"],
    "cap2": ["NO", "*more*", "TIMELINES"],
})
