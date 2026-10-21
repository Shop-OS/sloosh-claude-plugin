"""tl.py: Morph Chain (photoreal), 15 s, 9:16, 120 BPM. The ONE timeline: edit.py, audio.py and ui/type.html read it.
Story: hero -> a face/material morph run (wireframe, reptile, x-ray) -> breath -> DROP: outfit match-cuts every 0.25 s,
figure-locked -> a transition clip back to the hero -> SHAPE/SHIFT echo -> end card with the traced logo.
Run `python3 tl.py` after any change (writes tl.json)."""
import json

NAME = "morph_chain"
W, H, FPS = 1080, 1920, 30
BPM = 120.0; B = 60.0 / BPM            # one beat = 0.5 s, so a 0.25 s match cut = half a beat
GENRE, KEY = "trap", "F#m"

T_HOOK   = 0.0                         # hero still moves from frame 0 (handheld + push), no logo
T_RUN    = 2 * B                       # the morph run starts: k0->k1 transition clip
DROP     = 12 * B                      # 6.0 s: outfit match-cuts begin on a bar line
T_BREATH = DROP - 0.12                 # 4 frames of black + silence
T_BACK   = DROP + 4 * B                # 8.0 s: transition clip from the last outfit back to the hero
T_PAY    = DROP + 8 * B                # 10.0 s: SHAPE / SHIFT echo
T_END    = DROP + 12 * B               # 12.0 s: end card
LEN      = T_END + 6 * B               # 15.0 s

BEATS = [DROP + k * B for k in range(-int(DROP / B), int((LEN - DROP) / B) + 1) if 0 <= DROP + k * B < LEN]

# ---- type cues (film seconds). FORM = the state tag that rolls on each key landing (counter + one word).
TYPE = {
    "forms":   [[0.25, "ORIGINAL"], [2.5, "WIREFRAME"], [4.25, "REPTILE"], [5.25, "X-RAY"]],
    "forms_out": T_BREATH - 0.05,
    "lockA_1": [DROP + 0.05, T_BACK - 0.25],           # two-line stack over the match-cuts (bottom-left, clear of the face)
    "echo":    [T_PAY, T_END - 0.3],                    # SHAPE / SHIFT
    "end":     [T_END, LEN],
}
TYPE_POS = "bl"                                         # FORM tag bottom-left of the safe zone (tl | under for code films)
ECHO_POS = {"bottom": 0.56, "ghosts": 2, "step": 90}    # hero baseline at 56% of H: under the chin, over the torso (never the face)
COPY = {
    "lockA_1": ["ONE LOOK.", "EVERY FORM."],
    "echo":    ["SHAPE", "SHIFT"],
    "end":     ["NEW SEASON.", "YOUR BRAND  ·  SS27"],   # title may be "" when the logo carries the card
}
END_LOGO = True                                         # the type page draws ui/logo.json (traced from the real logo file)
ACCENT, INK, RULE = "#F6C945", "#FFFFFF", "#E5262A"

# ---- whole-frame hits that also hit the type: (time, kind, frames)
HITS = [(4.25, "duo", 2), (DROP, "white", 3), (DROP + 2 * B, "negative", 1), (T_PAY, "red", 2)]
# ---- morph landings (for SFX: shimmer peaks here) and the match-cut times (shutter ticks)
MORPHS = [2.35, 4.05, 5.2, 9.3, 10.0, 12.0]          # where each visible morph LANDS (read off the clip sheets)
MATCH  = [DROP + k * 0.25 for k in range(8)]
CLIP_STARTS = [1.0, 3.25, T_BACK]                     # where edit.py starts each transition clip (t1, t2, t3)
PRE_CUTS = [1.0, 2.5, 3.0, 3.25, 4.25, 4.75, 5.25]    # cuts before the drop (a whoosh leads into each)
VO = {}   # optional, e.g. {DROP: ("Every form.", "shout"), T_END + 0.4: ("Your brand. The new season.", "normal")}

def dump(path="tl.json"):
    json.dump({k: v for k, v in globals().items() if k.isupper()}, open(path, "w"), indent=1)

if __name__ == "__main__":
    dump(); print(f"{NAME}: {LEN:.2f} s at {BPM} BPM, drop {DROP:.2f} s, {len(BEATS)} beats -> tl.json")
