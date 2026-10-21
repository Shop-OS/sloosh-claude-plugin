"""tl.py: the ONE timeline for the default SaaS film "UI Walkthrough" (30 s, 16:9, 24 fps, 120 BPM house).
edit.py, audio.py and every ui/*.html page (through tl.json) read these numbers, so cuts, clicks, pops, type and
voice land on the same frames. Change a number once; everything follows. Run `python3 tl.py` after any change.

Story: hook (AI: the problem at a desk) -> rush into the screen -> gradient intro ("intro·ducing") -> breath ->
DROP: the product window springs in -> UI walkthrough (11 s of real UI, rebuilt in HTML) -> results build
(thermal reveal, build steps, cascade of posts) -> BEFORE (flat footage + OFF toggle) -> click: AFTER (every beat
effect on) -> end card."""
import json

NAME = "example_saas"                # REPLACE: <brand>_saas
W, H, FPS = 1920, 1080, 24        # 16:9 master. 9:16 1080x1920, 1:1 1080x1080, 4:5 1080x1350 (see SKILL.md, "Other sizes")
BPM = 120.0; B = 60.0 / BPM       # one beat = 0.5 s
GENRE, KEY = "house", "Am"

# ---- the story as beats (every boundary after the drop is a whole number of beats from it)
T_HOOK   = 0.0                    # AI: desk -> phone -> desk push (problem lockups)
T_RUSH   = 5 * B                  # 2.5: rush into the laptop screen (zoom 1 -> 1.9, zoom blur, to white)
T_INTRO  = 6 * B                  # 3.0: gradient intro page (ui/intro.html, natural 4.0 s)
DROP     = 14 * B                 # 7.0: THE DROP. the product window springs in (ui/ui.html)
T_BREATH = DROP - 3.0 / FPS       # 3 frames of black + silence before the drop
T_UI     = DROP
UI_NAT   = 11.2                   # ui.html's natural length (render it at this length, never cut it)
T_BUILD  = DROP + 22 * B          # 18.0: results build (ui/build.html, natural 4.0 s)
UI_SP    = UI_NAT / (T_BUILD - T_UI)   # 1.018: the UI plays 1.8% faster so it lands on the grid
T_TOG    = T_BUILD + 8 * B        # 22.0: BEFORE: flat footage, OFF toggle centred (ui/toggle.html)
T_CLICK  = T_TOG + 2 * B          # 23.0: the click. ON switches the footage on this exact frame (drop 2)
T_END    = T_CLICK + 8 * B        # 27.0: end card
LEN      = T_END + 6 * B          # 30.0
def ui2t(u): return T_UI + u / UI_SP          # UI time -> film time (SFX for clicks land on their click frames)

BEATS = [DROP + k * B for k in range(-int(DROP / B), int((LEN - DROP) / B) + 1) if 0 <= DROP + k * B < LEN]

# ---- UI cues in UI time (ui.html reads them for its clicks; audio.py converts them with ui2t)
UI_CUES = {
    "click":   [1.62, 2.25, 3.30, 4.15, 9.10],      # account chip, Settings, Integrations, Connect, Send
    "pop":     [1.68, 5.35, 6.45, 6.75, 9.62],      # menu, chip, photo 1 lands, photo 2 lands, logo tile
    "sparkle": [4.18, 10.0],                        # Connect -> Connected, wordmark grows out of the tile
    "whoosh":  [1.00, 2.45, 4.80, 5.95, 8.80],      # dive to chip, whip to settings, whip back, card drop, to send
    "type":    [7.45, 40.0],                        # typing starts at 7.45 s, 40 characters per second
}
BUILD_CUES = {"thermal": 0.25, "steps": [1.75, 2.10, 2.45], "cascade": 2.60}   # build.html time (starts at T_BUILD)

# ---- type cues (film seconds) and the exact words (written from the brief, approved in the treatment)
TYPE = {
    "lockA_1": [0.25, 1.15],              # hype stack over the desk
    "lockA_2": [1.30, 2.35],              # over the phone
    "echo":    [T_CLICK + 2 * B, T_CLICK + 5 * B - 0.25],     # 24.0: after the toggle has shrunk to its badge
    "slams":   [T_CLICK + 5 * B, T_CLICK + 6 * B],            # 25.5, 26.0
    "end":     [T_END, LEN],
}
END_CLICK = T_END + 1.55                  # the cursor clicks the CTA on the end card (type.html reads it; audio.py clicks)
COPY = {
    "lockA_1": ["40 POSTS.", "BY FRIDAY."],
    "lockA_2": ["ZERO", "DESIGNERS."],
    "echo":    ["40 POSTS", "DONE."],
    "slams":   ["BEFORE", "LUNCH."],
    "end":     ["Example Studio", "Your creative team, in one app.", "Start free", "example.com"],
    # pages
    "intro":   ["Imagine a whole", "creative team", "in one app", "intro·ducing"],   # editorial line, bracket words, split word
    "prompt":  "Launch posts for our new sneaker, rainy city at dusk",
    "steps":   ["Shooting product scenes", "Writing on-brand captions", "Sizing every channel"],
    "toggle":  ["OFF", "STUDIO", "MODE"],
}
ACCENT, ACCENT2, INK, RULE = "#FF6A3D", "#FFB547", "#FFFFFF", "#FF6A3D"   # one accent (+ its lighter gradient end)

# ---- whole-frame hits that also hit the type: (time, kind, frames)
HITS = [(T_CLICK, "negative", 2), (T_CLICK + 4 * B, "red", 2), (T_CLICK + 7 * B, "negative", 1)]
# ---- voice lines (optional, "Score + voice-over"): time -> (text, kind normal|shout|announcer)
VO = {}
# VO = {0.25: ("Forty posts. By Friday.", "normal"), T_CLICK + 2 * B: ("Done.", "shout"),
#       T_END + 0.2: ("Example Studio. Your creative team, in one app.", "normal")}

def dump(path="tl.json"):
    json.dump({k: v for k, v in globals().items() if k.isupper()}, open(path, "w"), indent=1)

if __name__ == "__main__":
    dump(); print(f"{NAME}: {LEN:.2f} s at {BPM} BPM, drop {DROP:.2f} s, UI x{1 / UI_SP:.3f}, {len(BEATS)} beats -> tl.json")
