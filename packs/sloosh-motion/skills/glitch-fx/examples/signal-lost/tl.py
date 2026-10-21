"""tl.py: glitch-fx default film "Signal Lost" (15 s, 9:16, 128 BPM techno). The ONE timeline: edit.py, audio.py and
ui/type.html + ui/hud.html (through tl.json) read these numbers. Run `python3 tl.py` after any change.
Story: hook under the light -> x-ray scan -> tracking HUD -> corruption builds -> psych strobe + tape stop -> breath ->
DATAMOSH DROP -> NEW / BUILD / LIVE slams -> product hold -> wordmark slice-stamp."""
import json

NAME = "nova_glitch"              # REPLACE: <brand>_glitch
W, H, FPS = 1080, 1920, 30
BPM = 128.0; B = 60.0 / BPM       # one beat = 0.469 s; the 16th grid = B / 4 (every hit starts or ends on it)
GENRE, KEY = "techno", "Dm"
PRESET = "signal"                 # hit budget: layer | signal | hard  (glitchkit.BUDGETS)

# ---- the story as beats
DROP     = 16 * B                 # 7.50 s: the datamosh blooms, music drops
T_PSYCH  = DROP - B               # psych strobe (8 frames) + tape stop, then silence
T_BREATH = DROP - 0.12            # 4 frames of black (block-noise confetti on its last 2)
T_PAY    = DROP + 2 * B           # slams on the beat
T_END    = 26 * B                 # end card: wordmark slice-stamp
LEN      = 32 * B                 # 15.0 s
BEATS = [DROP + k * B for k in range(-int(DROP / B), int((LEN - DROP) / B) + 1) if 0 <= DROP + k * B < LEN]

# ---- type cues (film s). ui/type.html reads these. [in, out]
TYPE = {
    "stack":  [0.10, 4 * B],                    # SIGNAL / LOST, stutters in, hard-cut out on the wipe
    "label1": [4 * B + 0.10, 7 * B],            # mono label under the HUD
    "label2": [12 * B, T_PSYCH],                # typed while it builds
    "slams":  [T_PAY, T_PAY + B, T_PAY + 2 * B, T_PAY + 3 * B],   # 3 words; the last time is the out
    "end":    [T_END, LEN],
}
COPY = {
    "stack":  ["SIGNAL", "LOST"],               # line 1 ink, line 2 accent. <= 8 letters per line
    "label1": "[ 01 / TRACKING ]",
    "label2": "[ REBOOTING ]",
    "slams":  ["NEW", "BUILD", "LIVE"],
    "end":    ["NOVA", "BUILT FOR NOISE"],      # REPLACE: brand wordmark, tagline <= 4 words
}
ACCENT, INK, ALERT = "#39E6FF", "#F2F2EE", "#FF3A3A"   # ONE accent (brand colour replaces it); ALERT = REC dot + 1 HUD box in 5
FRINGE = ["#FF2850", "#28E6FF"]                         # chroma fringe (red / cyan), only in hits and the 3 px rest offset

# type-only tears (time, frames): the lockup's entrance tears on its own layer
TEARS = [(TYPE["stack"][0], 4), (TYPE["slams"][0], 2), (TYPE["slams"][1], 2), (TYPE["slams"][2], 2)]

# ---- the HUD (ui/hud.html): persistent REC frame 0 -> T_END, tracking boxes in windows. Boxes = [cx, cy, w, h] as
# fractions of the frame, placed on REAL features of the plate under them (open the approved still and measure).
# The example's boxes sit on a centred 9:16 subject; col() keeps them on it at 16:9, 1:1 and 4:5. Measured boxes skip col().
colk = min(1.0, H * 9 / 16 / W)
col = lambda bx: [round(0.5 + (bx[0] - 0.5) * colk, 4), bx[1], round(bx[2] * colk, 4), bx[3]]
HUD = {
    "frame": [0.0, T_END],
    "track": [
        {"t": [4 * B, 7 * B], "boxes": [col(b) for b in [[0.50, 0.46, 0.34, 0.16], [0.50, 0.565, 0.06, 0.04], [0.50, 0.63, 0.09, 0.12],
                                        [0.22, 0.80, 0.14, 0.07], [0.78, 0.78, 0.15, 0.08], [0.30, 0.30, 0.10, 0.06]]]},
        {"t": [10 * B, 12 * B], "boxes": [col(b) for b in [[0.445, 0.41, 0.06, 0.035], [0.555, 0.41, 0.06, 0.035], [0.50, 0.42, 0.34, 0.26]]]},
    ],
}

# ---- glitch transitions on cuts (cut time, kind, frames): linewipe | slicecut | blockcut | mosaic
TRANS = [(4 * B, "linewipe", 5), (10 * B, "slicecut", 4), (24 * B, "linewipe", 5)]

# ---- whole-frame hits AFTER the type (so the type tears with the frame): (time, kind, frames[, params])
GLITCH = [
    (2 * B,        "slices+rgb", 4),                  # cut into the x-ray scan
    (8 * B,        "blocks",     4),
    (11 * B,       "static",     3),                  # signal lost
    (T_PSYCH,      "psych",      8),                  # psych strobe: 2 flashes, zoom blur, split, darkening
    (DROP - 2 / FPS, "noise",    2),                  # signal breaking, ends on the drop
    (DROP,         "white",      2),                  # the drop flash
    (T_PAY + B,    "slices+rgb", 4),                  # BUILD
    (22 * B,       "strobe",    10),                  # invert x3 (every 2 frames)
    (T_END,        "slices+rgb", 4, {"amp": 0.14}),   # wordmark slice-stamp
    (T_END + 3 * B, "rgb",       3),                  # echo; the logo is never glitched again
]
HITS = []                          # core-format hits (negative / red / duo ...) if wanted; glitch uses GLITCH above

# ---- voice lines (optional): time -> (text, normal|shout|announcer)
VO = {}                            # e.g. {0.3: ("Signal... lost.", "announcer"), T_PAY: ("New build.", "shout")}

def dump(path="tl.json"):
    json.dump({k: v for k, v in globals().items() if k.isupper()}, open(path, "w"), indent=1)

if __name__ == "__main__":
    dump(); print(f"{NAME}: {LEN:.2f} s at {BPM} BPM, drop {DROP:.2f} s, {len(BEATS)} beats -> tl.json")
