"""tl.py: the ONE timeline for the default feature film "A becomes B" (12 s, 1:1, 30 fps, 120 BPM techno).
edit.py, audio.py and every ui/*.html page (through tl.json) read these numbers. Run `python3 tl.py` after any change.

Story: hook (AI: the pain, 3 short windows) -> rush into the screen -> NEW pill + feature name + benefit -> breath ->
DROP: the window springs in; the cursor clicks the feature; ONE thing becomes THREE (A becomes B) -> payoff (AI windows,
every beat effect on, one hype lockup) -> end card with CTA."""
import json

NAME = "example_feature"              # REPLACE: <brand>_feature
W, H, FPS = 1080, 1080, 30         # 1:1 feed post. 9:16 1080x1920, 16:9 1920x1080, 4:5 1080x1350 (pages lay out per format)
BPM = 120.0; B = 60.0 / BPM
GENRE, KEY = "techno", "Am"

T_HOOK   = 0.0
T_RUSH   = 2.5 * B                 # 1.25: push into the laptop screen -> white
T_NAME   = 4 * B                   # 2.0: NEW pill + feature name + benefit (ui/feature.html page time 0)
DROP     = 8 * B                   # 4.0: THE DROP. the window springs in (feature.html page time 2.0)
T_BREATH = DROP - 3.0 / FPS
T_UI     = DROP
T_PAY    = DROP + 9 * B            # 8.5: payoff, AI windows with every beat effect
T_END    = DROP + 12 * B           # 10.0: end card
LEN      = T_END + 4 * B           # 12.0
FEAT_NAT = T_PAY - T_NAME          # 6.5 s: render feature.html at exactly this length
def p2t(p): return T_NAME + p      # feature.html page time -> film time

BEATS = [DROP + k * B for k in range(-int(DROP / B), int((LEN - DROP) / B) + 1) if 0 <= DROP + k * B < LEN]

# ---- feature.html cues in PAGE time (the page reads them; audio.py converts with p2t). Clicks sit on beats.
FEAT_CUES = {
    "click":   [3.0, 4.0],                 # the feature's chip, then the option (film 5.0, 6.0)
    "pop":     [0.15, 3.05, 5.0, 5.25, 5.5],   # NEW pill, menu, a check on each new size
    "sparkle": [0.15, 4.1],                # NEW pill, A becomes B
    "whoosh":  [1.8, 4.08],                # the name exits, the cards split
    "shine":   0.8,                        # shine bar across the feature name
}
TYPE = {
    "lockA_1": [0.15, 1.15],               # the pain, over the hook
    "lockA_2": [T_PAY + 0.1, T_END - 0.2], # the payoff
    "end":     [T_END, LEN],
}
END_CLICK = T_END + 1.2
COPY = {
    "lockA_1": ["ONE POST.", "NINE SIZES."],
    "lockA_2": ["EVERY", "CHANNEL."],
    "end":     ["Example Studio", "Auto-Resize is live.", "Try it free", "example.com"],
    "feature": ["NEW", "Auto-Resize", "Every channel size, in one click."],
    "menu":    ["Feed · 1:1", "Story · 9:16", "Video · 16:9", "All channels"],
    "sizes":   ["1:1", "9:16", "16:9"],
    "toggle":  ["OFF", "AUTO", "RESIZE"],  # only for the Before/After sub-preset (ui/toggle.html)
}
ACCENT, ACCENT2, INK, RULE = "#FF6A3D", "#FFB547", "#FFFFFF", "#FF6A3D"
HITS = [(T_PAY, "negative", 2), (T_PAY + 2 * B, "red", 2)]
VO = {}
# VO = {0.15: ("One post. Nine sizes.", "normal"), T_NAME + 0.3: ("New. Auto-Resize.", "normal"), T_END + 0.2: ("Try it free.", "normal")}
# Before/After sub-preset only (ui/toggle.html over footage; see references/feature-announcement.md, Tiles): T_TOG = T_PAY - 2 * B; T_CLICK = T_PAY

def dump(path="tl.json"):
    json.dump({k: v for k, v in globals().items() if k.isupper()}, open(path, "w"), indent=1)

if __name__ == "__main__":
    dump(); print(f"{NAME}: {LEN:.2f} s at {BPM} BPM, drop {DROP:.2f} s, feature page {FEAT_NAT:.2f} s, {len(BEATS)} beats -> tl.json")
