"""tl.py: SWISS CLEAN kinetic film (16 s, 120 BPM, beat 0.5 s). Locked bone frame with two soft hazes, Inter Tight sentence case,
words landing on half-beats with a 4-frame accent flash, a split-flap stat board, a word swap, a kinetic grid and a list finale.
edit.py, audio.py and ui/kt_swiss.html all read this file (python3 tl.py writes tl.json)."""
import json

NAME = "kt_swiss"
PRESET, PAGE = "swiss", "kt_swiss"
W, H, FPS = 1080, 1920, 30
BPM = 120.0; B = 60.0 / BPM
GENRE, KEY = "house", "Dm"        # minimal pluck house; "ambient" for calmer brands
SAFE = "reels"
DROP     = 16 * B                 # 8.0 s: the grid wave (the one loud moment in a quiet film)
T_BREATH = DROP - 0.1
T_END    = 27 * B                 # 13.5 s
LEN      = 32 * B                 # 16.0 s (end card holds 2.5 s)
BEATS = [k * B for k in range(int(LEN / B) + 1)]

def S(id, move, a, b, beats=None, **o):
    return dict(id=id, move=move, t=[round(a, 4), round(b, 4)], beats=[round(x, 4) for x in (beats or [])], **o)

BONE, INK_, ACC = "#ECEBE4", "#161614", "#E2416B"
FLASH = ["#8E1446", "#A8661C", "#E2416B", "#7E9A12"]          # landing accents: wine, amber, raspberry, olive-lime (>= 3:1 on bone)
FIELDS = [(0.0, BONE, INK_, ACC, "cut"), (DROP, INK_, BONE, ACC, "iris"), (20 * B, BONE, INK_, ACC, "cut")]
HAZES = [(0.12, 0.08, 0.42, "#F1DCEA", 0.75), (0.95, 0.85, 0.45, "#E3E8B8", 0.7)]     # pink upper-left, lime lower-right

TYPE = {"kt": [
    S("hook",  "rise",  0.25, 5 * B, [0.25, 0.25 + 3 * B / 2], stagger=B / 2, swing=0, dur=0.45, size=132, align="left", y=0.38,
      kicker="@ YOURBRAND  ·  NEW", flash=FLASH),
    S("stat",  "flap",  5 * B, 9 * B, [], kicker="NOW OPEN", roll=0.4, step=0.06, size=150),
    S("swap",  "swap",  9.5 * B, DROP - 0.45, [9.6 * B, 12 * B], size=118, flash=ACC),     # old line holds 1.2 s, new line 1.4 s, gone before the iris
    S("grid",  "grid",  DROP, 20 * B, [DROP + 0.5 * B, DROP + 1.5 * B, DROP + 2 * B], rows=10, cols=2, font="s"),   # hero grows after the last wave
    S("list",  "list",  20 * B + 0.1, T_END - 0.3, [20.5 * B, 21.5 * B, 22.5 * B, 23.5 * B, 25 * B], band=0.42, size=128, stemSize=72, stemFont="s"),
    S("end",   "end",   T_END, LEN, size=120, track=[0.5, 0.12]),
]}
COPY = {
    "hook": ["One clear idea.", "Made *really* well."],          # placeholder copy: REPLACE all of it from the brief
    "stat": ["SPRING 27", "NEW COLLECTION  ·  OUT NOW"],
    "swap": ["Made for one season.", "Made to last for years."],
    "grid": ["brand / new"],
    "list": ["FOR", "work.", "travel.", "weekends.", "every day.", "you."],
    "end":  ["Your Brand", "BRAND.COM  ·  NOW OPEN"],
}
ACCENT, INK, RULE = ACC, INK_, ACC
HITS = []                          # Swiss stays clean: no negatives; one punch on the grid
PUNCH = [DROP]
GRAIN = 3.0
PLATE = None
VO = {}

def dump(path="tl.json"):
    json.dump({k: v for k, v in globals().items() if k.isupper() and not callable(v)}, open(path, "w"), indent=1)

if __name__ == "__main__":
    dump(); print(f"{NAME}: {LEN:.2f} s at {BPM} BPM, drop {DROP:.2f} s, {len(TYPE['kt'])} type scenes -> tl.json")
