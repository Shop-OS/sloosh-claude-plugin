"""tl.py: the ONE timeline for a product-reveal film. edit.py, audio.py and ui/*.html (through tl.json)
read these numbers. Default film: Dark Luxury Light-Sweep, 15 s, 9:16, 96 BPM.
Run `python3 tl.py` after any change (writes tl.json)."""
import json

NAME = "product_reveal"           # REPLACE: <brand>_reveal
W, H, FPS = 1080, 1920, 30        # frame size; scripts/setup_film.sh writes it from the format
BPM = 96.0; B = 60.0 / BPM        # 0.625 s beat
GENRE, KEY = "luxury", "Dm"       # Tech Launch: "techno", "F#m", 120 BPM
TYPE_FAMILY = "expanded"          # "expanded" (tech / premium launch) | "serif" (fragrance, jewellery)

# ---- the story on the grid (sections after the drop are whole beats from it)
T_HOOK   = 0.0                    # rim-lit hook macro, something moves from frame 0, no type
T_PUSH   = 3 * B                  # the hook push accelerates into the anchor (push-in match cut)
T_D1     = 4 * B                  # detail 1: identity anchor macro (+ spec counter)
T_D2     = 6 * B                  # detail 2: label / print macro
T_D3     = 7 * B                  # detail 3: material macro
T_ACT    = 8 * B                  # action clip (lid opening, part separating, liquid)
T_BUILD  = 10 * B                 # half-beat build, ramps into cuts
DROP     = 13 * B                 # HERO lands on a set (punch + leak)          8.125 s
T_BREATH = DROP - 0.5 * B         # black breath with one white strobe          7.81 s
T_RUN    = DROP + 2 * B           # feature run: a cut and a word on every beat 9.375 s
T_PACK   = DROP + 5 * B           # code packshot: real cutout, name passes BEHIND it   11.25 s
T_END    = DROP + 7 * B           # refined end card                            12.5 s
LEN      = DROP + 11 * B          # 15.0 s (end card holds 2.5 s)

BEATS = [DROP + k * B for k in range(-int(DROP / B), int((LEN - DROP) / B) + 1) if 0 <= DROP + k * B < LEN]

# ---- type cues (film seconds). ui/type.html (front type) and ui/packshot.html (type behind the product) read these.
TYPE = {
    "counter": [T_D1 + 0.12, T_D2 - 0.24],          # spec counter over the anchor macro; its 0.22 s wipe-out ends before the label cut
    "lockA":   [T_ACT, T_BUILD - 0.05],             # two-line stack over the action clip
    "slams":   [T_RUN, T_RUN + B],                  # feature words, one per beat
    "echo":    [T_RUN + 2 * B, T_PACK - 0.08],      # echo stack closes the run
    "name":    [T_PACK + 0.12, T_END - 0.05],       # name lockup passing BEHIND the product (packshot page)
    "end":     [T_END, LEN],                        # refined end card
}
COUNT_DUR = 0.75                                   # the counter counts up over this long (audio ticks follow it)
# ---- the words: TRUE facts only (pack, brief, brand site). Written in the treatment, approved once.
COPY = {
    "counter": ["50", "ML", "EAU DE PARFUM"],      # value, unit, label (value = a number printed on the pack)
    "lockA":   ["LIGHT,", "BOTTLED."],             # line 1 ink, line 2 accent
    "slams":   ["AMBER", "GLASS"],                 # materials / features from the brief
    "echo":    ["SOLID", "BRASS"],                 # small word above, hero word
    "name":    ["MAISON", "ÉCLAT"],                # brand line, product name (exact spelling from the pack)
    "end":     ["MAISON ÉCLAT", "Nº 1 · EAU DE PARFUM · 50 ML"],
}
INK, ACCENT, MUTE, RULE = "#F4EFE6", "#E2B65C", "#A79C8B", "#E2B65C"   # palette_from_photo.py -> ACCENT from the product
BASE, LIT = "#050505", "#2A241D"                   # end-card background lift
# ---- the packshot: where the REAL cutout stands. Measured from the approved hero still (<skill>/scripts/cutout.py --bbox),
# so the code product lands exactly where the AI product stood on the set. Units: px of a frame whose short side is 1080.
# end_bottom: the product's bottom on the end card (the wordmark sits 64 px under it). Defaults per format:
PACK = {"cx": 540, "bottom": 1330, "height": 940, "reflect": 0.20, "float": 8, "end_scale": 0.62, "end_bottom": 1040}   # 9:16
if W / H > 1.2:    PACK.update(cx=960, bottom=900, height=680, end_scale=0.6, end_bottom=720)                         # 16:9
elif W / H > 0.85: PACK.update(cx=540, bottom=900, height=680, end_scale=0.58, end_bottom=720)                        # 1:1
elif H / W < 1.6:  PACK.update(cx=540, bottom=1120, height=800, end_scale=0.6, end_bottom=900)                        # 4:5
# paste the PACK.update(...) line that cutout.py --bbox prints HERE, under these defaults

# ---- whole-frame hits that also hit the type: (time, kind, frames). Dark Luxury budget: 1 strobe, 2 warm flashes.
HITS = [(T_BREATH + 0.16, "white", 2), (T_RUN, "warm", 2), (T_RUN + 2 * B, "warm", 2)]
VO = {}                                            # e.g. {DROP + 0.1: ("Maison Éclat.", "normal")}

def dump(path="tl.json"):
    json.dump({k: v for k, v in globals().items() if k.isupper()}, open(path, "w"), indent=1, ensure_ascii=False)

if __name__ == "__main__":
    dump(); print(f"{NAME}: {LEN:.2f} s at {BPM} BPM, drop {DROP:.3f} s, {len(BEATS)} beats -> tl.json")
