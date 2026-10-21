"""audio.py: original score, SFX and optional VO on the same timeline.

  python3 audio.py                        -> out/audio.wav (-14 LUFS / -2 dBTP) + RMS per 2 s
  python3 audio.py out/example_feature_v1.mp4 -> also muxes out/example_feature_v1_final.mp4
Arrangement: filtered techno intro under the hook and the name card, riser + breath, DROP when the window springs in,
the groove low-passed under the UI so the clicks read, drop 2 (wide open) on the payoff, tail on the end card.
SFX: pop + sparkle on the NEW pill, shine swish on the name, click per click, pop on the menu, sparkle on A -> B,
a pop per check, impacts on the payoff, sparkle + click on the end card.
"""
import subprocess, sys
sys.path.insert(0, "lib")
import numpy as np
import audiokit as ak
import tl
from edit import SHOTS

USER_TRACK, USER_DROP = None, None
MAX_MB = 30.0                               # delivery size cap for the final file
L, D, B, P, FPS = tl.LEN, tl.DROP, tl.B, tl.T_PAY, tl.FPS
pt = tl.p2t

if USER_TRACK:
    tmp = "audio/_track.wav"; start = max(0.0, USER_DROP - D)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{start:.3f}", "-i", USER_TRACK, "-t", f"{L:.3f}", "-ar", str(ak.SR), "-ac", "2", tmp], check=True)
    from scipy.io import wavfile
    music = wavfile.read(tmp)[1].astype(np.float32) / 32768.0; music = np.pad(music, ((0, max(0, int(L * ak.SR) - len(music))), (0, 0)))
else:
    music = ak.score(tl.GENRE, tl.BPM, L, D, tl.KEY, breath=D - tl.T_BREATH)
music = ak.gap(music, tl.T_BREATH, D)
music = ak.lowpass_region(music, D + 0.5, P - 2.0 / FPS, 1400, 0.6)      # under the UI: clicks read
music = ak.gap(music, P - 2.0 / FPS, P)                                  # 2-frame breath, then drop 2 wide open

sfx = ak.bus(L)
for c in sorted({round(s[0], 3) for s in SHOTS if 0.05 < s[0] < tl.T_RUSH}): ak.place(sfx, c - 0.22, ak.whoosh(0.3), -18)
ak.place(sfx, tl.T_RUSH, ak.riser(tl.T_NAME - tl.T_RUSH), -10); ak.place(sfx, tl.T_NAME, ak.impact(1.0), -16)
F = tl.FEAT_CUES
for p in F["click"]: ak.place(sfx, pt(p), ak.click(), -8)
for p in F["pop"]: ak.place(sfx, pt(p), ak.pop(), -12)
for p in F["sparkle"]: ak.place(sfx, pt(p), ak.sparkle(), -11)
for p in F["whoosh"]: ak.place(sfx, pt(p) - 0.15, ak.whoosh(0.3), -16)
ak.place(sfx, pt(F["shine"]), ak.whoosh(0.4, up=False), -20)                     # the shine swish
for i, w in enumerate(tl.COPY["feature"][2].split()): ak.place(sfx, pt(0.9 + i * 0.09), ak.tick(30 + i), -21)
ak.place(sfx, P - 2 * B, ak.riser(2 * B), -12); ak.place(sfx, P, ak.impact(), -6)
for (t, kind, n) in tl.HITS: ak.place(sfx, t, ak.glitch_sfx(0.12) if kind.startswith("negative") else ak.shutter(), -13)
for k in ("lockA_1", "lockA_2"): ak.place(sfx, tl.TYPE[k][0], ak.shutter(), -12)
ak.place(sfx, tl.T_END, ak.sparkle(), -12); ak.place(sfx, tl.END_CLICK, ak.click(), -9)

vo = ak.bus(L); regions = []
for t, (text, kind) in sorted(tl.VO.items(), key=lambda kv: float(kv[0])):
    x = ak.vo_fx(ak.tts(text, f"audio/vo_{float(t):.2f}.wav"), kind); ak.place(vo, float(t), x, -2)
    regions.append((float(t), float(t) + len(x) / ak.SR))
if regions: music = ak.duck(music, regions, to=0.45)

n = int(L * ak.SR); fit = lambda x: np.pad(x[:n], ((0, max(0, n - len(x[:n]))), (0, 0)))
ak.master(fit(music) + fit(sfx) + fit(vo), "out/audio.wav")
if len(sys.argv) > 1:
    v = sys.argv[1]; ak.mux(v, "out/audio.wav", v.replace(".mp4", "_final.mp4"), max_mb=MAX_MB)
