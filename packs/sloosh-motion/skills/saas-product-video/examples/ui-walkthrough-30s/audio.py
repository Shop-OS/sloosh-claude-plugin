"""audio.py: original score, SFX and optional voice-over on the SAME timeline as the picture.

  python3 audio.py                     -> out/audio.wav (mastered -14 LUFS / -2 dBTP) + RMS per 2 s
  python3 audio.py out/example_saas_v1.mp4 -> also muxes out/example_saas_v1_final.mp4 (< 30 MB)
Arrangement (follows the picture): filtered house intro under the hook and the gradient intro, a riser and the breath,
DROP 1 when the product window springs in, the groove LOW-PASSED under the UI walkthrough so every click reads, open
again for the dark results build, deliberately flat (500 Hz) under BEFORE, DROP 2 on the toggle click, a tail on the
end card. SFX from the shared cue lists: a click per click, a pop per card/chip/tile, a sparkle on connect and on the
logo, a tick per typed letter, whooshes on whips. The agent cannot hear: read the RMS report, then ask the user to listen.
"""
import subprocess, sys
sys.path.insert(0, "lib")
import numpy as np
import audiokit as ak
import tl
from edit import SHOTS

USER_TRACK, USER_DROP = None, None          # a user's own track: its drop lands on tl.DROP (beatmap.py finds USER_DROP)
MAX_MB = 30.0                               # delivery size cap for the final file
L, D, B, C, FPS = tl.LEN, tl.DROP, tl.B, tl.T_CLICK, tl.FPS
ui = tl.ui2t

# ---- 1. music
if USER_TRACK:
    tmp = "audio/_track.wav"; start = max(0.0, USER_DROP - D)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{start:.3f}", "-i", USER_TRACK, "-t", f"{L:.3f}", "-ar", str(ak.SR), "-ac", "2", tmp], check=True)
    from scipy.io import wavfile
    music = wavfile.read(tmp)[1].astype(np.float32) / 32768.0; music = np.pad(music, ((0, max(0, int(L * ak.SR) - len(music))), (0, 0)))
else:
    music = ak.score(tl.GENRE, tl.BPM, L, D, tl.KEY, breath=D - tl.T_BREATH)
music = ak.gap(music, tl.T_BREATH, D)                                  # the breath
music = ak.lowpass_region(music, D + 0.6, tl.T_BUILD, 1400, 0.6)       # under the UI: clicks must read
music = ak.lowpass_region(music, tl.T_TOG, C - 2.0 / FPS, 500, 0.45)   # BEFORE: deliberately flat
music = ak.gap(music, C - 2.0 / FPS, C)                                # a 2-frame breath before drop 2

# ---- 2. SFX from the shared cue lists (each peak sits on its frame)
sfx = ak.bus(L)
cuts = sorted({round(s[0], 3) for s in SHOTS if 0.05 < s[0] < tl.T_RUSH})
for c in cuts: ak.place(sfx, c - 0.22, ak.whoosh(0.3), -18)           # hook cuts
ak.place(sfx, tl.T_RUSH, ak.riser(tl.T_INTRO - tl.T_RUSH), -10)        # rush into the screen
ak.place(sfx, tl.T_INTRO, ak.impact(1.2), -16)                         # the white flash
for i in range(5): ak.place(sfx, tl.T_INTRO + 0.12 + i * 0.13, ak.tick(20 + i), -20)          # intro words blur in
for i in range(3): ak.place(sfx, tl.T_INTRO + 1.75 + i * 0.2, ak.pop(700 + 120 * i), -16)     # bracket words land
ak.place(sfx, tl.T_INTRO + 2.95 - 0.2, ak.whoosh(0.35), -14)                                   # intro·ducing splits
for k in range(8): ak.place(sfx, tl.T_INTRO + 3.0 + k * 2.0 / FPS, ak.shutter(), -24)         # thumbnails flicker
U = tl.UI_CUES                                                          # UI walkthrough (UI time -> film time)
for u in U["click"]: ak.place(sfx, ui(u), ak.click(), -8)
for u in U["pop"]: ak.place(sfx, ui(u), ak.pop(), -12)
for u in U["sparkle"]: ak.place(sfx, ui(u), ak.sparkle(), -11)
for u in U["whoosh"]: ak.place(sfx, ui(u) - 0.15, ak.whoosh(0.3), -17)
t0, cps = U["type"]
for k in range(len(tl.COPY["prompt"])): ak.place(sfx, ui(t0 + (k + 1) / cps), ak.tick(40 + k), -19)   # a tick per typed letter
BC = tl.BUILD_CUES                                                      # results build
ak.place(sfx, tl.T_BUILD - 0.15, ak.whoosh(0.3), -14)
ak.place(sfx, tl.T_BUILD + BC["thermal"], ak.whoosh(0.9, up=False), -18)
for s in BC["steps"]: ak.place(sfx, tl.T_BUILD + s, ak.pop(1100), -13)
for k in range(0, 12, 2): ak.place(sfx, tl.T_BUILD + BC["cascade"] + 0.1 + k * 0.04, ak.pop(600 + 40 * k), -19)
ak.place(sfx, C - 2 * B, ak.riser(2 * B), -11)                          # toggle: riser into the click
ak.place(sfx, C - 2 * B, ak.snare_roll(2 * B - 2.0 / FPS), -15)
ak.place(sfx, C, ak.click(), -6); ak.place(sfx, C, ak.impact(), -6); ak.place(sfx, C + 0.02, ak.sparkle(1760), -12)
a, _ = tl.TYPE["echo"]; ak.place(sfx, a, ak.shutter(), -10)
for b in tl.TYPE["slams"]: ak.place(sfx, b, ak.impact(0.9), -9)
for (t, kind, n) in tl.HITS: ak.place(sfx, t, ak.glitch_sfx(0.12) if kind.startswith("negative") else ak.shutter(), -13)
ak.place(sfx, tl.T_END, ak.sparkle(), -12); ak.place(sfx, tl.END_CLICK, ak.click(), -9)

# ---- 3. voice-over (optional): one line per slam / lockup, music ducked to 45% under each line
vo = ak.bus(L); regions = []
for t, (text, kind) in sorted(tl.VO.items(), key=lambda kv: float(kv[0])):
    x = ak.vo_fx(ak.tts(text, f"audio/vo_{float(t):.2f}.wav"), kind); ak.place(vo, float(t), x, -2)
    regions.append((float(t), float(t) + len(x) / ak.SR))
if regions: music = ak.duck(music, regions, to=0.45)

n = int(L * ak.SR); fit = lambda x: np.pad(x[:n], ((0, max(0, n - len(x[:n]))), (0, 0)))
ak.master(fit(music) + fit(sfx) + fit(vo), "out/audio.wav")
if len(sys.argv) > 1:
    v = sys.argv[1]; ak.mux(v, "out/audio.wav", v.replace(".mp4", "_final.mp4"), max_mb=MAX_MB)
