"""audio.py: original score, SFX and voice-over on the SAME timeline as the picture.

  python3 audio.py                         -> out/audio.wav (mastered -14 LUFS / -2 dBTP) + RMS per 2 s
  python3 audio.py out/film_v2.mp4         -> also muxes the delivery file out/film_v2_final.mp4 (under MAX_MB, true peak <= -1 dBTP)
If the user attached a track: set USER_TRACK and USER_DROP. The track is cut so its drop lands on tl.DROP.
Find the drop with: python3 <director>/scripts/beatmap.py audio/track.mp3 --film <LEN> --drop-at <DROP>
You cannot hear the mix: after rendering, read the RMS report and ask the user to listen.
"""
import os, subprocess, sys
sys.path.insert(0, "lib")
import numpy as np
import audiokit as ak
import tl

USER_TRACK = None                           # e.g. "audio/track.mp3" (a track the user supplied and has the rights to)
USER_DROP = None                            # drop time inside the user's track (s), from beatmap.py
USER_VO = {}                                # optional user VO files: time -> "audio/vo_line1.wav" (used instead of TTS)
MAX_MB = 30.0                               # delivery size cap for the final file

def cut_times():
    """cut times from the same cut list as the picture (edit.py); none if edit.py cannot be read yet."""
    try:
        from edit import SHOTS
    except (Exception, SystemExit) as e:
        print(f"audio.py: no cut list from edit.py ({e}); cut whooshes skipped"); return []
    return sorted({round(s[0], 3) for s in SHOTS if s[0] > 0.05})

def load_wav(path, length=None):
    """any audio file -> stereo float32 at ak.SR (through ffmpeg)."""
    tmp = "audio/_load.wav"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", path] + (["-t", f"{length:.3f}"] if length else []) + ["-ar", str(ak.SR), "-ac", "2", "-c:a", "pcm_s16le", tmp]
    subprocess.run(cmd, check=True)
    from scipy.io import wavfile
    return wavfile.read(tmp)[1].astype(np.float32) / 32768.0

def main():
    L, D, B = tl.LEN, tl.DROP, tl.B
    cuts = cut_times()

    # ---- 1. music: original score (or the user's track aligned so its drop lands on D)
    if USER_TRACK:
        if USER_DROP is None: sys.exit("audio.py: set USER_DROP (the drop time inside the track) from beatmap.py")
        start = max(0.0, USER_DROP - D); tmp = "audio/_track.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{start:.3f}", "-i", USER_TRACK, "-t", f"{L:.3f}",
                        "-ar", str(ak.SR), "-ac", "2", "-c:a", "pcm_s16le", tmp], check=True)
        from scipy.io import wavfile
        music = wavfile.read(tmp)[1].astype(np.float32) / 32768.0
        music = np.pad(music, ((0, max(0, int(L * ak.SR) - len(music))), (0, 0)))
    else:
        music = ak.score(tl.GENRE, tl.BPM, L, D, tl.KEY, breath=D - tl.T_BREATH)

    # ---- 2. edits on the music that follow the picture
    music = ak.gap(music, tl.T_BREATH, D)                       # silence in the breath
    # ak.tape_stop(music, D - 0.45, 0.32)                       # optional "psych" before the drop
    # ak.lowpass_region(music, ui_start, ui_end, 1400, 0.6)     # under a UI section so clicks read

    # ---- 3. SFX placed from the shared cue list (each SFX peak sits on its frame)
    sfx = ak.bus(L)
    for c in cuts:
        if c < D - 0.2: ak.place(sfx, c - 0.22, ak.whoosh(0.3), -16)          # whoosh peaking on each pre-drop cut
    for b in tl.TYPE.get("slams", []): ak.place(sfx, b, ak.impact(0.9), -9)   # every text slam hits
    if "echo" in tl.TYPE: ak.place(sfx, tl.TYPE["echo"][0], ak.shutter(), -10)
    for (t0, kind, n) in tl.HITS: ak.place(sfx, t0, ak.glitch_sfx(0.12) if kind.startswith("negative") else ak.shutter(), -12)
    if "end" in tl.TYPE: ak.place(sfx, tl.TYPE["end"][0], ak.sparkle(), -12)

    # ---- 4. voice-over (optional): a user VO file, or a local TTS voice. No voice -> no VO.
    vo = ak.bus(L); regions = []
    lines = {float(t): ("file", p) for t, p in USER_VO.items()}
    lines.update({float(t): ("tts", tk) for t, tk in tl.VO.items() if float(t) not in lines})
    for t0 in sorted(lines):
        how, val = lines[t0]
        try:
            if how == "file": x = load_wav(val).mean(1)
            else: text, kind = val; x = ak.vo_fx(ak.tts(text, f"audio/vo_{t0:.2f}.wav"), kind)
        except RuntimeError as e:
            print(f"audio.py: VO at {t0:.2f} s skipped: {e}"); continue
        ak.place(vo, t0, x, -2); regions.append((t0, t0 + len(x) / ak.SR))
    if regions: music = ak.duck(music, regions, to=0.45)

    n = int(L * ak.SR)
    fit = lambda x: np.pad(x[:n], ((0, max(0, n - len(x[:n]))), (0, 0)))
    mix = fit(music) + fit(sfx) + fit(vo)
    ak.master(mix, "out/audio.wav")
    if len(sys.argv) > 1:
        v = sys.argv[1]; ak.mux(v, "out/audio.wav", os.path.splitext(v)[0] + "_final.mp4", max_mb=MAX_MB)

if __name__ == "__main__":
    main()
