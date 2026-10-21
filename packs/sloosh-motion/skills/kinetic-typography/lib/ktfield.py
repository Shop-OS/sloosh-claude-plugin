"""ktfield.py: the coded background and type-film helpers for kinetic-typography films (used by edit.py and audio.py).

The type page (ui/kt_*.html) renders transparent PNGs. edit.py draws everything under and around it:
  Fields   colour fields from tl.FIELDS rows (t, bg, ink, accent, how): the field is fully in place AT t, so a wipe
           lands on the beat. how = cut | up | down | left | right | iris (wipes run over the 0.36 s before t).
           Optional soft hazes (tl.HAZES) and the finish grain stop flat colour from banding in H.264.
  Plate    optional generated backplate (one approved photoreal still, still first) with a slow push, a look
           (raw / dim / duo / bw), and an optional subject matte so the type can sit BEHIND the subject.
  camera_hits  beat punches on the whole composite (tl.PUNCH) and the zoom blur of type-as-camera scenes.
  sfx_cues     one SFX per word hit, read from the same TYPE scenes the page renders (tick, impact, shutter, ...).
"""
import math
import numpy as np
import cv2
import filmkit as fk

WIPE = 0.36

def _ease(u): u = min(1.0, max(0.0, u)); return 4 * u ** 3 if u < .5 else 1 - (-2 * u + 2) ** 3 / 2

class Fields:
    def __init__(self, rows, hazes=None):
        self.rows = sorted([tuple(r) for r in rows], key=lambda r: r[0]) or [(0.0, "#000000", "#FFFFFF", "#F6C945", "cut")]
        W, H = fk.W, fk.H
        yy, xx = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32) * 4
        self.yy, self.xx = yy, xx
        self.hazes = []
        home = self.rows[0][1]
        for hz in (hazes or []):            # (x, y, r, colour, alpha[, on_bg]): x, y, r fractions of W / H / max(W, H)
            x, y, r, col, a = hz[:5]; on = hz[5] if len(hz) > 5 else home     # hazes sit on the home field only (never muddy a dark block)
            g = np.exp(-(((xx - x * W) ** 2 + (yy - y * H) ** 2) / (2 * (r * max(W, H)) ** 2)))
            self.hazes.append((cv2.resize(g, (W, H))[..., None].astype(np.float32), fk.hex2bgr(col), a, on.lower()))
        self.cache = {}

    def solid(self, col):
        if col not in self.cache:
            img = np.empty((fk.H, fk.W, 3), np.float32); img[:] = fk.hex2bgr(col)
            for g, c, a, on in self.hazes:
                if on == col.lower(): img = img * (1 - g * a) + c * g * a
            self.cache[col] = np.clip(img, 0, 255).astype(np.uint8)
        return self.cache[col]

    def at(self, t):
        cur = self.rows[0]
        for r in self.rows:
            if r[0] <= t + 1e-6: cur = r
        return cur

    def render(self, t):
        cur = self.at(t); nxt = next((r for r in self.rows if r[0] > t + 1e-6), None)
        img = self.solid(cur[1])
        if nxt is None or (nxt[4] if len(nxt) > 4 else "cut") == "cut" or t < nxt[0] - WIPE: return img
        u = _ease((t - (nxt[0] - WIPE)) / WIPE); how = nxt[4]; W, H = fk.W, fk.H
        out = img.copy(); new = self.solid(nxt[1])
        if how == "up": y = int(H * (1 - u)); out[y:] = new[y:]
        elif how == "down": y = int(H * u); out[:y] = new[:y]
        elif how == "left": x = int(W * u); out[:, :x] = new[:, :x]
        elif how == "right": x = int(W * (1 - u)); out[:, x:] = new[:, x:]
        elif how == "iris":
            m = np.zeros((H, W), np.uint8); cv2.circle(m, (W // 2, H // 2), int(u * math.hypot(W, H) / 2 + 1), 255, -1)
            out = np.where(m[..., None] > 0, new, out)
        return out

class Plate:
    """An AI backplate (approved still) behind the type, with an optional matte so the subject sits IN FRONT of the type.
    PLATE = dict(path="plates/plate.jpg", matte="plates/plate_matte.png", t=[a, b], z=[1.0, 1.08], focus=[0.5, 0.45], look="dim")"""
    def __init__(self, path, t, matte=None, z=(1.0, 1.08), focus=(0.5, 0.45), look="dim", dark="#120d0a", light="#f2e9dc"):
        self.a, self.b = t; self.z0, self.z1 = z; self.fx, self.fy = focus; self.look, self.dark, self.light = look, dark, light
        im = cv2.imread(path, cv2.IMREAD_COLOR)
        if im is None: raise SystemExit(f"ktfield: missing plate {path}")
        self.img = fk.cover(im, fk.W, fk.H, fy=self.fy)
        self.m = None
        if matte:
            mm = cv2.imread(matte, cv2.IMREAD_UNCHANGED)
            if mm is None: raise SystemExit(f"ktfield: missing matte {matte}")
            mm = mm[..., 3] if mm.ndim == 3 and mm.shape[2] == 4 else (mm if mm.ndim == 2 else cv2.cvtColor(mm, cv2.COLOR_BGR2GRAY))
            self.m = fk.cover(cv2.merge([mm, mm, mm]), fk.W, fk.H, fy=self.fy)[..., :1].astype(np.float32) / 255.0
        self.graded = self._look(self.img)

    def _look(self, img):
        if self.look == "dim": return (img * 0.72).astype(np.uint8)
        if self.look == "duo": return fk.duotone(img, self.dark, self.light, 0.95)
        if self.look == "bw": g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY); return cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)
        return img

    def on(self, t): return self.a <= t < self.b
    def _z(self, t): return fk.lerp(self.z0, self.z1, fk.ease_in_out((t - self.a) / max(1e-6, self.b - self.a)))
    def under(self, t): return fk.camera(self.graded, self._z(t), self.fx, self.fy)
    def front(self, img, t):
        """composite the subject (same camera as the plate) over img, so the type sits behind it."""
        if self.m is None: return img
        z = self._z(t); sub = fk.camera(self.graded, z, self.fx, self.fy)
        a = fk.camera((self.m[..., 0] * 255).astype(np.uint8)[..., None].repeat(3, 2), z, self.fx, self.fy)[..., :1].astype(np.float32) / 255.0
        return (img * (1 - a) + sub * a).astype(np.uint8)

def scenes(tl): return (getattr(tl, "TYPE", {}) or {}).get("kt", [])

def zooms(tl):
    """type-as-camera windows (the page puts the letter counter at frame centre, so the blur is centred)."""
    return [(s["t"][1] - s.get("dur", 0.55), s["t"][1]) for s in scenes(tl) if s["move"] == "zoom"]

def camera_hits(img, t, punches=(), zoom_windows=()):
    z = 1.0
    for p in punches:
        if 0 <= t - p < 0.4: z *= 1 + 0.045 * math.exp(-(t - p) / 0.1)
    if z > 1.0005: img = fk.camera(img, z)
    for a, b in zoom_windows:
        if a <= t < b: img = fk.zblur(img, 0.32 * ((t - a) / (b - a)) ** 2)
    for p in punches:
        if 0 <= t - p < 0.15: img = fk.rgb_split(img, 10 * min(fk.W, fk.H) / 1080 * math.exp(-(t - p) / 0.05))
    return img

def flash_now(t, zoom_windows=(), fps=30):
    return any(0 <= t - b < 2 / fps for _, b in zoom_windows)

def flap_lock(s, i): return s["t"][0] + s.get("roll", 0.45) + i * s.get("step", 0.05)     # same formula as KT.flapLock

def sfx_cues(tl, layer=False):
    """[(time, name, gain_db)]: one SFX per word hit, from the same scenes the type page renders.
    names: tick impact shutter whoosh pop click sparkle subdrop riser glitch
    layer=True (caption layer over another style): only the type scenes; the base film's audio.py owns HITS and cuts."""
    out, B = [], tl.B
    for s in scenes(tl):
        a, b = s["t"]; mv = s["move"]; C = tl.COPY.get(s["id"], [])
        beats = s.get("beats") or [a + i * B for i in range(max(1, len(C)))]
        if mv in ("stack", "rise"):
            out += [(x, "tick", -15) for x in beats]
        elif mv == "slam":
            out += [(x, "impact", -12 if i < len(beats) - 1 else -9) for i, x in enumerate(beats)]
        elif mv == "stretch":
            out += [(x - 0.12, "whoosh", -15) for x in beats]
        elif mv == "frame":
            out += [(beats[0], "impact", -8), (beats[0], "subdrop", -12)]
        elif mv == "echo":
            out += [(beats[0], "impact", -9)] + [(x, "shutter", -12) for x in beats[1:]]
        elif mv == "flap":
            txt = str(C[0]) if C else ""
            out += [(flap_lock(s, i), "tick", -19) for i, ch in enumerate(txt) if ch != " "] + [(a, "whoosh", -18)]
        elif mv == "count":
            d = s.get("dur", 0.9); n = 10
            out += [(beats[0] + d * (1 - (1 - k / n) ** 0.5), "tick", -20) for k in range(n)] + [(beats[0] + d, "impact", -11)]
        elif mv == "list":
            out += [(x, "tick", -16) for x in beats[:-1]] + [(beats[-1], "pop", -12)]
        elif mv == "grid":
            out += [(x, "shutter", -12) for x in beats]
        elif mv == "zoom":
            out += [(beats[0], "impact", -11), (b - 0.22, "whoosh", -11), (b, "subdrop", -10)]
        elif mv == "lyric":
            out += [(x, "tick", -20) for x in beats]
        elif mv == "lockA":
            out += [(a - 0.1, "whoosh", -16)]
        elif mv == "swap":
            out += [(beats[0], "tick", -16), (beats[1] if len(beats) > 1 else a + B, "pop", -13)]
        elif mv == "wave":
            out += [(x, "shutter", -13) for x in s.get("beats", [])]
        elif mv == "end":
            out += [(a, "impact", -13), (a + 0.3, "sparkle", -14)]
        for (ti, *_rest) in s.get("inv", []) if mv in ("stack", "rise") else []:
            out.append((ti, "shutter", -13))
        if mv in ("slam", "lyric"):
            for k in s.get("inv", []):
                if k < len(beats): out.append((beats[k], "shutter", -13))
        for (ti, *_r) in s.get("strike", []): out.append((ti, "click", -14))
    if layer: return sorted(out)
    for r in getattr(tl, "FIELDS", [])[1:]:
        if len(r) > 4 and r[4] != "cut": out.append((r[0] - 0.2, "whoosh", -16))
    for (ti, kind, n) in getattr(tl, "HITS", []):
        out.append((ti, "glitch" if kind.startswith("negative") or kind == "glitch" else "shutter", -12))
    return sorted(out)
