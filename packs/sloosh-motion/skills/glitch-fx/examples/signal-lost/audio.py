"""audio.py (glitch-fx "Signal Lost"): original techno + glitch SFX on the SAME timeline as the picture.

  python3 audio.py                     -> out/audio.wav (-14 LUFS / -2 dBTP) + RMS per 2 s
  python3 audio.py out/nova_glitch_v1.mp4  -> also muxes out/nova_glitch_v1_final.mp4 (< 30 MB)
Glitch is the one style where SFX are dense: EVERY hit, wipe, stutter and typed letter has a sound peaking on its frame.
A silent glitch looks like a render bug. Claude cannot hear: read the RMS report, then ask the user to listen.
"""
import subprocess, sys
sys.path.insert(0, "lib")
import numpy as np
import audiokit as ak
import tl

USER_TRACK, USER_DROP = None, None          # the user's own track + its drop time (<director>/scripts/beatmap.py); cut so the drop lands on tl.DROP
L, D, B, FPS = tl.LEN, tl.DROP, tl.B, tl.FPS
fr = lambda n: n / FPS

# ---- 1. music: minimal techno, filtered intro, the drop opens up
if USER_TRACK:
    tmp = "audio/_track.wav"; start = max(0.0, USER_DROP - D)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{start:.3f}", "-i", USER_TRACK, "-t", f"{L:.3f}", "-ar", str(ak.SR), "-ac", "2", tmp], check=True)
    from scipy.io import wavfile
    music = wavfile.read(tmp)[1].astype(np.float32) / 32768.0; music = np.pad(music, ((0, max(0, int(L * ak.SR) - len(music))), (0, 0)))
else:
    music = ak.score(tl.GENRE, tl.BPM, L, D, tl.KEY, breath=D - tl.T_BREATH)

# ---- 2. edits that follow the picture: tape-stop "psych", silence until the drop; a 4x stutter on the BUILD hit
music = ak.tape_stop(music, tl.T_PSYCH, 0.32)
music = ak.gap(music, tl.T_PSYCH + 0.32, D)
def stutter(b, t, piece=2 / 30, n=4):      # repeat a 2-frame slice n times (audio glitch on a burst)
    i, k = int(t * ak.SR), int(piece * ak.SR); seg = b[i:i + k].copy()
    for j in range(n): b[i + j * k:i + (j + 1) * k] = seg * (1 - 0.15 * j)
    return b
music = stutter(music, tl.T_PAY + B)

# ---- 3. SFX from the shared cue list
sfx = ak.bus(L)
def static_burst(sec=0.12, seed=3): return ak.hp(ak.noise(sec, seed), 900) * ak.env(int(sec * ak.SR), 0.001, sec * 0.6, 0.4, 0.02) * 0.6
for (t0, kind, n, *p) in tl.GLITCH:
    k = kind.split("+")[0]
    if k in ("slices", "rgb", "blocks"): ak.place(sfx, t0, ak.glitch_sfx(fr(n) + 0.06, seed=int(t0 * 100)), -11)
    elif k == "static": ak.place(sfx, t0, static_burst(fr(n) + 0.05), -10)
    elif k == "noise": ak.place(sfx, t0, static_burst(0.08, 9), -12)
    elif k in ("strobe", "psych"):
        for g in range(0, n, 4): ak.place(sfx, t0 + fr(g), ak.glitch_sfx(0.07, seed=g + 5), -12)
for (tc, kind, n) in tl.TRANS:                                              # wipes: a tick at the start + a short whoosh
    ak.place(sfx, tc, ak.tick(4), -14); ak.place(sfx, tc - 0.05, ak.whoosh(0.2, seed=int(tc * 10)), -18)
a = tl.TYPE["stack"][0]                                                     # title stutter: a tick per visible step
for s in range(6): ak.place(sfx, a + fr(2 * s), ak.tick(20 + s), -16)
ak.place(sfx, a, ak.glitch_sfx(0.1, 2), -14)
for k in ("label1", "label2"):                                              # typed mono labels: a tick per letter
    t0, t1 = tl.TYPE[k]
    for j in range(len(tl.COPY[k])): ak.place(sfx, t0 + j / 30, ak.tick(40 + j), -22)
for w in tl.HUD["track"]:                                                   # HUD locks on: data-scan ticks for 0.5 s
    for j in range(8): ak.place(sfx, w["t"][0] + fr(2 * j), ak.tick(60 + j), -20, pan=0.3 if j % 2 else -0.3)
x0 = 2 * B                                                                  # x-ray scan: a fast rising sweep with the line
ak.place(sfx, x0, ak.sweep(300, 3200, 0.36, 2.0) * ak.env(int(0.36 * ak.SR), 0.01, 0.3, 0.6, 0.05) * 0.25, -12)
for t0 in tl.TYPE["slams"][:-1]: ak.place(sfx, t0, ak.impact(0.9), -9)    # every slam hits
ak.place(sfx, tl.T_END, ak.impact(1.2), -8)                                 # the stamp
ak.place(sfx, D - 0.4, ak.riser(0.4), -14)                                  # tiny lift into the drop out of the silence

# ---- 4. voice-over (optional, tl.VO is empty by default): music ducked to 45% under each line.
#      ak.tts needs a text-to-speech engine on the user's computer. Ask the user before installing one; or record the
#      lines and place the files instead.
vo = ak.bus(L); regions = []
for t0, (text, kind) in sorted(tl.VO.items(), key=lambda kv: float(kv[0])):
    x = ak.vo_fx(ak.tts(text, f"audio/vo_{float(t0):.2f}.wav"), kind); ak.place(vo, float(t0), x, -2)
    regions.append((float(t0), float(t0) + len(x) / ak.SR))
if regions: music = ak.duck(music, regions, to=0.45)

n = int(L * ak.SR); fit = lambda x: np.pad(x[:n], ((0, max(0, n - len(x[:n]))), (0, 0)))
ak.master(fit(music) + fit(sfx) + fit(vo), "out/audio.wav")
if len(sys.argv) > 1:
    v = sys.argv[1]; ak.mux(v, "out/audio.wav", v.replace(".mp4", "_final.mp4"))
