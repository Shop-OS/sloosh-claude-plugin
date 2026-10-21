"""tl.py: UI Shape-Shifter -> Send Morph -> Wordmark (code only, 0 generations), 12 s, 16:9, 120 BPM.
One shape lives through six UI states (each does its micro-action), becomes a prompt bar, the send click radiates
rings, the bar collapses into a dark tile, the logo's eyes pop in, glance and blink, and the full wordmark grows out
of the tile with its eyes exactly over the tile's eyes. ui/morph.html draws it; ui/type.html adds the verbs + end line.
Run `python3 tl.py` after any change (writes tl.json)."""
import json

NAME = "send_morph"
W, H, FPS = 1920, 1080, 30
BPM = 120.0; B = 60.0 / BPM
GENRE, KEY = "house", "Am"

STATES  = [1 * B, 3 * B, 5 * B, 7 * B, 9 * B, 11 * B]   # morph starts: button, loader, player, toggle, chart, prompt bar
T_CLICK = 14 * B                                         # 7.0 s: send click -> rings
DROP    = 16 * B                                         # 8.0 s: the tile lands, the eyes pop in (the key moment)
T_BREATH = DROP                                          # no black breath in a code sting (kept for the core scripts)
T_GROW  = 18 * B                                         # 9.0 s: the wordmark grows out of the tile
T_END   = 20 * B                                         # 10.0 s: end line
LEN     = 24 * B                                         # 12.0 s
MORPH = {"states": STATES, "type": [5.75, 30], "cursor": [6.45, 6.95], "click": T_CLICK, "collapse": T_CLICK + 0.05,
         "tile": T_CLICK + 0.42, "icon": DROP, "glance": [DROP + 0.3, DROP + 0.6], "blink": DROP + 0.85,
         "grow": T_GROW, "settle": T_GROW + 0.8, "prompt": "a launch film for my brand", "button": "Get started",
         "track": "Morning Mix"}
BEATS = [k * B for k in range(int(LEN / B) + 1)]

TYPE = {
    "forms": [[s + 0.08, w] for s, w in zip(STATES, ["TAP.", "LOAD.", "PLAY.", "SWITCH.", "TRACK.", "PROMPT."])],
    "forms_out": T_CLICK - 0.1,
    "end": [T_END, LEN],
}
TYPE_POS = "under"                                       # verbs centred under the shape
FORM_LABEL = "STATE"
END_LOGO, END_Y = False, 0.61                            # morph.html lands the logo; the end text block starts at 61% of H
COPY = {"end": ["ONE SHAPE.", "EVERY STATE  ·  YOUR BRAND"]}
ACCENT, INK, RULE = "#F6C945", "#FFFFFF", "#E5262A"
SURFACE, BG = "#F2F2EE", "#0B0B0C"

HITS = [(T_CLICK, "negative", 2)]
VO = {}

def dump(path="tl.json"):
    json.dump({k: v for k, v in globals().items() if k.isupper()}, open(path, "w"), indent=1)

if __name__ == "__main__":
    dump(); print(f"{NAME}: {LEN:.2f} s at {BPM} BPM, drop {DROP:.2f} s, {len(BEATS)} beats -> tl.json")
