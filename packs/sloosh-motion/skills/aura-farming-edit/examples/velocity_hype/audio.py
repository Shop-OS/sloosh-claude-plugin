"""audio.py: the aura edit's original score, SFX and voice lines on the SAME timeline as the picture.

  python3 audio.py                         -> out/audio.wav (-14 LUFS / -2 dBTP) + RMS per 2 s
  python3 audio.py out/<name>_vN.mp4       -> also muxes out/<name>_vN_final.mp4 (< 30 MB)
  python3 audio.py --no-vo [video.mp4]     -> skip the voice lines
Arrangement: filtered drift-phonk tease + heartbeats -> announcer over the tease -> TAPE-STOP psych -> silence in the
breath -> the drop (impact + sub drop + full phonk) -> slams with shouts -> face-flicker shutter burst -> calm hold ->
end announcer. The agent cannot hear: read the RMS report, then ask the user to listen.

Voice lines use only a text-to-speech voice that is already on this computer. This script never downloads a voice.
If no local voice works, it prints a skip line and builds the mix without voice.
"""
import subprocess
import sys

sys.path.insert(0, "lib")

USER_TRACK = None                 # e.g. "audio/track.mp3": cut so its drop lands on tl.DROP (find it with the director's beatmap.py)
USER_DROP = None


def voice_bus(ak, tl, L):
    """Build the voice bus. Returns (bus, regions). Any failure skips voice instead of stopping the mix."""
    vo = ak.bus(L)
    regions = []
    for t0, (text, kind) in sorted(tl.VO.items(), key=lambda kv: float(kv[0])):
        t0 = float(t0)
        try:
            x = ak.vo_fx(ak.tts(text, "audio/vo_%.2f.wav" % t0), kind)
        except Exception as e:  # no local voice, or the engine failed
            print("  VO skipped (%s). Build continues without voice." % e)
            return ak.bus(L), []
        ak.place(vo, t0, x, -1 if kind != "normal" else -3)
        end = t0 + len(x) / ak.SR
        regions.append((t0, end))
        print("  VO %6.2f-%6.2f s  %-9s %s" % (t0, end, kind, text))
    return vo, regions


def main(argv):
    import numpy as np
    import audiokit as ak
    import tl
    from edit import SHOTS

    use_vo = "--no-vo" not in argv
    args = [a for a in argv if a != "--no-vo"]

    L, D, B, FPS = tl.LEN, tl.DROP, tl.B, tl.FPS
    cuts = sorted({round(s[0], 3) for s in SHOTS if s[0] > 0.05})

    # ---- 1. music
    if USER_TRACK:
        tmp = "audio/_track.wav"
        start, lead = max(0.0, USER_DROP - D), int(round(max(0.0, D - USER_DROP) * ak.SR))   # a track that drops before tl.DROP gets silence in front, so its drop still lands on tl.DROP
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "%.3f" % start, "-i", USER_TRACK,
                        "-t", "%.3f" % L, "-ar", str(ak.SR), "-ac", "2", tmp], check=True)
        from scipy.io import wavfile
        music = wavfile.read(tmp)[1].astype(np.float32) / 32768.0
        music = np.pad(music, ((lead, 0), (0, 0)))[:int(L * ak.SR)]
        music = np.pad(music, ((0, max(0, int(L * ak.SR) - len(music))), (0, 0)))
    else:
        music = ak.score(tl.GENRE, tl.BPM, L, D, tl.KEY, breath=D - tl.T_BREATH)

    # ---- 2. edits that follow the picture: the psych (tape-stop, then silence through the breath)
    music = ak.tape_stop(music, tl.T_PSYCH, 0.32)
    music = ak.gap(music, tl.T_PSYCH + 0.32, D)
    music = ak.lowpass_region(music, tl.T_CALM, tl.T_END, 2200, 0.8)          # the calm hold breathes; the lens look opens up

    # ---- 3. SFX from the shared cue list (each peak on its frame)
    sfx = ak.bus(L)
    for c in cuts:
        if c < tl.T_ANN - 0.05:
            ak.place(sfx, c - 0.22, ak.whoosh(0.3, seed=int(c * 100)), -16)    # whoosh into each build cut
    tints = ("red", "pink", "teal", "warm")
    for s in SHOTS:
        if s[0] >= D and any(x in tints for x in s[9].split()):
            ak.place(sfx, s[0], ak.shutter(), -15)                              # grade flashes click
    ak.place(sfx, tl.T_ANN, ak.subdrop(1.2), -12)                               # the tease opens under the announcer
    ak.place(sfx, tl.T_PSYCH, ak.glitch_sfx(0.3, seed=21), -13)                  # the psych
    ak.place(sfx, tl.T_BREATH - 0.45, ak.whoosh(0.45, up=True, seed=22), -12)   # sucked into the breath
    for k, w in enumerate(tl.TYPE["slams"]):
        ak.place(sfx, w, ak.impact(0.9, seed=30 + k), -8)                       # every slam hits
    for key in ("lockA_1", "lockA_2"):
        ak.place(sfx, tl.TYPE[key][0], ak.impact(0.7, seed=40), -13)
    for (t0, kind, n) in tl.HITS:
        if kind in ("negative", "threshold"):
            ak.place(sfx, t0, ak.glitch_sfx(0.12, seed=int(t0 * 10)), -12)
    for k in range(int(round(B * FPS))):
        ak.place(sfx, tl.T_FLICK + k / FPS, ak.shutter(), -11 + (k % 3))        # one shutter per face
    ak.place(sfx, tl.T_FLICK, ak.riser(B), -14)
    ak.place(sfx, tl.T_END, ak.subdrop(1.4), -10)

    # ---- 4. voice lines: a line on every lockup, slam and turn; music ducked to 45% under each line
    if use_vo:
        vo, regions = voice_bus(ak, tl, L)
    else:
        print("  VO off (--no-vo).")
        vo, regions = ak.bus(L), []
    if regions:
        music = ak.duck(music, regions, to=0.45)

    n = int(L * ak.SR)

    def fit(x):
        return np.pad(x[:n], ((0, max(0, n - len(x[:n]))), (0, 0)))

    # -2 dBTP, not -1: the AAC encode in mux() adds up to about 1 dB of true peak, and qa.py flags peaks above -1
    ak.master(fit(music) + fit(sfx) + fit(vo), "out/audio.wav", tp=-2.0)
    if args:
        v = args[0]
        ak.mux(v, "out/audio.wav", v.replace(".mp4", "_final.mp4"))


if __name__ == "__main__":
    main(sys.argv[1:])
