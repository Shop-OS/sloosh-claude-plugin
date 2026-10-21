"""tl.py: the ONE timeline. edit.py, audio.py and every HTML page (through tl.json) read these numbers, so cuts,
type slams, SFX and voice lines land on the same frames. Change a number once; everything follows.
Run `python3 tl.py` after any change (it writes tl.json for the HTML pages)."""
import json

NAME = "film"                     # REPLACE: <product>_<style>
W, H, FPS = 1080, 1920, 30        # 9:16 vertical feed. 16:9 -> 1920, 1080, 24 or 30. 1:1 -> 1080, 1080. 4:5 -> 1080, 1350
BPM = 130.0; B = 60.0 / BPM       # one beat
GENRE, KEY = "phonk", "F#m"       # genre and key for audiokit.score() (audio.py)

# ---- the story as beats (REPLACE with the film's own story; every section after the drop is whole beats from it)
T_HOOK   = 0.0                    # hook: something moves from frame 0, no logo
DROP     = 14 * B                 # the key moment (hero / gesture / logo slam) on a bar line
T_BREATH = DROP - 0.12            # 3-4 frames of black + silence before the drop
T_PAY    = DROP + 8 * B           # payoff section
T_END    = DROP + 12 * B          # end card
LEN      = T_END + 6 * B          # film length (end card holds >= 2.5 s)

# every beat, aligned so a bar line lands on the drop
BEATS = [DROP + k * B for k in range(-int(DROP / B), int((LEN - DROP) / B) + 1) if 0 <= DROP + k * B < LEN]

# ---- type cues (film seconds): lockups, slams, end card. The HTML type page reads these from tl.json.
TYPE = {
    "lockA_1": [2 * B, 6 * B],                 # [in, out] two-line stack
    "lockA_2": [T_PAY, T_PAY + 3 * B],
    "echo":    [DROP + 0.0, DROP + 4 * B - 0.25],  # echo stack on the drop (out before the first slam: words never overlap)
    "slams":   [DROP + 4 * B, DROP + 5 * B, DROP + 6 * B],
    "end":     [T_END, LEN],
}
# ---- the words (REPLACE: exact strings from the brief, approved by the user in the treatment). Max ~6 words per line.
COPY = {
    "lockA_1": ["YOUR", "HEADLINE."],          # line 1 white, line 2 accent
    "lockA_2": ["SECOND", "LINE."],
    "echo":    ["THE", "HERO"],                # small word above, hero word
    "slams":   ["ONE", "TWO", "THREE"],
    "end":     ["PRODUCT NAME", "TAGLINE · CALL TO ACTION"],
}
ACCENT, INK, RULE = "#F6C945", "#FFFFFF", "#E5262A"   # one accent colour; RULE only for the end-card rules

# ---- whole-frame hits that also hit the type: (time, kind, frames)
HITS = [(DROP + 4 * B, "negative", 2), (DROP + 6 * B, "red", 2)]
# ---- voice lines (optional): time -> (text, kind normal|shout|announcer). Needs a local TTS voice or a user VO file.
VO = {}

def dump(path="tl.json"):
    with open(path, "w") as f:
        json.dump({k: v for k, v in globals().items() if k.isupper()}, f, indent=1)

if __name__ == "__main__":
    dump(); print(f"{NAME}: {LEN:.2f} s at {BPM} BPM, drop {DROP:.2f} s, {len(BEATS)} beats -> tl.json")
