#!/usr/bin/env python3
"""Envelope analysis of an SFX library: duration, attack, peak time, end, peak/RMS dBFS.
usage: python3 sfx_analyze.py <sfx_root> [category_subdir …] > sfx_index.tsv
With no categories, every sub-folder containing audio is analysed."""
import subprocess, sys, os, json
import numpy as np
B = sys.argv[1]
cats = sys.argv[2:]
if not cats:
    cats = sorted({os.path.relpath(dp, B) for dp, _, fs in os.walk(B) if any(f.lower().endswith((".wav", ".mp3", ".aif", ".aiff")) for f in fs)})
rows = []
for cat in cats:
    d = os.path.join(B, cat)
    for f in sorted(os.listdir(d)):
        if not f.lower().endswith((".wav", ".mp3", ".aif", ".aiff")):
            continue
        p = os.path.join(d, f)
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", "8000", "-f", "f32le", "-"], capture_output=True).stdout
        x = np.frombuffer(raw, dtype=np.float32)
        if len(x) == 0:
            continue
        sr = 8000
        dur = len(x) / sr
        win = int(sr * 0.02)
        n = len(x) // win
        if n == 0:
            continue
        rms = np.sqrt(np.mean(x[: n * win].reshape(n, win) ** 2, axis=1) + 1e-12)
        mx = rms.max()
        peak_t = (np.argmax(rms) + 0.5) * 0.02
        att = np.argmax(rms > 0.25 * mx) * 0.02
        above = np.where(rms > 0.1 * mx)[0]
        end_t = (above[-1] + 1) * 0.02 if len(above) else dur
        rms_db = 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)
        pk_db = 20 * np.log10(np.abs(x).max() + 1e-12)
        rows.append((cat, f, f"{dur:.2f}", f"{att:.2f}", f"{peak_t:.2f}", f"{end_t:.2f}", f"{pk_db:.1f}", f"{rms_db:.1f}", p))
print("category\tfile\tdur\tattack\tpeak\tend\tpeak_dBFS\trms_dBFS\tpath")
for r in rows:
    print("\t".join(str(x) for x in r))
