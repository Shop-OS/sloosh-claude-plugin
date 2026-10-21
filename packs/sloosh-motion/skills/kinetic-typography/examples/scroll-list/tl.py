"""tl.py: SCROLL LIST kinetic film (9 s, 120 BPM). The "we make ___" device: a stem above a fixed band, rows glide through it one
per beat (band row ink, others dim), one suspense beat, the payoff decelerates long and turns accent; a mono ticker runs on top."""
import json

NAME = "kt_list"
PRESET, PAGE = "list", "kt_list"
W, H, FPS = 1080, 1920, 30
BPM = 120.0; B = 60.0 / BPM
GENRE, KEY = "house", "Gm"
SAFE = "reels"
DROP     = 10 * B                 # 5.0 s: the payoff row lands
T_BREATH = DROP - 0.1
T_END    = 14 * B
LEN      = 18 * B                 # 9.0 s
BEATS = [k * B for k in range(int(LEN / B) + 1)]

def S(id, move, a, b, beats=None, **o):
    return dict(id=id, move=move, t=[round(a, 4), round(b, 4)], beats=[round(x, 4) for x in (beats or [])], **o)

PAPER, INK_, COBALT = "#F2F1EC", "#141414", "#2F5BFF"
FIELDS = [(0.0, PAPER, INK_, COBALT, "cut"), (T_END, COBALT, PAPER, PAPER, "up")]
HAZES = []

TYPE = {"kt": [
    S("tick", "ticker", 0.0, LEN, y=0.085, size=34, speed=90, font="s"),
    S("list", "list", 0.3, T_END - 0.3, [2 * B, 3 * B, 4 * B, 5 * B, 6 * B, 7 * B, DROP], band=0.47, size=136, stemSize=96),
    S("end",  "end",  T_END, LEN, size=120, y=0.42),
]}
COPY = {
    "tick": ["YOUR STUDIO  ·  INDEPENDENT DESIGN  ·  EST. 2019"],
    "list": ["We design", "brands.", "packaging.", "websites.", "campaigns.", "type.", "films.", "worlds."],
    "end":  ["your studio", "STUDIO.COM"],
}
ACCENT, INK, RULE = COBALT, INK_, PAPER
HITS = []
PUNCH = [DROP]
GRAIN = 3.0
PLATE = None
VO = {}

def dump(path="tl.json"):
    json.dump({k: v for k, v in globals().items() if k.isupper() and not callable(v)}, open(path, "w"), indent=1)

if __name__ == "__main__":
    dump(); print(f"{NAME}: {LEN:.2f} s at {BPM} BPM, drop {DROP:.2f} s, {len(TYPE['kt'])} type scenes -> tl.json")
