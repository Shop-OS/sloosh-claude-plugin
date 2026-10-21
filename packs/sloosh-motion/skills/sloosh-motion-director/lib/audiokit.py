"""audiokit.py: original score, sound design and voice-over, built in code to the picture.

All audio is synthesised with NumPy/SciPy against the SAME timeline as the video (tl.py). Nothing is copied from a
reference. audio.py (per film) imports this and tl, writes the arrangement, and calls master().

Building blocks (all mono float32 at SR unless noted; place() mixes into a stereo bus):
  drums    kick, clap, snare, hat, snare_roll, tom
  tonal    bass808, cowbell, pad, pluck, keys, sub, stab
  sfx      whoosh, riser, impact, subdrop, click, pop, sparkle, tick, shutter, glitch, heartbeat, swell
  edits    tape_stop(bus, t, len), lowpass_region(bus, a, b, hz, level), duck(bus, regions, to=0.45), gap(bus, a, b)
  scores   score(genre, tl...): phonk | trap | techno | house | luxury | cinematic | ambient, arranged around the drop
  voice    tts(text) -> Kokoro or Piper, only if already installed with a local voice; vo_fx(x, 'normal|shout|announcer')
           tts() never downloads anything. Without a local voice it raises: skip the VO or use the user's VO file.
  master   master(bus, 'out/audio.wav') -> two-pass loudnorm to -14 LUFS / -2 dBTP; rms_report() per 2 s window
  mux      mux('out/film_v3.mp4', 'out/audio.wav', 'out/film_v3_final.mp4', max_mb=30)  (max_mb: the delivery size cap)
           mux measures the final file and turns the AAC down if its true peak is above -1 dBTP; loudness(path) -> (LUFS, dBTP)
"""
import importlib.util, json, math, os, re, subprocess, sys
import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 48000
NOTE = {n: i for i, n in enumerate(["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"])}
NOTE.update({"Db": 1, "Eb": 3, "Gb": 6, "Ab": 8, "Bb": 10})

def hz(n):
    """'F#2' -> Hz"""
    m = re.match(r"([A-G][#b]?)(-?\d)", n); return 440.0 * 2 ** ((NOTE[m.group(1)] + 12 * (int(m.group(2)) + 1) - 69) / 12)

def T(sec): return np.arange(int(sec * SR)) / SR
def bus(sec): return np.zeros((int(sec * SR) + SR, 2), np.float32)
def db(x): return 10 ** (x / 20)
def env(n, a=0.002, d=0.2, s=0.0, r=0.05, hold=0.0):
    t = np.arange(n) / SR; e = np.where(t < a, t / max(a, 1e-6), 1.0)
    dec = np.exp(-(t - a - hold).clip(0) / max(d, 1e-6)) * (1 - s) + s
    e = np.where(t < a, e, dec); tail = int(r * SR)
    if tail and n > tail: e[-tail:] *= np.linspace(1, 0, tail)
    return e.astype(np.float32)

def _sos(kind, f, order=2):
    nyq = SR / 2
    if kind == "bp": return signal.butter(order, [max(20, f[0]) / nyq, min(f[1], nyq * 0.95) / nyq], "bandpass", output="sos")
    return signal.butter(order, min(f, nyq * 0.95) / nyq, kind, output="sos")
def lp(x, f, o=2): return signal.sosfilt(_sos("low", f, o), x, axis=0).astype(np.float32)
def hp(x, f, o=2): return signal.sosfilt(_sos("high", f, o), x, axis=0).astype(np.float32)
def bp(x, lo, hi, o=2): return signal.sosfilt(_sos("bp", (lo, hi), o), x, axis=0).astype(np.float32)
def sat(x, drive=2.0): return (np.tanh(x * drive) / np.tanh(drive)).astype(np.float32)
def noise(sec, seed=0): return np.random.default_rng(seed).uniform(-1, 1, int(sec * SR)).astype(np.float32)
def sine(f, sec, ph=0): t = T(sec); return np.sin(2 * np.pi * f * t + ph).astype(np.float32)
def sweep(f0, f1, sec, curve=3.0):
    t = T(sec); u = t / sec; f = f0 + (f1 - f0) * (1 - np.exp(-curve * u)) / (1 - np.exp(-curve)); return np.sin(2 * np.pi * np.cumsum(f) / SR).astype(np.float32)
def square(f, sec, duty=0.5): t = T(sec); return np.where((t * f) % 1 < duty, 1.0, -1.0).astype(np.float32)
def saw(f, sec): t = T(sec); return (2 * ((t * f) % 1) - 1).astype(np.float32)

def reverb(x, sec=1.2, mix=0.22, seed=3, damp=6000):
    ir = noise(sec, seed) * np.exp(-np.arange(int(sec * SR)) / (SR * sec / 5)); ir = lp(ir, damp); ir /= np.abs(ir).sum() ** 0.5 * 30
    if x.ndim == 1: return (x * (1 - mix) + signal.fftconvolve(x, ir)[:len(x)] * mix).astype(np.float32)
    return np.stack([x[:, c] * (1 - mix) + signal.fftconvolve(x[:, c], np.roll(ir, 37 * c))[:len(x)] * mix for c in range(2)], 1).astype(np.float32)

def place(dst, t, sig, gain_db=0.0, pan=0.0):
    """mix mono or stereo `sig` into stereo bus `dst` starting at time t (s); pan -1..1 (equal power)."""
    i = int(round(t * SR))
    if i >= len(dst) or len(sig) == 0: return dst
    if i < 0: sig = sig[-i:]; i = 0
    n = min(len(sig), len(dst) - i); g = db(gain_db)
    if sig.ndim == 1:
        l, r = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
        dst[i:i + n, 0] += sig[:n] * g * l * 1.414; dst[i:i + n, 1] += sig[:n] * g * r * 1.414
    else: dst[i:i + n] += sig[:n] * g
    return dst

# ------------------------------------------------------------------ drums
def kick(f0=150, f1=44, sec=0.45, click=0.6, drive=1.6):
    s = sweep(f0, f1, sec, 9) * env(int(sec * SR), 0.001, sec * 0.45)
    c = hp(noise(0.012, 1), 2000) * np.linspace(1, 0, int(0.012 * SR)) * click
    s[:len(c)] += c; return sat(s, drive) * 0.9
def clap(seed=2):
    n = noise(0.35, seed); e = np.zeros_like(n)
    for k, off in enumerate([0, 0.011, 0.022]): i = int(off * SR); e[i:] = np.maximum(e[i:], np.exp(-np.arange(len(e) - i) / (SR * (0.006 if k < 2 else 0.12))))
    return reverb(bp(n * e, 900, 5200), 0.4, 0.2) * 0.8
def snare(seed=4): return (bp(noise(0.3, seed), 1500, 8000) * env(int(0.3 * SR), 0.001, 0.09) * 0.7 + sine(190, 0.3) * env(int(0.3 * SR), 0.001, 0.05) * 0.5).astype(np.float32)
def hat(open_=False, seed=5):
    sec = 0.32 if open_ else 0.06; return hp(noise(sec, seed), 7000, 4) * env(int(sec * SR), 0.0005, 0.12 if open_ else 0.018) * 0.45
def tom(f=110): return (sweep(f * 1.6, f, 0.5, 6) * env(int(0.5 * SR), 0.001, 0.22)).astype(np.float32) * 0.8
def snare_roll(sec, start_rate=8, end_rate=32, seed=6):
    out = np.zeros(int(sec * SR) + SR, np.float32); t = 0.0; k = 0
    while t < sec:
        u = t / sec; rate = start_rate + (end_rate - start_rate) * u ** 2; s = snare(seed + k) * (0.35 + 0.65 * u)
        i = int(t * SR); out[i:i + len(s)] += s[:len(out) - i]; t += 1 / rate; k += 1
    return out[:int(sec * SR) + int(0.3 * SR)]

# ------------------------------------------------------------------ tonal
def bass808(f, sec, glide_from=None, drive=4.5, cut=900):
    t = T(sec); fr = np.full_like(t, f) if glide_from is None else f + (glide_from - f) * np.exp(-t / 0.06)
    x = np.sin(2 * np.pi * np.cumsum(fr) / SR) * env(len(t), 0.003, sec * 0.8, 0.0, 0.03)
    return lp(sat(x, drive), cut) * 0.55
def cowbell(f, sec=0.22):
    """two detuned squares (ratio 1.48), band-passed 600 Hz-4.2 kHz, short decay (the phonk lead)"""
    x = square(f, sec) + square(f * 1.48, sec); return sat(bp(x, 600, 4200) * env(int(sec * SR), 0.001, 0.07), 1.3) * 0.32
def pad(freqs, sec, cut=1800, detune=0.006, a=0.4):
    x = sum(saw(f * (1 + d), sec) for f in freqs for d in (-detune, 0, detune)) / (3 * len(freqs))
    return lp(x, cut) * env(int(sec * SR), a, 9e9, 1.0, min(0.6, sec * 0.3)) * 0.5
def pluck(f, sec=0.4, cut=3000): return lp(saw(f, sec) * env(int(sec * SR), 0.001, 0.12), cut) * 0.35
def keys(f, sec=1.6):
    """felt-piano-ish: additive partials with a fast attack and long decay"""
    x = sum(sine(f * k, sec) * (0.6 / k ** 1.3) * env(int(sec * SR), 0.002, sec * (0.5 / k)) for k in range(1, 7))
    return reverb(x.astype(np.float32), 1.6, 0.3) * 0.5
def sub(f, sec): return sine(f, sec) * env(int(sec * SR), 0.3, 9e9, 1.0, 0.5) * 0.4
def stab(freqs, sec=0.25, cut=2500): return lp(sum(saw(f, sec) for f in freqs) / len(freqs), cut) * env(int(sec * SR), 0.002, 0.08) * 0.5

# ------------------------------------------------------------------ sound effects (peak lands on t when placed at t - lead)
def whoosh(sec=0.5, up=True, seed=7):
    n = noise(sec, seed); u = np.linspace(0, 1, len(n)); shape = np.sin(np.pi * u) ** 2
    out = np.zeros_like(n); step = int(SR * 0.01); zi = None
    for i in range(0, len(n), step):                 # the filter state carries over, so the 10 ms steps do not click
        f = 400 + (5000 if up else 2500) * (u[i] if up else 1 - u[i]); sos = _sos("bp", (f * 0.6, f * 1.4))
        zi = np.zeros((sos.shape[0], 2)) if zi is None else zi; out[i:i + step], zi = signal.sosfilt(sos, n[i:i + step], zi=zi)
    return reverb(out * shape * 1.6, 0.5, 0.25)
def riser(sec=2.0, seed=8):
    n = noise(sec, seed); u = np.linspace(0, 1, len(n))
    return (hp(n, 800) * u ** 2 * 0.5 + sweep(200, 1600, sec, 1.5) * u ** 3 * 0.25).astype(np.float32)
def impact(sec=2.2, seed=9):
    body = sweep(90, 32, sec, 5) * env(int(sec * SR), 0.001, 0.5) * 1.0
    crack = lp(noise(sec, seed), 3000) * env(int(sec * SR), 0.0005, 0.08) * 0.8
    return reverb(sat((body + crack).astype(np.float32), 2.0), 2.0, 0.35)
def subdrop(sec=1.4): return (sweep(110, 30, sec, 3) * env(int(sec * SR), 0.005, sec * 0.5)).astype(np.float32) * 0.9
def click():
    """UI click: a short 2.4 kHz sine plus a noise tick"""
    n = int(0.03 * SR); x = sine(2400, 0.03) * env(n, 0.0005, 0.006); x[:int(0.01 * SR)] += hp(noise(0.01, 11), 4000) * np.linspace(0.4, 0, int(0.01 * SR))
    return x.astype(np.float32) * 0.7
def pop(f=900): return (sweep(f * 1.8, f, 0.08, 8) * env(int(0.08 * SR), 0.0008, 0.025)).astype(np.float32) * 0.6
def sparkle(root=1568):
    out = np.zeros(int(0.9 * SR), np.float32)
    for k, m in enumerate([1, 1.25, 1.5, 2, 2.5]):
        s = sine(root * m, 0.5) * env(int(0.5 * SR), 0.001, 0.12) * 0.25; i = int(k * 0.045 * SR); out[i:i + len(s)] += s
    return reverb(out, 0.9, 0.35)
def tick(seed=12): return hp(noise(0.015, seed), 3000) * env(int(0.015 * SR), 0.0003, 0.004) * 0.5
def shutter(): return (hp(noise(0.06, 13), 2500) * env(int(0.06 * SR), 0.0005, 0.012) * 0.7).astype(np.float32)
def glitch_sfx(sec=0.25, seed=14):
    r = np.random.default_rng(seed); x = np.zeros(int(sec * SR), np.float32); i = 0
    while i < len(x):
        L = int(r.integers(200, 2400)); f = float(r.choice([80, 220, 880, 1760, 3520]))
        seg_ = square(f, L / SR + 0.01) * 0.4 if r.random() < 0.6 else noise(L / SR + 0.01, int(r.integers(1e6))) * 0.5
        n_ = len(x[i:i + L]); x[i:i + n_] = seg_[:n_]; i += L
    return bp(x, 150, 9000)
def heartbeat(): b = sine(55, 0.18) * env(int(0.18 * SR), 0.002, 0.05); out = np.zeros(int(0.5 * SR), np.float32); out[:len(b)] += b; out[int(0.2 * SR):int(0.2 * SR) + len(b)] += b * 0.7; return lp(out, 200)
def swell(freqs, sec=1.6): return pad(freqs, sec, 2400, a=sec * 0.8)

# ------------------------------------------------------------------ edits on a bus
def tape_stop(b, t, sec=0.32):
    """playback rate falls to zero over `sec` from t, then silence (the "psych")"""
    i0 = int(t * SR); n = int(sec * SR)
    if i0 + n >= len(b): return b
    rate = np.linspace(1, 0, n) ** 1.5; pos = i0 + np.cumsum(rate)
    for c in range(2): b[i0:i0 + n, c] = np.interp(pos, np.arange(len(b)), b[:, c])
    b[i0 + n:i0 + n + int(0.02 * SR)] *= np.linspace(1, 0, int(0.02 * SR))[:, None]
    return b
def gap(b, a, z): b[int(a * SR):int(z * SR)] = 0; return b
def lowpass_region(b, a, z, cut=1400, level=0.6):
    i, j = int(a * SR), int(z * SR); b[i:j] = lp(b[i:j], cut) * level; return b
def duck(b, regions, to=0.45, fade=0.04):
    """sidechain-style ducking: music falls to `to` (45%) under each (start, end) region, e.g. every VO line"""
    g = np.ones(len(b), np.float32); f = int(fade * SR)
    for a, z in regions:
        i, j = int(a * SR), int(z * SR); g[i:j] = np.minimum(g[i:j], to)
        g[max(0, i - f):i] = np.minimum(g[max(0, i - f):i], np.linspace(1, to, len(g[max(0, i - f):i])))
        g[j:j + f] = np.minimum(g[j:j + f], np.linspace(to, 1, len(g[j:j + f])))
    return b * g[:, None]

# ------------------------------------------------------------------ scores (arranged around the picture)
MAJOR, MINOR = [0, 2, 4, 5, 7, 9, 11], [0, 2, 3, 5, 7, 8, 10]
KEYS = {r + q: (r, sc) for r in NOTE for q, sc in (("", MAJOR), ("m", MINOR))}   # every major and minor key: "F#m", "Bb", "Ebm" ...
def _key(key):
    if key not in KEYS: raise ValueError(f"audiokit: unknown key {key!r}. Use a root ({', '.join(NOTE)}), plus 'm' for minor: for example 'F#m', 'Bb' or 'Ebm'.")
    return KEYS[key]
def deg(key, d, octave=3):
    root, sc = _key(key); o = octave + d // 7; return hz(f"{root}{o}") * 2 ** (sc[d % 7] / 12)
def chord(key, d, octave=3): return [deg(key, d, octave), deg(key, d + 2, octave), deg(key, d + 4, octave)]

def score(genre, bpm, length, drop, key="F#m", intro="tease", breath=0.0, end_hit=True, seed=1):
    """An original track, arranged to the picture: a sparse intro (filtered), a riser into `drop`, an optional silent
    breath of `breath` s right before the drop, the full groove from the drop, and a tail. Returns a stereo bus.
    Genres: phonk (drift phonk: cowbell, 808 glides, syncopated kick, clap on 2 and 4, 16th hats with rolls),
    trap, techno, house, luxury (felt keys + low strings + sub), cinematic (hybrid toms, braams), ambient."""
    B = 60.0 / bpm; out = bus(length); rng = np.random.default_rng(seed)
    beats = np.arange(-64, int(length / B) + 2) * B + (drop % (4 * B))       # grid aligned so a bar line hits the drop
    beats = beats[(beats >= 0) & (beats < length)]
    prog = {"phonk": [0, 0, 5, 4], "trap": [0, 5, 3, 4], "techno": [0, 0, 0, 0], "house": [0, 5, 3, 6], "luxury": [0, 5, 3, 4],
            "cinematic": [0, 5, 2, 6], "ambient": [0, 3, 5, 4]}[genre]
    for bi, t in enumerate(beats):
        post = t >= drop - 1e-6; bar = int(round((t - drop) / B)) // 4; step = int(round((t - drop) / B)) % 4
        d = prog[bar % 4]; lvl = 0.0 if (breath and drop - breath <= t < drop) else 1.0
        if lvl == 0: continue
        if genre == "phonk":
            if post:
                if step in (0,) or (step == 2 and bar % 2 == 0): place(out, t, kick(), -2)
                if step == 3 and bar % 2: place(out, t + B / 2, kick(), -5)
                if step in (1, 3): place(out, t, clap(seed + bi), -6)
                if step == 0: place(out, t, bass808(deg(key, d, 1), 4 * B * 0.95, glide_from=deg(key, d, 2)), -4)
                for k in range(4):
                    roll = (bar % 4 == 3 and step == 3 and k >= 2)
                    for r in range(3 if roll else 1): place(out, t + k * B / 4 + r * B / 12, hat(seed=bi * 7 + k + r), -16 + (2 if k == 0 else 0), pan=0.25)
            if post or intro == "tease":
                for k, dd in enumerate([0, 2, 4, 2, 5, 4, 2, 1]):
                    if (k + step) % 2 == 0: place(out, t + k * B / 8 * 2 % B, cowbell(deg(key, d + dd, 4)), -10 if post else -12, pan=-0.4 if k % 2 else 0.4)
        elif genre == "trap":
            if post:
                if step == 0 or (step == 2 and rng.random() < .5): place(out, t, kick(120, 40), -3)
                if step == 2: place(out, t, snare(bi), -6); place(out, t, clap(bi), -9)
                if step == 0: place(out, t, bass808(deg(key, d, 1), 4 * B, glide_from=deg(key, d, 1) * 1.5), -4)
                for k in range(4 if bar % 2 else 2): place(out, t + k * B / (4 if bar % 2 else 2), hat(seed=bi + k), -15)
            if step == 0: place(out, t, pad(chord(key, d, 3), 4 * B, 1400), -14 if post else -12)
        elif genre in ("techno", "house"):
            if post or genre == "house":
                place(out, t, kick(130 if genre == "techno" else 120, 45), -2 if post else -14)
            if post:
                place(out, t + B / 2, hat(open_=genre == "house", seed=bi), -14)
                if genre == "house" and step in (1, 3): place(out, t, clap(bi), -8)
                if genre == "techno": place(out, t + B / 2, lp(saw(deg(key, d, 1), B / 2) * env(int(B / 2 * SR), 0.002, 0.08), 600), -6)
                else:
                    if step in (0, 2): place(out, t + B * 0.5, stab(chord(key, d, 4)), -10)
                    place(out, t, lp(saw(deg(key, d, 1), B * 0.4) * env(int(B * 0.4 * SR), 0.002, 0.1), 700), -7)
            if step == 0 and not post: place(out, t, pad(chord(key, d, 3), 4 * B, 900), -13)
        elif genre == "luxury":
            if step == 0: place(out, t, pad(chord(key, d, 2), 4 * B, 1200, a=0.8), -12); place(out, t, sub(deg(key, d, 1), 4 * B), -12)
            if step in (0, 2) or post: place(out, t, keys(deg(key, d + (0, 4, 2, 7)[step], 4), 2.0), -10, pan=0.15 * (step - 1.5))
            if post and step == 0: place(out, t, kick(90, 40, 0.6, 0.2, 1.2), -10)
        elif genre == "cinematic":
            if step == 0: place(out, t, pad(chord(key, d, 2), 4 * B, 900, a=1.0), -10)
            if post and step in (0, 2): place(out, t, tom(90 if step == 0 else 120), -6)
            if post and step == 3: place(out, t + B / 2, tom(150), -9)
        elif genre == "ambient":
            if step == 0: place(out, t, pad(chord(key, d, 3), 4 * B, 2200, a=1.5), -12)
            if rng.random() < .35: place(out, t, pluck(deg(key, int(rng.integers(0, 7)), 5), 0.8, 2500), -18, pan=float(rng.uniform(-.6, .6)))
    if intro and drop > 1.0:
        place(out, 0, sub(deg(key, 0, 1), drop), -7 if genre in ('phonk', 'trap', 'techno', 'house') else -16)   # sub drone under the intro
        if genre in ("phonk", "trap"):                                      # heartbeats speeding up toward the drop
            t = 0.0
            while t < drop - 2 * B:
                place(out, t, heartbeat(), -4); t += 2 * B if t < drop * 0.5 else B
        r = min(drop, 4 * B); place(out, drop - r, riser(r), -12)           # riser ends on the drop
        if genre in ("phonk", "trap", "techno", "house"): place(out, drop - min(drop, 2 * B), snare_roll(min(drop, 2 * B) - breath if breath else min(drop, 2 * B)), -12)
        out[:int(drop * SR)] = lp(out[:int(drop * SR)], 2600 if genre != "luxury" else 7000)   # intro is filtered; the drop opens up
    place(out, drop, impact(), -4); place(out, drop, subdrop(), -6)
    if end_hit: place(out, length - 1.2, impact(1.6), -10)
    tail = int(0.8 * SR); e = int(length * SR); out[e - tail:e] *= np.linspace(1, 0, tail)[:, None]; out[e:] = 0
    return out[:e]

# ------------------------------------------------------------------ voice-over
def _has(mod):
    try: return importlib.util.find_spec(mod) is not None
    except (ImportError, ValueError): return False

def _piper_voice():
    """a local Piper voice: $PIPER_VOICE (an .onnx path) or the first .onnx under ~/.cache/piper. Never downloads."""
    v = os.environ.get("PIPER_VOICE")
    if v and os.path.isfile(v): return v
    vdir = os.path.expanduser("~/.cache/piper")
    for root, _, files in os.walk(vdir):
        for f in sorted(files):
            if f.endswith(".onnx"): return os.path.join(root, f)
    return None

def tts(text, out_wav, voice=None):
    """Voice-over from a TTS engine that is ALREADY installed on this computer. Nothing is downloaded.
    Kokoro is used when the kokoro module and its English language model are installed (offline mode, so it only reads
    weights that are already cached). Otherwise Piper is used when the piper module and a local voice (.onnx) exist.
    With neither, this raises RuntimeError: make the film without a VO, or use a VO file the user supplies.
    Returns a float32 mono array at SR, with leading silence trimmed so the line starts on its cue."""
    os.makedirs(os.path.dirname(out_wav) or ".", exist_ok=True); ok = False; why = []
    if _has("kokoro") and _has("en_core_web_sm"):
        os.environ["HF_HUB_OFFLINE"] = "1"; os.environ["TRANSFORMERS_OFFLINE"] = "1"   # read cached weights only
        try:
            from kokoro import KPipeline
            pipe = KPipeline(lang_code="a"); chunks = [a for _, _, a in pipe(text, voice=voice or "am_michael")]
            wavfile.write(out_wav, 24000, np.concatenate(chunks).astype(np.float32)); ok = True
        except Exception as e:
            why.append(f"kokoro: {str(e)[:160]}")
    else:
        why.append("kokoro: not installed")
    if not ok:
        model = _piper_voice()
        if not _has("piper") or model is None:
            why.append("piper: not installed or no local voice (.onnx) in $PIPER_VOICE or ~/.cache/piper")
            raise RuntimeError("no local TTS voice (" + "; ".join(why) + "). Make the film without a VO, or use the "
                               "user's VO file. Ask the user before installing any TTS engine or voice.")
        r = subprocess.run([sys.executable, "-m", "piper", "-m", model, "-f", out_wav], input=text.encode(), capture_output=True)
        if r.returncode: raise RuntimeError("TTS failed: " + r.stderr.decode()[-300:])
    sr, x = wavfile.read(out_wav); x = x.astype(np.float32); x = x / (np.abs(x).max() + 1e-9)
    if x.ndim > 1: x = x.mean(1)
    x = signal.resample_poly(x, SR, sr).astype(np.float32)
    nz = np.where(np.abs(x) > 0.02)[0]; return x[nz[0]:nz[-1] + int(0.05 * SR)] if len(nz) else x

def pitch_speed(x, speed=0.85):
    """slow down and pitch down together, tape-style (0.85 = about -3 semitones): the heavy 'announcer' read"""
    return signal.resample(x, int(len(x) / speed)).astype(np.float32)
def vo_fx(x, kind="normal"):
    """compression (|x|^0.75), 2.5-6.5 kHz presence boost, high-pass 90 Hz, short room reverb.
    shout: + saturation and a 45 ms slap double. announcer: 0.85 speed (pitched down), driven."""
    if kind == "announcer": x = pitch_speed(x, 0.85); x = sat(x, 2.2)
    x = np.sign(x) * np.abs(x) ** 0.75; x = hp(x, 90) + bp(x, 2500, 6500) * 0.6
    if kind == "shout":
        x = sat(x, 2.5); d = int(0.045 * SR); y = np.zeros(len(x) + d, np.float32); y[:len(x)] += x; y[d:] += x * 0.5; x = y
    x = reverb(x.astype(np.float32), 0.6, 0.12); return (x / (np.abs(x).max() + 1e-9) * 0.9).astype(np.float32)

# ------------------------------------------------------------------ master, report, mux
def loudness(path):
    """(integrated LUFS, true peak dBTP) of any audio or video file, from ffmpeg ebur128; None where it cannot be read."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr); p = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r.stderr)
    return (float(i[-1]) if i else None, float(p[-1]) if p else None)

def master(b, out_wav, lufs=-14.0, tp=-2.0):
    """two-pass loudnorm. tp is -2 dBTP, not -1: the AAC encode in mux() adds up to about 1 dB of peak, and the final file must stay at or under -1 dBTP."""
    os.makedirs(os.path.dirname(out_wav) or ".", exist_ok=True); raw = os.path.splitext(out_wav)[0] + "_raw.wav"
    peak = np.abs(b).max() + 1e-9; wavfile.write(raw, SR, (b / peak * 0.8).astype(np.float32))
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", raw, "-af", f"loudnorm=I={lufs}:TP={tp}:LRA=9:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = json.loads(r.stderr[r.stderr.rfind("{"):r.stderr.rfind("}") + 1])
    af = (f"loudnorm=I={lufs}:TP={tp}:LRA=9:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
          f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", af, "-ar", str(SR), out_wav], check=True)
    os.remove(raw); print("audio ->", out_wav); rms_report(out_wav); return out_wav

def rms_report(wav, win=2.0):
    """You cannot hear the mix: print loudness per 2 s window to catch silent gaps or a too-loud section, then ask the user to listen."""
    sr, x = wavfile.read(wav); x = x.astype(np.float32) / (32768.0 if np.issubdtype(x.dtype, np.integer) else 1.0); x = x.mean(1) if x.ndim > 1 else x; n = int(win * sr)
    rows = [f"{k * win:4.0f}-{(k + 1) * win:<4.0f}s {20 * math.log10(np.sqrt(np.mean(x[k * n:(k + 1) * n] ** 2) + 1e-9)):6.1f} dBFS" for k in range(math.ceil(len(x) / n))]
    print("RMS per 2 s:\n  " + "\n  ".join(rows))
    i, p = loudness(wav); print(f"integrated {'?' if i is None else i} LUFS, true peak {'?' if p is None else p} dBTP")

def mux(video, audio, out, max_mb=30.0, tp=-1.0):
    """Encode the delivery file: H.264 + AAC 256k, sized under max_mb (default 30 MB; set it to the delivery size cap).
    Then measure the file: if the AAC true peak is above tp (-1 dBTP), the audio is encoded again, turned down by the excess."""
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video], capture_output=True, text=True).stdout)
    kbps = max(400, int((max_mb * 8192 * 0.94) / max(dur, 0.1) - 256))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow",
                    "-b:v", f"{min(kbps, 12000)}k", "-maxrate", f"{min(kbps, 12000) * 1.5:.0f}k", "-bufsize", f"{min(kbps, 12000) * 2}k",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", out], check=True)
    gain = 0.0
    for _ in range(3):                                   # the AAC encode can overshoot the master's peak: measure, never assume
        lu, pk = loudness(out)
        if pk is None or pk <= tp: break
        gain += tp - pk - 0.3; tmp = os.path.splitext(out)[0] + "_tp.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", out, "-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-af", f"volume={gain:.2f}dB",
                        "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", tmp], check=True)
        os.replace(tmp, out); print(f"mux: AAC true peak {pk:.1f} dBTP is above {tp:.1f}: audio encoded again at {gain:.2f} dB")
    lu, pk = loudness(out)
    print(f"final -> {out}  ({os.path.getsize(out) / 1e6:.1f} MB, {'?' if lu is None else lu} LUFS, true peak {'?' if pk is None else pk} dBTP)")
