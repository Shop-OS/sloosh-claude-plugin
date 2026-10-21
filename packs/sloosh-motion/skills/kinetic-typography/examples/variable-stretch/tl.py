"""tl.py: VARIABLE STRETCH kinetic film (10 s, 120 BPM). Archivo axes only: squeeze-to-fill (wdth 62 -> 125), a per-letter
weight/width wave with skew snaps on beats, stretch-to-frame, then type-as-camera through the O into the acid block."""
import json

NAME = "kt_stretch"
PRESET, PAGE = "stretch", "kt_stretch"
W, H, FPS = 1080, 1920, 30
BPM = 120.0; B = 60.0 / BPM
GENRE, KEY = "techno", "Em"
SAFE = "reels"
DROP     = 14 * B                 # 7.0 s: through the counter into the acid block
T_BREATH = DROP - 0.1
T_END    = DROP
LEN      = 20 * B                 # 10.0 s
BEATS = [k * B for k in range(int(LEN / B) + 1)]

def S(id, move, a, b, beats=None, **o):
    return dict(id=id, move=move, t=[round(a, 4), round(b, 4)], beats=[round(x, 4) for x in (beats or [])], **o)

BLK, BONE, ACID = "#0D0D0D", "#EFEBE3", "#C6FF3D"
FIELDS = [(0.0, BLK, BONE, ACID, "cut"), (DROP, ACID, BLK, BLK, "cut")]
HAZES = []

TYPE = {"kt": [
    S("loud", "stretch", 0.0, 4 * B - 0.3, [0.5 * B, 1.5 * B], w0=62, w1=125, g0=300, g1=900, accent=[1], dur=0.9),
    S("flex", "wave", 4 * B, 8 * B - 0.3, [5 * B, 6 * B, 7 * B], ax={"wght": [150, 900], "wdth": [125, 62]}, freq=0.9, spread=0.8, size=300),
    S("tall", "frame", 8 * B, 11 * B, [8 * B], w0=62, w1=118, wght=900, accent=True),
    S("bold", "zoom", 11 * B, DROP + 0.9, [11 * B], dur=0.9, axes={"wght": 900, "wdth": 125}),
    S("end", "end", DROP + 0.3, LEN, size=130, y=0.4),
]}
COPY = {
    "loud": ["MAKE IT", "LOUD"],
    "flex": ["FLEX"],
    "tall": ["TALL"],
    "bold": ["BOLD"],
    "end":  ["YOUR BRAND", "TYPE THAT MOVES  ·  BRAND.COM"],
}
ACCENT, INK, RULE = ACID, BONE, BLK
HITS = [(8 * B, "negative", 2)]
PUNCH = [DROP, DROP + 2 * B]
GRAIN = 4.0
PLATE = None
VO = {}

def dump(path="tl.json"):
    json.dump({k: v for k, v in globals().items() if k.isupper() and not callable(v)}, open(path, "w"), indent=1)

if __name__ == "__main__":
    dump(); print(f"{NAME}: {LEN:.2f} s at {BPM} BPM, drop {DROP:.2f} s, {len(TYPE['kt'])} type scenes -> tl.json")
