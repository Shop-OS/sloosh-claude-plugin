"""audio.py: Send Morph score + SFX on the same timeline.

  python3 audio.py                  -> out/audio.wav (-14 LUFS)        python3 audio.py out/x_v2.mp4 -> + muxed final
SFX map: pop when the dot is born, a soft tick on every state landing, a click on each micro-action, typing ticks,
the send click + one ring ping per ring + shimmer, an impact + sparkle when the eyes pop, a whoosh/shimmer as the
wordmark grows out, a shutter on the end line. The groove sits low-passed under the UI and opens on the drop.
"""
import sys
sys.path.insert(0, "lib")
import numpy as np
import audiokit as ak, morphsfx as ms
import tl

L, D, B, M = tl.LEN, tl.DROP, tl.B, tl.MORPH
music = ak.score(tl.GENRE, tl.BPM, L, D, tl.KEY)
music = ak.lowpass_region(music, 0.0, D, 1400, 0.7)                     # the UI section breathes; clicks read
sfx = ak.bus(L)
ak.place(sfx, 0.1, ak.pop(), -14)
for s in M["states"]: ak.place(sfx, s + 0.42, ak.tick(), -12); ak.place(sfx, s + 0.05, ms.shimmer(0.45), -24)
S = M["states"]
for t in [S[0] + 0.7, S[3] + 0.45]: ak.place(sfx, t, ak.click(), -12)                 # button press, toggle
for i in range(5): ak.place(sfx, S[4] + 0.35 + i * 0.06, ak.pop(1200 + 120 * i), -22)   # bars
t0, cps = M["type"]
for i, ch in enumerate(M["prompt"]):
    if ch != " ": ak.place(sfx, t0 + i / cps, ak.tick(i), -18)
ak.place(sfx, M["click"], ak.click(), -8)
for k in range(3): ak.place(sfx, M["click"] + 0.08 * k, ms.ring(1760 * (1 + 0.25 * k)), -14)
ak.place(sfx, M["tile"] + 0.5 - 0.4, ms.shimmer(0.5), -14)
ak.place(sfx, M["icon"], ak.sparkle(), -10)
for g in M["glance"]: ak.place(sfx, g, ak.tick(), -16)
ak.place(sfx, M["blink"], ak.pop(1600), -18)
ak.place(sfx, M["grow"] - 0.1, ak.whoosh(0.5), -14); ak.place(sfx, M["settle"] - 0.56, ms.shimmer(0.7), -12)
ak.place(sfx, M["settle"], ak.impact(1.2), -12); ak.place(sfx, tl.T_END, ak.shutter(), -14)
for (t, kind, n) in tl.HITS: ak.place(sfx, t, ak.glitch_sfx(0.1), -16)
n = int(L * ak.SR); fit = lambda x: np.pad(x[:n], ((0, max(0, n - len(x[:n]))), (0, 0)))
ak.master(fit(music) + fit(sfx), "out/audio.wav")
if len(sys.argv) > 1: ak.mux(sys.argv[1], "out/audio.wav", sys.argv[1].replace(".mp4", "_final.mp4"))
