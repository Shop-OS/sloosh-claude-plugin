"""aurakit.py: the aura-edit moves on top of the core filmkit.

scripts/new_aura_film.sh copies this file into a film's lib/ next to filmkit.py.
Everything here is a pure function of t (or of the frame number), so render(t) stays exact and repeatable.

  shots(rows)                 cut-list rows -> Shots; rows tagged `velo` / `velo:<hit>` get the flash-in velocity curve
  FaceFlicker(faces, t0, dur) the face-flicker burst: up to 12 face images, one per frame, each ghosted 70/30 into the
                              previous one, cycling through 6 colour gains, every 4th frame blurred
  psych(img, t, t0, t1)       the pre-drop psych strobe: inverted every other frame, zoom blur, colour split, darkening
  hits(img, t, events)        fk.hits plus aura kinds: threshold (1-bit), duo-blue, duo-red, eyes:<y>, grid, black
  threshold / eye_strip / clone_grid / letterbox / polaroid   the sub-preset signature frames
  ease_back(u)                overshoot easing for the polaroid pop-in
"""
import math
import numpy as np
import cv2
import filmkit as fk

def upx(v):
    """v pixels on a frame whose short side is 1080, scaled to this frame (9:16, 16:9, 1:1 and 4:5 alike)."""
    return v * min(fk.W, fk.H) / 1080

# ------------------------------------------------------------------ velocity ("flash-in") speed ramp
def velo_speed(u, hit=0.0, fast=2.0, slow=0.25, out=1.8, hold=0.45, ease=0.12):
    """Speed multiplier at shot progress u (0..1). Fast approach -> eases to `slow` AT `hit` -> holds -> accelerates out.
    Never below 0.25 on generated footage (interpolation warps hands and hair)."""
    if u < hit - ease: return fast
    if u < hit: return fk.lerp(fast, slow, fk.ease_in_out((u - (hit - ease)) / ease))
    if u < hit + hold: return slow
    return fk.lerp(slow, out, fk.ease_in_out((u - hit - hold) / max(1e-6, 1 - hit - hold)))

class VShot(fk.Shot):
    """A Shot whose source time follows the velocity curve (tag `velo`, or `velo:0.4` to put the slowest point 40% in)."""
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        h = float(self.arg("velo")[0]) if self.arg("velo") else 0.0
        us = np.linspace(0, 1, 241); sp = np.array([velo_speed(x, h) for x in us])
        self._cum = np.concatenate([[0], np.cumsum((sp[1:] + sp[:-1]) / 2 * np.diff(us))])   # integral of speed du

    def src_time(self, lt):
        u = fk.clamp01(lt / max(self.dur, 1e-6))
        return self.inp + float(np.interp(u, np.linspace(0, 1, 241), self._cum)) * self.dur * self.speed

def shots(rows):
    """Turn cut-list tuples into Shots for fk.CutList; `velo` rows become VShots."""
    out = []
    for r in rows:
        tags = r[9] if len(r) > 9 else ""
        out.append(VShot(*r) if any(t == "velo" or t.startswith("velo:") for t in tags.split()) else fk.Shot(*r))
    return out

# ------------------------------------------------------------------ the face-flicker burst (one beat: about 14 frames at 130 BPM and 30 fps)
GAINS = [(0.80, 0.85, 1.35), (1.30, 1.05, 0.70), (0.75, 1.30, 0.95), (1.25, 0.70, 1.20), (1.10, 1.10, 1.10), (0.70, 0.90, 1.45)]  # BGR

class FaceFlicker:
    """faces: up to 12 entries (source, source_time, zoom, focus_x, focus_y). Sources are approved stills or clips
    (clean-window frames); zoom/focus put each face at its own scale so the burst jumps. One face per frame.
    Frame k = 0.7 * face_k (colour gain k % 6, Gaussian-blurred when k % 4 == 3) + 0.3 * frame k-1."""
    def __init__(self, faces, start, dur, ghost=0.7):
        self.faces, self.start, self.dur, self.ghost = faces, start, dur, ghost
        self.cache = {}

    def active(self, t): return self.start - 1e-6 <= t < self.start + self.dur - 1e-6

    def _face(self, k):
        src, st, z, fx, fy = self.faces[k % len(self.faces)]
        img = fk.camera(fk.Clip.get(src).frame(st), z, fx, fy)
        img = np.clip(img.astype(np.float32) * np.array(GAINS[k % len(GAINS)], np.float32), 0, 255)
        if k % 4 == 3: img = cv2.GaussianBlur(img, (0, 0), upx(7))
        return img

    def frame(self, t):
        k = fk.frame_of(t) - fk.frame_of(self.start)
        if k in self.cache: return self.cache[k]
        prev = self.frame(self.start + (k - 1) / fk.FPS).astype(np.float32) if k > 0 else None
        cur = self._face(k)
        out = cur if prev is None else self.ghost * cur + (1 - self.ghost) * prev
        out = out.astype(np.uint8)
        if len(self.cache) > 40: self.cache.clear()
        self.cache[k] = out; return out

# ------------------------------------------------------------------ the psych (tape-stop strobe before the drop)
def psych(img, t, t0, t1):
    """Inverted frames on every other frame, zoom blur growing, colour split, the image darkening toward the breath."""
    u = fk.clamp01((t - t0) / max(t1 - t0, 1e-6)); f = fk.frame_of(t)
    img = fk.zblur(img, 0.05 + 0.22 * u)
    if f % 2 == 0: img = fk.negative(img)
    img = fk.rgb_split(img, upx(6 + 20 * u))
    return (img.astype(np.float32) * (1 - 0.5 * u)).astype(np.uint8)

# ------------------------------------------------------------------ signature frames (sub-presets)
def threshold(img, level=118):
    """1-bit black/white: the signature frame of the dark preset."""
    g = cv2.GaussianBlur(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), (0, 0), 1.2)
    return cv2.cvtColor(np.where(g > level, 255, 0).astype(np.uint8), cv2.COLOR_GRAY2BGR)

def eye_strip(img, eye_y=0.38, h=0.09):
    """Eye strip: the frame blown to white, only a horizontal strip at the eyes left (crushed and contrasty)."""
    out = fk.whiteout(img, 0.95); y0 = int((eye_y - h / 2) * fk.H); y1 = int((eye_y + h / 2) * fk.H)
    strip = cv2.convertScaleAbs(img[y0:y1], alpha=1.5, beta=-60); out[y0:y1] = strip; return out

def clone_grid(img, n=3, bw=True):
    """the subject repeated n x n (B/W), 3 px black gutters."""
    s = cv2.resize(img, (fk.W // n, fk.H // n), interpolation=cv2.INTER_AREA)
    if bw: s = cv2.cvtColor(cv2.equalizeHist(cv2.cvtColor(s, cv2.COLOR_BGR2GRAY)), cv2.COLOR_GRAY2BGR)
    g = np.zeros((fk.H, fk.W, 3), np.uint8); hh, ww = s.shape[:2]
    for r in range(n):
        for c in range(n): g[r * hh:(r + 1) * hh, c * ww:(c + 1) * ww] = s
    g[:, ::max(1, fk.W // n)] = 0; g[::max(1, fk.H // n)] = 0; return g

def letterbox(img, t, a, b, px=160):
    """cinema bars that slide in over 0.3 s at a and out over 0.3 s at b (px on a frame whose short side is 1080)."""
    if not (a <= t < b + 0.3): return img
    k = fk.ease_out((t - a) / 0.3) * (1 - fk.ease_out((t - b) / 0.3) if t >= b else 1)
    h = int(upx(px) * k)
    if h: img = img.copy(); img[:h] = 0; img[fk.H - h:] = 0
    return img

def polaroid(base, frozen, k, rot=-3.0, scale=0.56, border=24, dy=0):
    """Freeze-frame card: a freeze frame popped out as a white-bordered photo over the live shot. Stack 1->3 on beats
    by calling it again with the next freeze, a new rotation and a small dy. k = pop-in progress; pass ease_back(u) so k overshoots past 1 and settles."""
    if k <= 0: return base
    w, h = int(fk.W * scale), int(fk.H * scale); b = int(upx(border))
    card = np.full((h + 2 * b, w + 2 * b, 3), 245, np.uint8); card[b:b + h, b:b + w] = cv2.resize(frozen, (w, h), interpolation=cv2.INTER_AREA)
    s = 1.25 - 0.25 * min(k, 1.0) + 0.05 * max(0.0, k - 1.0)
    M = cv2.getRotationMatrix2D((card.shape[1] / 2, card.shape[0] / 2), rot, s)
    M[0, 2] += fk.W / 2 - card.shape[1] / 2; M[1, 2] += fk.H / 2 - card.shape[0] / 2 + dy
    warped = cv2.warpAffine(card, M, (fk.W, fk.H), borderValue=(0, 0, 0))
    mask = cv2.warpAffine(np.full(card.shape[:2], 255, np.uint8), M, (fk.W, fk.H))[..., None] / 255.0
    shadow = cv2.GaussianBlur(mask, (0, 0), upx(30))
    if shadow.ndim == 2: shadow = shadow[..., None]
    out = base.astype(np.float32) * (1 - 0.35 * np.roll(shadow, int(upx(20)), 0))
    return (out * (1 - mask) + warped * mask).astype(np.uint8)

def ease_back(u, s=1.70158):
    """Back easing out: rises past 1 near the end, then settles at 1 when u = 1."""
    u = fk.clamp01(u) - 1.0
    return 1.0 + u * u * ((s + 1.0) * u + s)

# ------------------------------------------------------------------ whole-frame hits that also hit the type
def hits(img, t, events):
    """fk.hits plus the aura kinds. events: [(time, kind, frames)].
    kinds: everything fk.hits takes (negative, negative:amber, duo, red, pink, teal, warm, glitch, smear, white)
           + threshold | duo-blue | duo-red | eyes:<y> | grid | black"""
    f = fk.frame_of(t); rest = []
    for (t0, kind, n) in events:
        k = f - fk.frame_of(t0)
        if not (0 <= k < n): continue
        if kind == "threshold": img = threshold(img)
        elif kind == "duo-blue": img = fk.duotone(img, "#0b1bd6", "#ffffff")
        elif kind == "duo-red": img = fk.duotone(img, "#d0142c", "#fff3f0")
        elif kind.startswith("eyes"): img = eye_strip(img, float(kind.split(":")[1]) if ":" in kind else 0.38)
        elif kind == "grid": img = clone_grid(img)
        elif kind == "black": img = np.zeros_like(img)
        else: rest.append((t0, kind, n))
    return fk.hits(img, t, rest) if rest else img
