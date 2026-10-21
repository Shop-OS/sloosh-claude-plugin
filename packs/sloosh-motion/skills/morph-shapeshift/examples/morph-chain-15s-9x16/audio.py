"""audio.py: Morph Chain score + SFX on the SAME timeline.

  python3 audio.py                  -> out/audio.wav (-14 LUFS / -2 dBTP) + RMS per 2 s
  python3 audio.py out/x_v2.mp4     -> also muxes out/x_v2_final.mp4 (< 30 MB)
Sound of this style: a shimmer that PEAKS on every morph landing, a reversed swell into each transition clip,
a shutter tick on every 0.25 s match cut, glitch on negatives, an impact on the drop, a sparkle when the logo lands.
VO is optional (tl.VO); it needs the director's voice setup.
"""
import subprocess, sys
sys.path.insert(0, "lib")
import numpy as np
import audiokit as ak, morphsfx as ms
import tl

USER_TRACK, USER_DROP = None, None          # a user's track (path, drop second): its drop is cut onto tl.DROP
L, D, B = tl.LEN, tl.DROP, tl.B


def music_bed():
    if USER_TRACK:
        tmp = "audio/_track.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{max(0.0, USER_DROP - D):.3f}", "-i", USER_TRACK,
                        "-t", f"{L:.3f}", "-ar", str(ak.SR), "-ac", "2", tmp], check=True)
        from scipy.io import wavfile
        music = wavfile.read(tmp)[1].astype(np.float32) / 32768.0
    else:
        music = ak.score(tl.GENRE, tl.BPM, L, D, tl.KEY, breath=D - tl.T_BREATH)
    music = ak.gap(music, tl.T_BREATH, D)
    return ak.tape_stop(music, tl.T_BREATH - 0.34, 0.32)       # "psych" into the breath


def sfx_bus():
    sfx = ak.bus(L)
    for m in tl.MORPHS: ak.place(sfx, m - 0.56, ms.shimmer(0.7), -13)          # every morph: shimmer peaks on the landing
    for c in tl.CLIP_STARTS: ak.place(sfx, c + 0.25, ms.morph_swell(0.9), -15)  # transition clips suck into their landing
    for c in tl.PRE_CUTS: ak.place(sfx, c - 0.22, ak.whoosh(0.3), -18)
    for m in tl.MATCH[1:]: ak.place(sfx, m, ak.shutter(), -13)                 # 0.25 s match cuts
    for f in tl.TYPE["forms"]: ak.place(sfx, f[0], ak.tick(), -14)
    for (t0, kind, n) in tl.HITS:
        if kind.startswith("negative"): ak.place(sfx, t0, ak.glitch_sfx(0.12), -12)
        elif kind in ("duo", "red"): ak.place(sfx, t0, ak.shutter(), -11)
    ak.place(sfx, tl.TYPE["echo"][0], ak.impact(1.4), -9)
    ak.place(sfx, tl.T_END, ak.sparkle(), -11); ak.place(sfx, tl.T_END + 0.35, ak.impact(1.2), -13)
    return sfx


def main():
    music, sfx = music_bed(), sfx_bus()
    vo = ak.bus(L); regions = []
    for t0, (text, kind) in sorted(tl.VO.items(), key=lambda kv: float(kv[0])):
        x = ak.vo_fx(ak.tts(text, f"audio/vo_{float(t0):.2f}.wav"), kind)
        ak.place(vo, float(t0), x, -2); regions.append((float(t0), float(t0) + len(x) / ak.SR))
    if regions: music = ak.duck(music, regions, to=0.45)
    n = int(L * ak.SR)
    fit = lambda x: np.pad(x[:n], ((0, max(0, n - len(x[:n]))), (0, 0)))
    ak.master(fit(music) + fit(sfx) + fit(vo), "out/audio.wav")
    if len(sys.argv) > 1: ak.mux(sys.argv[1], "out/audio.wav", sys.argv[1].replace(".mp4", "_final.mp4"))


if __name__ == "__main__":
    main()
