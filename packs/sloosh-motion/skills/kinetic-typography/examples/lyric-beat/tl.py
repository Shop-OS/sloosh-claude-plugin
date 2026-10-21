"""tl.py: LYRIC / BEAT kinetic film (10.3 s, 140 BPM, beat 0.429 s). A word on every beat: condensed caps slam, *serif italic*
breath words, ^accent^ words, per-word inversions on beats, an accent-block drop with an echo stack whose fill walks down.
With a user's track: BPM and DROP come from the director scripts/beatmap.py; word beats from VO / lyric timestamps minus 0.05 s."""
import json

NAME = "kt_lyric"
PRESET, PAGE = "lyric", "kt_lyric"
W, H, FPS = 1080, 1920, 30
BPM = 140.0; B = 60.0 / BPM
GENRE, KEY = "trap", "F#m"
SAFE = "reels"
DROP     = 16 * B                 # 6.86 s: the title word on the accent block
T_BREATH = DROP - 0.12
T_END    = 20 * B
LEN      = 24 * B                 # 10.29 s
BEATS = [k * B for k in range(int(LEN / B) + 1)]

def S(id, move, a, b, beats=None, **o):
    return dict(id=id, move=move, t=[round(a, 4), round(b, 4)], beats=[round(x, 4) for x in (beats or [])], **o)

def on(k0, n): return [k * B for k in range(k0, k0 + n)]            # n consecutive beats from beat k0

OFF, BONE, RED = "#0E0D0C", "#F1ECE2", "#E0322A"
FIELDS = [(0.0, OFF, BONE, RED, "cut"), (T_BREATH, "#000000", "#000000", "#000000", "cut"), (DROP, RED, OFF, BONE, "cut"), (T_END, OFF, BONE, RED, "cut")]
HAZES = []

TYPE = {"kt": [
    S("idx", "flap", 0.0, DROP - 0.2, [], size=34, roll=0.2, step=0.03, box=[0.11, 0.115, 0.6, 0.15], noRail=True),
    S("p1", "lyric", 0.0, 4 * B - 1 / 30, on(0, 4), size=210),
    S("p2", "lyric", 4 * B, 8 * B - 1 / 30, on(4, 4), size=210, inv=[1]),
    S("p3", "lyric", 8 * B, 12 * B - 1 / 30, on(8, 4), size=210, inv=[3]),
    S("p4", "lyric", 12 * B, T_BREATH, on(12, 4), size=230),
    S("drop", "echo", DROP, T_END - 0.3, [DROP, DROP + B, DROP + 2 * B, DROP + 3 * B], walk=3, n=3, size=280, y=0.32),
    S("end", "end", T_END, LEN, size=110),
]}
COPY = {
    "idx": ["01 / 04  ARTIST NAME"],
    "p1": ["WE DON'T", "*chase*", "NOISE"],
    "p2": ["WE ^BECOME^", "*the*", "SIGNAL"],
    "p3": ["NO SLEEP", "*no*", "^SIGNAL^ LOST"],
    "p4": ["TURN IT", "*all*", "UP"],
    "drop": ["PURE", "SIGNAL"],
    "end": ["ARTIST NAME", "NEW SINGLE  ·  OUT FRIDAY"],
}
ACCENT, INK, RULE = RED, BONE, RED
HITS = [(4 * B, "negative", 2), (8 * B, "negative", 2), (DROP, "white", 3)]
PUNCH = [DROP + k * 2 * B for k in range(2)]
GRAIN = 5.0
PLATE = None
VO = {}

def dump(path="tl.json"):
    json.dump({k: v for k, v in globals().items() if k.isupper() and not callable(v)}, open(path, "w"), indent=1)

if __name__ == "__main__":
    dump(); print(f"{NAME}: {LEN:.2f} s at {BPM} BPM, drop {DROP:.2f} s, {len(TYPE['kt'])} type scenes -> tl.json")
