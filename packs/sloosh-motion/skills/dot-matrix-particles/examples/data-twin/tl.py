"""tl.py: dot-matrix-particles default film "Data Twin" (15 s, 9:16, 128 BPM minimal techno). The ONE timeline:
edit.py, audio.py and ui/type.html (through tl.json) read these numbers. Run `python3 tl.py` after any change.
Story: the face switches on as an LED wall from the eyes -> real / ASCII / negative-LED strobe on 1/8 notes ->
3D point-cloud scan -> thermal reveal of the product -> the cloud implodes -> breath -> LIGHT BURST, every LED on (DROP)
-> product halftone dot-wave -> the real product (data twin -> real) -> LED board "MADE OF / LIGHT" -> the halftone
dots fly into the wordmark -> dot-grid end card."""
import json

NAME = "nova_dots"                # REPLACE: <brand>_dots
W, H, FPS = 1080, 1920, 30
BPM = 128.0; B = 60.0 / BPM       # one beat = 0.469 s; the strobe cuts on 1/8 notes (B / 2)
GENRE, KEY = "techno", "Am"       # minimal techno; slow luxury sub-presets: "ambient", 84 BPM

# ---- the story as beats
DROP     = 16 * B                 # 7.50 s: light burst, every LED on
T_BREATH = DROP - 0.12            # 4 frames of black + silence
T_ASM    = 24 * B                 # halftone dots start flying into the wordmark
T_END    = 27 * B                 # end card (the HTML wordmark has faded in over the particles)
LEN      = 32 * B                 # 15.0 s
BEATS = [DROP + k * B for k in range(-int(DROP / B), int((LEN - DROP) / B) + 1) if 0 <= DROP + k * B < LEN]
STROBE = [4 * B + k * B / 2 for k in range(6)]   # the twin-strobe cut times (edit.py `hard` rows, audio.py glitch hits)

# ---- type cues (film s). [in, out]
TYPE = {
    "label": [7 * B + 0.15, 11 * B - 0.2],     # two mono labels over the point cloud, gone before the thermal shot
    "led":   [22 * B, 24 * B],                 # LED board lockup (built in Python: dotskit.LEDText)
    "word":  [T_END - 0.45, LEN],              # HTML wordmark fades in ON the assembled particles
    "tag":   [T_END + 0.35, LEN],
}
COPY = {
    "label": ["SCAN 01 / SUBJECT", "POINT CLOUD"],   # only real, true words: never fake claims or numbers
    "led":   ["MADE OF", "LIGHT"],                   # <= 8 letters per line at cap 11 cells
    "word":  "NOVA",                                 # REPLACE: brand word (<= 6 letters at 220 px; longer auto-fits)
    "tag":   "EAU DE PARFUM",                        # REPLACE: <= 4 words
}
# Amber LED palette: one ink + its ramp (bg -> mid -> ink -> hot). Brand colour replaces INK; derive MID = ink x 0.3,
# HOT = ink lerped 70% to white.
PAL = {"BG": "#070403", "MID": "#5A1E0C", "INK": "#FFB45A", "HOT": "#FFF3DC", "ASCII": "#FFD9A8",
       "TONES": ["#070403", "#5A1E0C", "#FFB45A", "#FFF3DC"]}

# ---- dots transitions on cuts (cut time, kind, frames): halftone | dither
TRANS = [(20 * B, "halftone", 6), (22 * B, "dither", 5)]
# ---- whole-frame hits after the type (the director's fk.hits kinds): the drop flash only. Flashes <= 2 per film.
HITS = [(DROP, "white", 3)]
# ---- voice lines (optional): time -> (text, normal|shout|announcer)
VO = {}                           # e.g. {DROP + 2 * B: ("Made of light.", "normal")}

def dump(path="tl.json"):
    with open(path, "w") as fh:
        json.dump({k: v for k, v in globals().items() if k.isupper()}, fh, indent=1)

if __name__ == "__main__":
    dump(); print(f"{NAME}: {LEN:.2f} s at {BPM} BPM, drop {DROP:.2f} s, {len(BEATS)} beats -> tl.json")
