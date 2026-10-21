#!/usr/bin/env python3
"""beatmap.py — read a music track and give the edit its skeleton: BPM, beat grid, bar lines, the DROP, and cut points.

Never trust an auto beat grid blindly: the drop is found by a jump in low-band energy, then the grid is phase-locked to it.
Usage:
  python3 beatmap.py song.mp3                       -> prints summary + writes song.beatmap.json
  python3 beatmap.py song.mp3 --film 15 --drop-at 6 -> also computes where to START the song so its drop lands at film t=6s,
                                                       and lists beat times inside the 15 s film (for cuts / word hits)
Needs: numpy, ffmpeg on PATH.
"""
import argparse, json, shutil, subprocess
import numpy as np

FF = shutil.which("ffmpeg") or "ffmpeg"
SR = 22050

def load(path):
    raw = subprocess.run([FF, "-v", "quiet", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()

def envelope(x, hop=256):
    n = len(x) // hop
    return np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1)), SR / hop

def lowpass(x, k=60):
    return np.convolve(x, np.ones(k) / k, "same")

def bpm_estimate(env, fps):
    on = np.maximum(0, np.diff(np.log(env + 1e-6))); on -= on.mean()
    seg = on[: min(len(on), int(fps * 90))]
    ac = np.correlate(seg, seg, "full")[len(seg) - 1 :]
    best, score = 120.0, -1e9
    for lag in range(int(fps * 0.33), int(fps * 1.0)):  # 60-180 BPM
        s = ac[lag] + 0.5 * ac[min(len(ac) - 1, lag * 2)]
        if s > score: score, best = s, 60 * fps / lag
    while best < 75: best *= 2
    while best > 170: best /= 2
    return best, on

def find_drop(x):
    """Largest sustained jump in low-band energy (per half-second), refined to the onset within +-0.25 s."""
    low = lowpass(x)
    win = SR // 2
    n = len(low) // win
    e = np.array([10 * np.log10((low[i * win:(i + 1) * win] ** 2).mean() + 1e-12) for i in range(n)])
    if n < 10: return 0.0, 0.0                      # too short for a before/after window
    gains = [(np.mean(e[i:i + 4]) - np.mean(e[max(0, i - 4):i]), i) for i in range(4, n - 4)]
    g, i = max(gains)
    t0 = i * 0.5
    # refine: strongest 20 ms rise around t0
    a, b = int(max(0, t0 - 0.25) * SR), int(min(len(x) / SR, t0 + 0.25) * SR)
    seg = np.abs(x[a:b]); step = int(0.02 * SR)
    if len(seg) > 2 * step:
        rms = np.array([seg[j:j + step].mean() for j in range(0, len(seg) - step, step)])
        j = int(np.argmax(np.diff(rms))) + 1
        t0 = (a + j * step) / SR
    return round(float(t0), 3), round(float(g), 1)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("song"); ap.add_argument("--film", type=float, default=None, help="film length in s")
    ap.add_argument("--drop-at", type=float, default=None, help="film time where the drop must land")
    a = ap.parse_args()
    x = load(a.song); dur = len(x) / SR
    env, fps = envelope(x)
    bpm, on = bpm_estimate(env, fps)
    drop, gain = find_drop(x)
    beat = 60 / bpm
    # phase-lock grid to the drop (drop is a downbeat in almost all modern tracks)
    first = drop % beat
    beats = [round(first + k * beat, 3) for k in range(int((dur - first) / beat) + 1)]
    bars = [b for i, b in enumerate(beats) if (round((b - drop) / beat)) % 4 == 0]
    out = {"file": a.song, "duration": round(dur, 2), "bpm": round(bpm, 2), "beat_s": round(beat, 4),
           "drop_s": drop, "drop_gain_db": gain, "beats": beats, "bars": bars}
    if a.film and a.drop_at is not None:
        start = round(drop - a.drop_at, 3)
        film_beats = [round(b - start, 3) for b in beats if 0 <= b - start <= a.film]
        out.update({"song_start_s": start, "film_beats": film_beats,
                    "film_bars": [round(b - start, 3) for b in bars if 0 <= b - start <= a.film],
                    "note": "trim the song from song_start_s; cut on film_beats; biggest visual moment on drop_at"})
        if start < 0: out["warning"] = "drop comes too early in the song for this drop-at; lower --drop-at or pick another track"
    path = a.song.rsplit(".", 1)[0] + ".beatmap.json"
    with open(path, "w", encoding="utf-8") as f: json.dump(out, f, indent=1)
    print(f"BPM ~{out['bpm']} (beat {out['beat_s']} s) | drop at {drop} s (+{gain} dB low band) | {len(beats)} beats")
    if "song_start_s" in out:
        print(f"start song at {out['song_start_s']} s -> drop lands at film {a.drop_at} s | film beats: {out['film_beats'][:24]}")
    print("->", path)

if __name__ == "__main__":
    main()
