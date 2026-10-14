#!/usr/bin/env python3
"""VO-vs-SFX balance check: subtracts the (aligned) voiceover from the rendered mix and
prints VO and SFX levels per 250 ms window, flagging windows where SFX crowd speech.
usage: python3 mixcheck.py <mix.wav or .mp4> <vo audio> <vo_offset_seconds>"""
import subprocess, sys
import numpy as np
mix_path, vo_path, offset = sys.argv[1], sys.argv[2], float(sys.argv[3])
SR = 16000
def load(p):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()
mix = load(mix_path)
vo = load(vo_path)
vo_al = np.zeros_like(mix)
o = int(offset * SR)
n = min(len(vo), len(mix) - o)
vo_al[o:o + n] = vo[:n]
# best-fit gain for VO in the mix (Remotion mixes VO at volume 1, but codec may alter slightly)
g = float(np.dot(mix, vo_al) / (np.dot(vo_al, vo_al) + 1e-9))
res = mix - g * vo_al
print(f"VO gain in mix: {g:.3f}   mix peak: {20*np.log10(np.abs(mix).max()+1e-9):.1f} dBFS")
win = int(0.25 * SR)
def db(x):
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)
print(f"{'t(s)':>6} {'VO dB':>7} {'SFX dB':>7} {'SFX-VO':>7}")
flags = []
for i in range(0, len(mix) - win, win):
    t = i / SR
    v = db(g * vo_al[i:i + win]); s = db(res[i:i + win])
    rel = s - v
    mark = ""
    if v > -40 and rel > -6:
        mark = "  <-- SFX loud vs speech"
        flags.append(t)
    print(f"{t:6.2f} {v:7.1f} {s:7.1f} {rel:7.1f}{mark}")
print("flagged:", flags)
