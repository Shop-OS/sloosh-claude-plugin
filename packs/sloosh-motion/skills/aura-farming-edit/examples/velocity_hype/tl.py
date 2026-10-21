"""tl.py: the ONE timeline for the default aura edit (the Velocity Hype preset). edit.py, audio.py and
ui/type.html (through tl.json) read these numbers, so cuts, type slams, hits, SFX and voice lines land on the same
frames. Change a number once; everything follows. Run `python3 tl.py` after any change (writes tl.json)."""
import json

NAME = "aura_velocity"            # REPLACE: <subject>_aura
W, H, FPS = 1080, 1920, 30        # 9:16 vertical (16:9: 1920, 1080, 24)
BPM = 130.0; B = 60.0 / BPM       # one beat = 0.4615 s, one bar = 1.846 s
GENRE, KEY = "phonk", "F#m"       # original drift phonk (Velocity Hype / Night Luxe / Night Drive). trap | techno for the others

# ---- the story as beats. Every section boundary after the drop is a whole number of beats from it.
DROP     = 16 * B                 # 7.385 s: the ONE gesture lands here, on a bar line (about 42% of the film)
T_ANN    = DROP - 4 * B           # 5.538 s: calm hold, eyes open, announcer line over the filtered tease
T_PSYCH  = DROP - 1 * B           # 6.923 s: tape-stop "psych": inverted strobe, colour split, darkening
T_BREATH = DROP - 0.12            # 3-4 frames of black + silence
T_FLICK  = DROP + 10 * B          # 12.000 s: the face-flicker burst (one beat, one face per frame)
T_CALM   = DROP + 11 * B          # 12.462 s: the calm-vs-chaos hold (the emotional centre)
T_END    = DROP + 16 * B          # 14.769 s: the lens-look ending + end card
LEN      = DROP + 22 * B          # 17.538 s
T_PAY    = DROP                   # (core name) the hyper section runs from the drop to the lens look

BEATS = [DROP + k * B for k in range(-int(DROP / B), int((LEN - DROP) / B) + 1) if 0 <= DROP + k * B < LEN]

# ---- type cues (film seconds). Each cue sits over a shot whose face is clear of the type (see edit.py SHOTS).
TYPE = {
    "lockA_1": [6 * B, 10 * B - 0.2],          # two-line stack, bottom-left, over the power walk
    "echo":    [DROP, DROP + 4 * B - 0.25],    # echo stack on the drop (out before the first slam)
    "slams":   [DROP + 4 * B, DROP + 5 * B],   # one word per beat, centred, over no-face shots
    "slam_out": DROP + 6 * B,
    "lockA_2": [T_CALM + 0.1, T_END - B],      # over the calm-vs-chaos hold
    "end":     [T_END, LEN],
}
COPY = {                                       # written from the brief, approved in the treatment. 1-2 words per line.
    "lockA_1": ["LIGHTS", "OUT."],
    "echo":    ["PURE", "AURA"],
    "slams":   ["FULL", "SEND."],
    "lockA_2": ["STAY", "QUIET."],
    "end":     ["NO. 07", "CALM IS THE FLEX"],
}
ACCENT, INK, RULE, SMEAR = "#F6C945", "#FFFFFF", "#E5262A", "#E5262A"   # one accent; red = end-card rules + slam smear
ECHO_Y, SLAM_Y = 0.495, 0.45                   # hero-word bottom / slam centre as a fraction of H (drop face sits above 0.28)

# ---- whole-frame hits, applied AFTER the type so they hit the words too: (time, kind, frames)
HITS = [(DROP, "white", 4), (DROP + 4 * B, "negative", 2), (DROP + 5 * B, "red", 2), (DROP + 8 * B, "threshold", 2)]

# ---- voice: a line on every lockup, slam and section turn. kind: normal | shout | announcer
VO = {
    0.30:              ("You were never loud.", "normal"),
    6 * B:             ("Lights out!", "shout"),
    T_ANN:             ("Aura... farming.", "announcer"),
    DROP + 0.05:       ("Pure aura!", "shout"),
    DROP + 4 * B:      ("Full send!", "shout"),
    T_CALM + 0.1:      ("Stay quiet.", "normal"),
    T_END + 0.35:      ("Number seven. Unbothered.", "announcer"),
}

def dump(path="tl.json"):
    with open(path, "w") as f:
        json.dump({k: v for k, v in globals().items() if k.isupper()}, f, indent=1)

if __name__ == "__main__":
    dump(); print(f"{NAME}: {LEN:.2f} s at {BPM} BPM, drop {DROP:.2f} s, {len(BEATS)} beats -> tl.json")
