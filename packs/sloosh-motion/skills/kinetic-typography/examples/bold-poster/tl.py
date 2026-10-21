"""tl.py: the ONE timeline for a kinetic-typography film. edit.py, audio.py and the type page
(ui/kt_poster.html, through tl.json) all read these numbers, so every word, field wipe, hit and SFX lands on the same frame.
Run `python3 tl.py` after any change. BOLD POSTER default film: 15 s, 120 BPM (beat 0.5 s, bar 2 s), a new field every bar."""
import json

NAME = "kt_poster"                # REPLACE: <brand>_kt
PRESET, PAGE = "poster", "kt_poster"
W, H, FPS = 1080, 1920, 30
BPM = 120.0; B = 60.0 / BPM
GENRE, KEY = "house", "Am"        # punchy four-on-the-floor; "techno" for darker brands
SAFE = "reels"                    # reels = director safe zone + right rail; "poster" for ads without platform UI

DROP     = 16 * B                 # 8.0 s: the counter of NOW opens and the camera flies through it
T_BREATH = DROP - 0.1             # 3 frames of silence in the score (the picture keeps zooming)
T_END    = 24 * B                 # 12.0 s end card
LEN      = 30 * B                 # 15.0 s (end card holds 3 s)
BEATS = [k * B for k in range(int(LEN / B) + 1)]

def S(id, move, a, b, beats=None, **o):        # one scene: id (COPY key), move, [in, out], landing beats, options
    return dict(id=id, move=move, t=[round(a, 4), round(b, 4)], beats=[round(x, 4) for x in (beats or [])], **o)

# ---- colour fields drawn by edit.py (ktfield.Fields): (t, bg, ink, accent, how). The field is fully in at t (wipes land on the beat).
PAPER, INK_, ACC = "#F3EEE4", "#121212", "#FF4A1C"
FIELDS = [
    (0.0,      PAPER, INK_, ACC,   "cut"),
    (4 * B,    ACC,   INK_, PAPER, "up"),      # stat block wipes up on bar 2
    (8 * B,    INK_,  PAPER, ACC,  "left"),    # stretch on ink
    (12 * B,   PAPER, INK_, ACC,   "down"),    # urgency slams on paper
    (DROP,     ACC,   INK_, PAPER, "cut"),     # seen first through the counter of NOW, then full frame
    (20 * B,   INK_,  PAPER, ACC,  "cut"),     # stretch-to-frame on ink (hard cut on the bar)
    (T_END,    PAPER, INK_, ACC,   "right"),   # end card
]
HAZES = []                                     # e.g. [(0.15, 0.1, 0.5, "#F1DCEA", 0.5)] for Swiss-style soft hazes

# ---- the type film: one scene per move, every landing on a beat (TYPE["kt"] is what the page renders)
TYPE = {"kt": [
    S("tick",  "ticker", 0.0, LEN, size=60, speed=150, gaps=[(DROP, 20 * B)]),   # y defaults by format (9:16 0.74, 16:9 0.885)   # steps aside for the grid
    S("hook",  "stack",  0.0, 4 * B, [0.5 * B, 1.5 * B, 2.5 * B], kicker="DROP 04  ·  SS27", accent=[1], max=400,
      inv=[(3 * B, 2, -1, 0.25)]),                                       # DROP inverts on beat 3
    S("stat",  "count",  4 * B, 8 * B, [4.5 * B], kicker="ALL WEEKEND", dur=0.9),
    S("every", "stretch", 8 * B, 11.5 * B, [8.5 * B, 9.5 * B], accent=[1]),
    S("ends",  "slam",   12 * B, 15 * B, [12 * B, 13 * B, 14 * B], accent=[2], inv=[1], exit="cut"),
    S("now",   "zoom",   15 * B, DROP + 1.0, [15 * B], dur=1.0, accent=False),    # lands on beat 15, flies through from the drop
    S("grid",  "grid",   DROP, 20 * B, [DROP + 2 * B, DROP + 3 * B, DROP + 3.5 * B], rows=9, cols=3, z=5),
    S("sale",  "frame",  20 * B, 23.5 * B, [20 * B], accent=True),
    S("end",   "end",    T_END, LEN, size=110),
]}
# ---- the words (exact strings; written from the brief, approved in the treatment). REPLACE all of them.
COPY = {
    "tick":  ["NEW SEASON DROP — 40% OFF EVERYTHING — ENDS SUNDAY"],   # placeholder offer: REPLACE with the real one
    "hook":  ["NEW", "SEASON", "DROP"],
    "stat":  ["40%", "OFF EVERYTHING"],
    "every": ["EVERY", "THING"],
    "ends":  ["ENDS", "THIS", "SUNDAY"],
    "now":   ["NOW"],
    "grid":  ["DROP 04"],
    "sale":  ["SALE"],
    "end":   ["YOUR BRAND", "BRAND.COM  ·  ENDS SUNDAY"],
}
ACCENT, INK, RULE = ACC, INK_, ACC

# ---- whole-frame hits that also hit the type (filmkit.hits): (time, kind, frames)
HITS = [(20 * B, "negative", 2), (DROP + 2 * B, "duo", 2)]
PUNCH = [DROP + k * 2 * B for k in range(4)] + [T_END]     # composite punch + RGB split on bar downbeats after the drop
GRAIN = 4.0                                              # luminance grain on flat fields (no banding)
PLATE = None                                             # optional generated backplate: dict(path, matte, t, z, focus, look) (SKILL.md, "Optional plate")
PLATE_CLIP = None                                        # optional animated plate: e.g. "clips/plate.mp4" (SKILL.md, "Optional plate"); overrides FIELDS / PLATE
VO = {}                                                  # optional, only if the user asks: {time: (text, "shout")}

def dump(path="tl.json"):
    json.dump({k: v for k, v in globals().items() if k.isupper() and not callable(v)}, open(path, "w"), indent=1)

if __name__ == "__main__":
    dump(); print(f"{NAME}: {LEN:.2f} s at {BPM} BPM, drop {DROP:.2f} s, {len(TYPE['kt'])} type scenes -> tl.json")
