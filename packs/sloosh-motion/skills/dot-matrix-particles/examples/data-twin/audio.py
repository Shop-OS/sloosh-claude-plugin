"""audio.py (dot-matrix-particles "Data Twin"): original minimal techno + data SFX on the SAME timeline as the picture.

  python3 audio.py                       -> out/audio.wav (-14 LUFS / -2 dBTP) + RMS per 2 s
  python3 audio.py out/nova_dots_v1.mp4  -> also muxes out/nova_dots_v1_final.mp4 (< 30 MB)
Restraint: ticks for LEDs switching on and data scans, a glitch on each strobe cut, a riser into the burst, a pop on the
reveal, a whoosh when the particles fly, a click when the wordmark locks. No whoosh on every cut.
Claude cannot hear: read the RMS report, then ask the user to listen.
"""
import subprocess, sys
sys.path.insert(0, "lib")
import numpy as np
import audiokit as ak
import tl

USER_TRACK, USER_DROP = None, None           # the user's track + its drop (<director>/scripts/beatmap.py): cut so the drop lands on tl.DROP
L, D, B = tl.LEN, tl.DROP, tl.B

if USER_TRACK:
    tmp = "audio/_track.wav"; start = max(0.0, USER_DROP - D)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{start:.3f}", "-i", USER_TRACK, "-t", f"{L:.3f}", "-ar", str(ak.SR), "-ac", "2", tmp], check=True)
    from scipy.io import wavfile
    music = wavfile.read(tmp)[1].astype(np.float32) / 32768.0; music = np.pad(music, ((0, max(0, int(L * ak.SR) - len(music))), (0, 0)))
else:
    music = ak.score(tl.GENRE, tl.BPM, L, D, tl.KEY, breath=D - tl.T_BREATH)
music = ak.gap(music, tl.T_BREATH, D)
music = ak.lowpass_region(music, tl.T_ASM, tl.T_END, 1800, 0.75)      # the assemble breathes; the end card opens again

sfx = ak.bus(L)
for j in range(6): ak.place(sfx, 0.1 + j * 0.16, ak.tick(1 + j), -20, pan=0.3 if j % 2 else -0.3)   # LEDs switching on
for t0 in tl.STROBE: ak.place(sfx, t0, ak.glitch_sfx(0.06, seed=int(t0 * 100)), -16)                  # every strobe switch
for k in range(int(4 * B / (B / 2))): ak.place(sfx, 7 * B + k * B / 2, ak.tick(30 + k), -22)        # data-scan bed under the cloud
ak.place(sfx, 11 * B, ak.sweep(200, 1400, 0.9, 1.5) * ak.env(int(0.9 * ak.SR), 0.05, 0.7, 0.5, 0.1) * 0.2, -14)  # thermal rise
ak.place(sfx, 18 * B, ak.pop(), -12)                                                                # dot-wave reveal
for (tc, kind, n) in tl.TRANS: ak.place(sfx, tc, ak.shutter(), -14)
a, _ = tl.TYPE["led"]
for j in range(5): ak.place(sfx, a + j * 0.05, ak.tick(50 + j), -18)                                # the LED board sweeps on
ak.place(sfx, tl.T_ASM + 0.2, ak.whoosh(1.2, seed=3), -13)                                          # particles fly
ak.place(sfx, tl.T_END - 0.05, ak.click(), -10); ak.place(sfx, tl.T_END, ak.sparkle(), -14)         # the wordmark locks

vo = ak.bus(L); regions = []
for t0, (text, kind) in sorted(tl.VO.items(), key=lambda kv: float(kv[0])):
    x = ak.vo_fx(ak.tts(text, f"audio/vo_{float(t0):.2f}.wav"), kind); ak.place(vo, float(t0), x, -2)
    regions.append((float(t0), float(t0) + len(x) / ak.SR))
if regions: music = ak.duck(music, regions, to=0.45)

n = int(L * ak.SR); fit = lambda x: np.pad(x[:n], ((0, max(0, n - len(x[:n]))), (0, 0)))
ak.master(fit(music) + fit(sfx) + fit(vo), "out/audio.wav")
if len(sys.argv) > 1:
    v = sys.argv[1]; ak.mux(v, "out/audio.wav", v.replace(".mp4", "_final.mp4"))
