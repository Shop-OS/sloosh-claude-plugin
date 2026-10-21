"""audio.py: original score + one SFX per word hit + optional VO, on the SAME timeline as the type.

  python3 audio.py                     -> out/audio.wav (-14 LUFS / -2 dBTP) + RMS per 2 s
  python3 audio.py out/kt_poster_v1.mp4 -> also muxes out/kt_poster_v1_final.mp4 (< 30 MB)
SFX cues come from lib/ktfield.sfx_cues(tl): the scenes in tl.TYPE["kt"] (tick per landing word, impact per slam, shutter per
inversion, ticks per split-flap lock, whoosh per wipe...). A user's own track: set USER_TRACK + USER_DROP (director beatmap.py).
VO is opt-in: it runs only when tl.VO has lines, and only with a voice already installed on this computer (nothing is fetched).
The agent cannot hear: read the RMS report, then ask the user to listen."""
import subprocess, sys

USER_TRACK = None
USER_DROP = None


def main():
    sys.path.insert(0, "lib")
    import numpy as np
    import audiokit as ak
    import ktfield as kf
    import tl
    L, D = tl.LEN, tl.DROP

    # ---- 1. music: original score arranged around the drop (or the user's track cut so its drop lands on D)
    if USER_TRACK:
        tmp = "audio/_track.wav"; start = max(0.0, USER_DROP - D)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{start:.3f}", "-i", USER_TRACK, "-t", f"{L:.3f}", "-ar", str(ak.SR), "-ac", "2", tmp], check=True)
        from scipy.io import wavfile
        music = wavfile.read(tmp)[1].astype(np.float32) / 32768.0; music = np.pad(music, ((0, max(0, int(L * ak.SR) - len(music))), (0, 0)))
    else:
        music = ak.score(tl.GENRE, tl.BPM, L, D, tl.KEY, breath=D - tl.T_BREATH)
    music = ak.gap(music, tl.T_BREATH, D)

    # ---- 2. one SFX per word hit (the same cue list the page animates)
    SFX = {"tick": lambda: ak.tick(), "impact": lambda: ak.impact(0.9), "shutter": lambda: ak.shutter(), "whoosh": lambda: ak.whoosh(0.35),
           "pop": lambda: ak.pop(), "click": lambda: ak.click(), "sparkle": lambda: ak.sparkle(), "subdrop": lambda: ak.subdrop(),
           "riser": lambda: ak.riser(1.5), "glitch": lambda: ak.glitch_sfx(0.12)}
    LEAD = {"whoosh": 0.0, "riser": 1.5}            # whooshes are already cued ~0.2 s early by sfx_cues; risers end on their cue
    sfx = ak.bus(L)
    for t0, name, g in kf.sfx_cues(tl):
        ak.place(sfx, max(0.0, t0 - LEAD.get(name, 0.0)), SFX[name](), g)
    ak.place(sfx, max(0.0, D - 1.5), ak.riser(1.5), -15)       # a riser that ends on the drop

    # ---- 3. voice-over (opt-in, only when tl.VO has lines): one line per slam, music ducked to 45% under each line
    vo = ak.bus(L); regions = []
    for t0, (text, kind) in sorted(getattr(tl, "VO", {}).items(), key=lambda kv: float(kv[0])):
        x = ak.vo_fx(ak.tts(text, f"audio/vo_{float(t0):.2f}.wav"), kind); ak.place(vo, float(t0), x, -2)
        regions.append((float(t0), float(t0) + len(x) / ak.SR))
    if regions: music = ak.duck(music, regions, to=0.45)

    n = int(L * ak.SR)
    def fit(x): return np.pad(x[:n], ((0, max(0, n - len(x[:n]))), (0, 0)))
    mix = fit(music) * 0.8 + fit(sfx) + fit(vo)
    ak.master(mix, "out/audio.wav")
    if len(sys.argv) > 1:
        v = sys.argv[1]; ak.mux(v, "out/audio.wav", v.replace(".mp4", "_final.mp4"))


if __name__ == "__main__":
    main()
