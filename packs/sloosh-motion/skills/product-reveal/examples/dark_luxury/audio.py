"""audio.py: product-reveal score, SFX and optional VO on the SAME timeline.

  python3 audio.py                     -> out/audio.wav (-14 LUFS / -2 dBTP) + RMS per 2 s
  python3 audio.py out/<name>_vN.mp4   -> also muxes <name>_vN_final.mp4 (< 30 MB)
Restraint: a luxury reveal carries 10-16 SFX in 15 s, each on its frame. Claude cannot hear: read the RMS report,
then ask the user to listen.
"""
import subprocess, sys
sys.path.insert(0, "lib")
import numpy as np
import audiokit as ak
import tl
from edit import SHOTS

USER_TRACK, USER_DROP = None, None          # a user's track: its drop is cut onto tl.DROP
L, D, B = tl.LEN, tl.DROP, tl.B

# ---- 1. music: original score arranged to the picture (or the user's track, drop on D)
if USER_TRACK:
    tmp = "audio/_track.wav"; start = max(0.0, USER_DROP - D)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{start:.3f}", "-i", USER_TRACK, "-t", f"{L:.3f}",
                    "-ar", str(ak.SR), "-ac", "2", tmp], check=True)
    from scipy.io import wavfile
    music = wavfile.read(tmp)[1].astype(np.float32) / 32768.0
else:
    music = ak.score(tl.GENRE, tl.BPM, L, D, tl.KEY, breath=D - tl.T_BREATH)
music = ak.gap(music, tl.T_BREATH, D)                                   # the black breath is silent
music = ak.lowpass_region(music, tl.T_PACK, tl.T_END, 2400, 0.8)        # the packshot breathes; the sweep reads

# ---- 2. SFX from the shared cue list
sfx = ak.bus(L)
cuts = sorted({round(s[0], 3) for s in SHOTS if 0.05 < s[0] < tl.T_BREATH})
ak.place(sfx, 0.0, ak.whoosh(1.2, up=True), -22)                        # air under the rim light crawl
for c in cuts: ak.place(sfx, c - 0.2, ak.whoosh(0.28), -19)             # each pre-drop cut peaks on its frame
ak.place(sfx, tl.T_D1, ak.pop(1300), -15)                               # the anchor macro: a glass/metal ping
# counter ticks: one per integer step of the SAME ease-out the page uses (RV.counter, cubic)
ca = tl.TYPE["counter"][0] + 0.05; to = float(tl.COPY["counter"][0]); last = -1
for f in range(int(tl.COUNT_DUR * tl.FPS) + 1):
    x = f / tl.FPS / tl.COUNT_DUR; v = int(to * (1 - (1 - min(1, x)) ** 3))
    if v != last and v % max(1, int(to // 12)) == 0: ak.place(sfx, ca + f / tl.FPS, ak.tick(f), -14); last = v
ak.place(sfx, tl.T_ACT, ak.swell(ak.chord(tl.KEY, 0, 4), 1.2), -18)     # the action moment opens
ak.place(sfx, tl.T_BREATH + 0.16, ak.shutter(), -10)                    # the white strobe
ak.place(sfx, D, ak.impact(1.8), -8); ak.place(sfx, D, ak.subdrop(), -10)  # the hero lands
for a in tl.TYPE["slams"]: ak.place(sfx, a, ak.impact(0.7), -12)
ak.place(sfx, tl.TYPE["echo"][0], ak.impact(0.9), -11)
ak.place(sfx, tl.TYPE["name"][0] - 0.12, ak.whoosh(0.5), -16)           # the name passes behind the product
ak.place(sfx, tl.T_PACK + 0.55, ak.whoosh(0.9, up=False), -24)          # the specular sweep: soft air
ak.place(sfx, tl.T_END + 0.35, ak.sparkle(), -16)                       # the wordmark settles

# ---- 3. voice-over (optional), music ducked under each line
vo = ak.bus(L); regions = []
for t0, (text, kind) in sorted(tl.VO.items(), key=lambda kv: float(kv[0])):
    x = ak.vo_fx(ak.tts(text, f"audio/vo_{float(t0):.2f}.wav"), kind); ak.place(vo, float(t0), x, -2)
    regions.append((float(t0), float(t0) + len(x) / ak.SR))
if regions: music = ak.duck(music, regions, to=0.45)

n = int(L * ak.SR); fit = lambda x: np.pad(x[:n], ((0, max(0, n - len(x[:n]))), (0, 0)))
ak.master(fit(music) + fit(sfx) + fit(vo), "out/audio.wav")
if len(sys.argv) > 1:
    v = sys.argv[1]; ak.mux(v, "out/audio.wav", v.replace(".mp4", "_final.mp4"))
