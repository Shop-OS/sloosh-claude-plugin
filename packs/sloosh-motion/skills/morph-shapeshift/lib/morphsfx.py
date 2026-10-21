"""morphsfx.py: the morph style's sound effects, built on the core audiokit. Copy into the film's lib/.

  shimmer(sec)      a rising glassy shimmer: band-passed noise sweep + detuned high partials. One per visible morph,
                    PEAKING on the landing (place at landing - 0.8 * sec).
  morph_swell(sec)  a reversed reverb swell that sucks into the landing (photoreal transitions, logo morphs).
  goo(n)            liquid blips for goo splits / merges (n staggered pops, falling pitch).
  ring()            the send-morph ring pulse: a soft sine ping with a short tail, one per ring.
"""
import numpy as np
import audiokit as ak

def shimmer(sec=0.7, seed=21):
    n = int(sec * ak.SR); u = np.linspace(0, 1, n)
    air = ak.noise(sec, seed); out = np.zeros(n, np.float32); step = int(ak.SR * 0.01)
    for i in range(0, n, step):
        f = 2500 + 7000 * u[i]; out[i:i + step] = ak.bp(air[i:i + step + 64], f * 0.8, min(f * 1.25, 20000))[:len(out[i:i + step])]
    tone = sum(ak.sine(f, sec) * a for f, a in [(2637, .5), (2650, .4), (3951, .3), (5274, .2)])
    x = (out * 0.9 + tone * 0.18) * (u ** 1.6) * np.exp(-np.maximum(u - 0.8, 0) * 30)
    return ak.reverb(x.astype(np.float32), 1.1, 0.35)

def morph_swell(sec=0.9, seed=22):
    hit = ak.lp(ak.noise(0.25, seed), 4000) * ak.env(int(0.25 * ak.SR), 0.001, 0.08)
    x = ak.reverb(np.pad(hit, (0, int(sec * ak.SR))).astype(np.float32), sec, 0.9)     # pad: reverb keeps the input length
    x = x[: int(sec * ak.SR)][::-1].copy(); return (x / (np.abs(x).max() + 1e-9) * 0.7).astype(np.float32)

def goo(n=3, f=520):
    out = np.zeros(int((0.12 * n + 0.2) * ak.SR), np.float32)
    for k in range(n):
        p = ak.pop(f * (1 - 0.12 * k)); i = int(k * 0.06 * ak.SR); out[i:i + len(p)] += p
    return ak.lp(out, 2400)

def ring(f=1760):
    x = ak.sine(f, 0.5) * ak.env(int(0.5 * ak.SR), 0.002, 0.14) * 0.35; return ak.reverb(x.astype(np.float32), 0.8, 0.3)
