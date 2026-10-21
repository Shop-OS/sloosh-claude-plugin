"""tl.py: EDITORIAL SERIF kinetic film (12 s, 90 BPM, beat 0.667 s). Fraunces display with an italic accent phrase, masked word
rises with a 3 degree swing, a variable-axis "ink swell", a strike and a marker, tracked sign-off.
USE_PLATE = True puts one approved generated still behind the masthead, with the subject cut-out IN FRONT of the type
(plates/plate.jpg + plates/plate_matte.png from scripts/cutout.py; scripts/make_placeholders.py makes test stand-ins)."""
import json

NAME = "kt_editorial"
PRESET, PAGE = "editorial", "kt_editorial"
W, H, FPS = 1080, 1920, 30
BPM = 90.0; B = 60.0 / BPM
GENRE, KEY = "luxury", "Cm"        # KEY must be one of the director audiokit keys
SAFE = "reels"
DROP     = 6 * B                  # 4.0 s: the turn (strike)
T_BREATH = DROP - 0.1
T_END    = 13 * B                 # 8.67 s
LEN      = 18 * B                 # 12.0 s
BEATS = [k * B for k in range(int(LEN / B) + 1)]
USE_PLATE = False                 # True: masthead behind the subject (optional AI backplate, still-first rules)

def S(id, move, a, b, beats=None, **o):
    return dict(id=id, move=move, t=[round(a, 4), round(b, 4)], beats=[round(x, 4) for x in (beats or [])], **o)

PAPER, INK_, ACC = "#F4EFE6", "#1B1712", "#9A3B26"
if USE_PLATE:
    PLATE = dict(path="plates/plate.jpg", matte="plates/plate_matte.png", t=[0.0, DROP], z=[1.0, 1.06], focus=[0.5, 0.4], look="dim")
    FIELDS = [(0.0, INK_, PAPER, "#E9B08A", "cut"), (DROP, PAPER, INK_, ACC, "up")]
    HOOK = dict(y=0.0, box=[0.07, 0.06, 0.93, 0.27], noRail=True, fill=True)   # band ends above the head top (30%): the head tucks under, never over a word   # masthead spans the top band; the head tucks over its last line
else:
    PLATE = None
    FIELDS = [(0.0, PAPER, INK_, ACC, "cut")]
    HOOK = dict(y=0.35)
HAZES = []

TYPE = {"kt": [
    S("hook", "rise", 0.3, DROP - 0.45, [0.3, 0.3 + 1.5 * B], kicker="CHAPTER 01  —  SS27", size=200, max=320,
      swell=[(1, 0, 1.5 * B + 0.9, {"wght": 380, "SOFT": 0}, {"wght": 760, "SOFT": 100}, 1.4)], **HOOK),
    S("turn", "rise", DROP, T_END - 0.1, [DROP, DROP + 3 * B], size=150, y=0.4, strike=[(0, 3, DROP + 1.5 * B)], marker=[(1, 2, DROP + 4.2 * B)]),
    S("end",  "end",  T_END, LEN, size=104, font="d", track=[0.6, 0.16], dur=1.8),
]}
COPY = {
    "hook": ["Made for", "*real* life."],
    "turn": ["Not for a season.", "For a *lifetime.*"],
    "end":  ["Your Brand", "BRAND.COM"],
}
ACCENT, INK, RULE = ACC, INK_, ACC
HITS = []
PUNCH = []
GRAIN = 3.0
VO = {}

def dump(path="tl.json"):
    json.dump({k: v for k, v in globals().items() if k.isupper() and not callable(v)}, open(path, "w"), indent=1)

if __name__ == "__main__":
    dump(); print(f"{NAME}: {LEN:.2f} s at {BPM} BPM, drop {DROP:.2f} s, {len(TYPE['kt'])} type scenes -> tl.json")
