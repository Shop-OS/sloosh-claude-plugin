"""filmkit.py: the compositor toolkit for a motion film.

A film is ONE editor script (edit.py) with a pure render(t) -> frame function. The same t always gives the
same frame: random effects are seeded by the frame number, so re-renders match exactly.

edit.py imports this module and the shared timeline (tl.py). It builds a cut list of Shots, adds overlay layers
(transparent PNG sequences rendered from HTML by render_html.py), and calls run(render).

  python3 edit.py                         -> out/<name>_vN.mp4 (never overwrites; next free version)
  python3 edit.py sheet.jpg 1.2,3.4,9.0   -> stills mode: renders only those times into a labelled sheet

Cut-list row:
  (start, end, source, in_point, speed, zoom_from, zoom_to, focus_x, focus_y, tags)
  tags: a space-separated string, e.g. "punch red", "ramp glitch", "hard negative".

Tags (exact recipes):
  punch    hard hit-zoom on the beat: scale x (1 + 0.12 e^(-t/0.05))
  ramp     motion decelerating into the cut: clip time = d x (1 - (1 - u)^2.2) x 1.25
  red pink teal warm   single-colour grade flash: luma mapped onto a colour, mixed 35-90%
  duo      cream-to-deep-red poster frame (duo, or duo:#dark:#light)
  bwflick  histogram-equalised B/W on every other 3-frame group
  smear    one-sided horizontal box blur of 120-420 px in random bands
  glitch   12 random horizontal slices shifted +-160 px, plus a 14 px RGB split
  zblur    a rush toward the centre: the average of 6 progressively zoomed copies
  shake    decaying jitter plus a constant 4 px sin/cos wobble
  negative a single-frame invert hit (255 - x); "negative:amber" for the amber-tinted version
  leak     a blue-to-orange Gaussian flare sweeping left to right over 0.45 s
  whiteout the ending flash: fade the image to 90% white
  flat     the deliberately flat BEFORE look: 35% colour, contrast cut to 78%, slightly lifted
  flash    brightness x1.25 + 30 for 2 frames at the shot start
  freeze   hold the frame after 40% of the shot
  reverse  play the window backwards
  stutter  repeat the first 0.1 s twice, then continue
  hard     no cut grammar into this shot
  locked   no handheld motion on a still (a code packshot sitting on a set plate)
  pushin   the zoom accelerates (u^2.2) instead of easing, for a push-in that cuts at peak speed (match cut)
  vert_full | vert_blurbg   how a vertical source sits in a horizontal frame
                            (cover-crop slightly high | centred over a blurred, darkened copy)
Stills automatically get the handheld micro-rotation (1.2 deg x sin(9t), plus a 2.5 deg kick on the cut) and the
slow zoom, so nothing reads as a photo.

Placeholders: set FILMKIT_PLACEHOLDERS=1 to render a missing source as a dark card with its file name, so the cut can
be checked before any shot exists.
"""
import glob, math, os, re, subprocess, sys
import numpy as np
import cv2

W, H, FPS = 1080, 1920, 30
TINTS = {"red": "#d0142c", "pink": "#ff4fa3", "teal": "#14b8b0", "warm": "#ff9a3c"}

def setup(w, h, fps):
    global W, H, FPS
    W, H, FPS = w, h, fps

# ------------------------------------------------------------------ small helpers
def hex2bgr(h):
    h = h.lstrip("#"); return np.array([int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16)], np.float32)

def clamp01(x): return min(1.0, max(0.0, x))
def ease_out(u, p=4): u = clamp01(u); return 1 - (1 - u) ** p          # quartic ease-out
def ease_in_out(u): u = clamp01(u); return 0.5 - 0.5 * math.cos(math.pi * u)
def lerp(a, b, u): return a + (b - a) * u
def rng(frame, salt=0): return np.random.default_rng((int(frame) * 7919 + salt * 104729) & 0xFFFFFFFF)
def frame_of(t): return int(round(t * FPS))

def cover(img, w, h, fy=0.5):
    ih, iw = img.shape[:2]; s = max(w / iw, h / ih)
    r = cv2.resize(img, (max(w, round(iw * s)), max(h, round(ih * s))), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)
    y = int((r.shape[0] - h) * fy); x = (r.shape[1] - w) // 2
    return r[y:y + h, x:x + w]

def blurbg(img, w, h):
    """vert_blurbg: the clip centred over a blurred, darkened copy of itself (vertical into horizontal, or the reverse)."""
    bg = cover(img, w, h); bg = cv2.GaussianBlur(cv2.resize(bg, (w // 8, h // 8)), (0, 0), 6)
    bg = (cv2.resize(bg, (w, h)) * 0.45).astype(np.uint8)
    ih, iw = img.shape[:2]; s = min(w / iw, h / ih); fg = cv2.resize(img, (round(iw * s), round(ih * s)), interpolation=cv2.INTER_AREA)
    y = (h - fg.shape[0]) // 2; x = (w - fg.shape[1]) // 2; bg[y:y + fg.shape[0], x:x + fg.shape[1]] = fg
    return bg

def placeholder(label):
    """a dark card with a frame and the missing file name: a stand-in shot for previews."""
    img = np.full((H, W, 3), 38, np.uint8); m = max(8, W // 40)
    cv2.rectangle(img, (m, m), (W - m, H - m), (90, 90, 90), max(2, W // 400))
    cv2.line(img, (m, m), (W - m, H - m), (60, 60, 60), 2); cv2.line(img, (W - m, m), (m, H - m), (60, 60, 60), 2)
    sc = W / 1080.0; txt = os.path.basename(label)
    cv2.putText(img, txt, (int(60 * sc), H // 2), cv2.FONT_HERSHEY_SIMPLEX, 1.4 * sc, (220, 220, 220), max(1, int(3 * sc)), cv2.LINE_AA)
    return img

# ------------------------------------------------------------------ sources
class Clip:
    """A source decoded on demand into a small frame cache. frame(t) returns the source frame at time t, fitted to
    the film size; in-between times blend two frames, so speed ramps stay smooth.
    Accepts: a video, an image (gets the handheld treatment), 'black', or '#rrggbb'."""
    _all = {}

    @classmethod
    def get(cls, path, fit="cover"):
        key = (path, fit)
        if key not in cls._all: cls._all[key] = Clip(path, fit)
        return cls._all[key]

    def __init__(self, path, fit="cover"):
        self.path, self.fit, self.cache = path, fit, {}
        if path == "black" or path.startswith("#"):
            self.kind = "color"; self.img = np.zeros((H, W, 3), np.uint8)
            if path.startswith("#"): self.img[:] = hex2bgr(path).astype(np.uint8)
            return
        if not os.path.exists(path):
            if os.environ.get("FILMKIT_PLACEHOLDERS") == "1":
                self.kind = "image"; self.img = placeholder(path); return
            sys.exit(f"filmkit: missing source {path} (set FILMKIT_PLACEHOLDERS=1 to preview with placeholder cards)")
        if os.path.splitext(path)[1].lower() in (".jpg", ".jpeg", ".png", ".webp", ".bmp"):
            im = cv2.imread(path, cv2.IMREAD_COLOR)
            if im is None: sys.exit(f"filmkit: cannot read image {path}")
            self.kind = "image"; self.img = self._fit(im); return
        self.kind = "video"; cap = cv2.VideoCapture(path)
        self.fps = cap.get(cv2.CAP_PROP_FPS) or 30.0; self.n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); cap.release()
        self.duration = self.n / self.fps; self._cap = None; self._pos = -1

    def _fit(self, im):
        if self.fit == "vert_blurbg": return blurbg(im, W, H)
        if self.fit == "vert_full": return cover(im, W, H, fy=0.38)
        return cover(im, W, H)

    def _read(self, i):
        if i in self.cache: return self.cache[i]
        if self._cap is None or i != self._pos + 1:
            if self._cap is not None: self._cap.release()
            self._cap = cv2.VideoCapture(self.path); self._cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ok, fr = self._cap.read(); self._pos = i
        if not ok:
            return self.cache.get(max(self.cache)) if self.cache else np.zeros((H, W, 3), np.uint8)
        fr = self._fit(fr)
        if len(self.cache) > 90: self.cache.pop(next(iter(self.cache)))
        self.cache[i] = fr; return fr

    def frame(self, t):
        if self.kind != "video": return self.img
        x = min(max(t * self.fps, 0), self.n - 1); i = int(math.floor(x)); f = x - i
        a = self._read(i)
        if f < 0.08 or i + 1 >= self.n: return a
        b = self._read(i + 1); return cv2.addWeighted(a, 1 - f, b, f, 0)

# ------------------------------------------------------------------ frame effects
def camera(img, z, fx=0.5, fy=0.5, rot=0.0, dx=0.0, dy=0.0):
    """eased zoom around a focus point; BLACK border when zooming below 1x (never mirrored edges)."""
    M = cv2.getRotationMatrix2D((fx * W, fy * H), rot, z); M[0, 2] += dx; M[1, 2] += dy
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))

def zblur(img, strength, fx=0.5, fy=0.5, n=6):
    if strength <= 0.003: return img
    acc = img.astype(np.float32); cx, cy = fx * W, fy * H
    for k in range(1, n):
        s = 1 + strength * k / (n - 1); M = np.float32([[s, 0, cx - s * cx], [0, s, cy - s * cy]])
        acc += cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    return (acc / n).astype(np.uint8)

def whip(img, px):
    """horizontal box blur up to ~170 px: the whip-pan streak."""
    px = int(px) | 1; return img if px < 3 else cv2.blur(img, (px, 1))

def luma(img): return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0

def tint(img, col, mix=0.6):
    L = luma(img)[..., None]; out = hex2bgr(col) * np.clip(L * 1.2, 0, 1)
    return np.clip(img * (1 - mix) + out * mix, 0, 255).astype(np.uint8)

def duotone(img, dark="#3a0008", light="#f4ead8", mix=0.92):
    L = luma(img)[..., None]; out = hex2bgr(dark) * (1 - L) + hex2bgr(light) * L
    return np.clip(img * (1 - mix) + out * mix, 0, 255).astype(np.uint8)

def rgb_split(img, px):
    px = int(round(px))
    if px < 1: return img
    out = img.copy(); out[:, px:, 2] = img[:, :-px, 2]; out[:, :-px, 0] = img[:, px:, 0]; return out

def smear(img, frame):
    r = rng(frame, 3); out = img.copy()
    for _ in range(int(r.integers(2, 5))):
        y0 = int(r.integers(0, H - 40)); h = int(r.integers(H // 20, H // 5)); k = int(r.integers(120, 421) * W / 1920) | 1
        bl = cv2.blur(out[y0:y0 + h], (k, 1)); s = k // 2; out[y0:y0 + h, s:] = bl[:, :W - s]
    return out

def glitch(img, frame):
    r = rng(frame, 5); out = img.copy(); amp = int(160 * W / 1920)
    for _ in range(12):
        y0 = int(r.integers(0, H)); h = int(r.integers(max(2, H // 90), H // 14))
        out[y0:y0 + h] = np.roll(img[y0:y0 + h], int(r.integers(-amp, amp + 1)), axis=1)
    return rgb_split(out, 14 * W / 1920)

def bwflick(img, local_frame):
    if (local_frame // 3) % 2: return img
    return cv2.cvtColor(cv2.equalizeHist(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)), cv2.COLOR_GRAY2BGR)

def negative(img, amber=False):
    n = 255 - img
    return tint(n, "#ffb347", 0.35) if amber else n

def leak(img, u):
    """a Gaussian blob travelling left to right over the shot's first 0.45 s, blue fading to orange."""
    x = lerp(-0.3, 1.3, u) * W; y = 0.42 * H; s = 4
    yy, xx = np.mgrid[0:H // s, 0:W // s].astype(np.float32)
    g = np.exp(-(((xx * s - x) / (0.30 * W)) ** 2 + ((yy * s - y) / (0.50 * H)) ** 2) / 2)
    g = cv2.resize(g, (W, H))[..., None]; col = lerp(np.array([255, 120, 40], np.float32), np.array([40, 140, 255], np.float32), u)
    return np.clip(img + g * col * 0.6 * math.sin(math.pi * clamp01(u)), 0, 255).astype(np.uint8)

def whiteout(img, k):
    return cv2.addWeighted(img, 1 - 0.9 * k, np.full_like(img, 255), 0.9 * k, 0)

def flash(img): return cv2.convertScaleAbs(img, alpha=1.25, beta=30)

def mosaic_wipe(a, b, u, block=None, seed=1):
    """pixel-mosaic wipe: blocks switch from a to b in centre-out order with randomness (about 0.3 s)."""
    block = block or max(24, W // 24); gh, gw = math.ceil(H / block), math.ceil(W / block)
    yy, xx = np.mgrid[0:gh, 0:gw]; d = np.hypot(yy - gh / 2, xx - gw / 2); d = d / d.max()
    order = 0.75 * d + 0.25 * np.random.default_rng(seed).random(d.shape)
    m = cv2.resize((order < u).astype(np.uint8), (gw * block, gh * block), interpolation=cv2.INTER_NEAREST)[:H, :W, None]
    return np.where(m > 0, b, a)

def shockwave(img, u, cx=0.5, cy=0.5, amp=28):
    """a radial ring distortion travelling outward (u 0..1 over ~0.4 s)."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); dx, dy = xx - cx * W, yy - cy * H; r = np.hypot(dx, dy) + 1e-3
    R = u * math.hypot(W, H) * 0.7; ring = np.exp(-((r - R) / (0.05 * W)) ** 2) * amp * (1 - u)
    return cv2.remap(img, xx - dx / r * ring, yy - dy / r * ring, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

# ------------------------------------------------------------------ finishing stack (applied in this fixed order)
class Finish:
    def __init__(self, contrast=True, vignette=0.6, bloom=0.55, grain=6.0):
        self.contrast, self.bloom, self.grain = contrast, bloom, grain
        x = np.arange(256) / 255.0
        self.lut = (np.clip((x - 0.03) / 0.95, 0, 1) ** 1.1 * 255).astype(np.uint8)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d2 = ((xx - W / 2) / (W / 2)) ** 2 * 0.5 + ((yy - H / 2) / (H / 2)) ** 2 * 0.5
        v = np.clip(1.15 - vignette * d2, 0.35, 1.0) if vignette else None
        self.vig = cv2.merge([(v * 255).astype(np.uint8)] * 3) if v is not None else None   # cached uint8: cv2.multiply is fast

    def __call__(self, img, frame, grain=None, vignette=True):
        if self.contrast: img = cv2.LUT(img, self.lut)                                       # 6 contrast curve
        if self.vig is not None and vignette: img = cv2.multiply(img, self.vig, scale=1 / 255.0)   # 7 vignette
        if self.bloom:                                                                        # 8 bloom (>175, 22 px, 55%)
            sm = cv2.resize(img, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
            m = cv2.GaussianBlur(cv2.subtract(sm, (175, 175, 175, 0)), (0, 0), 22 / 4)
            img = cv2.addWeighted(img, 1.0, cv2.resize(m, (W, H)), self.bloom * 0.3 * 255 / 80, 0)
        g = self.grain if grain is None else grain                                            # 10 grain at 1/3 res
        if g:
            n = np.clip(rng(frame, 11).normal(128, g, (H // 3, W // 3)), 0, 255).astype(np.uint8)
            img = cv2.addWeighted(img, 1.0, cv2.resize(cv2.merge([n] * 3), (W, H)), 1.0, -128)
        return img

# ------------------------------------------------------------------ shots and the cut list
class Shot:
    def __init__(self, start, end, source, inp=0.0, speed=1.0, z0=1.0, z1=1.0, fx=0.5, fy=0.5, tags=""):
        self.start, self.end, self.source, self.inp, self.speed = start, end, source, inp, speed
        self.z0, self.z1, self.fx, self.fy = z0, z1, fx, fy
        self.tags = tags.split() if isinstance(tags, str) else list(tags)
        fit = "vert_blurbg" if "vert_blurbg" in self.tags else "vert_full" if "vert_full" in self.tags else "cover"
        self.clip = Clip.get(source, fit)

    @property
    def dur(self): return self.end - self.start
    def has(self, tag): return any(t == tag or t.startswith(tag + ":") for t in self.tags)
    def arg(self, tag):
        for t in self.tags:
            if t.startswith(tag + ":"): return t.split(":")[1:]
        return []

    def src_time(self, lt):
        d, u = self.dur, clamp01(lt / max(self.dur, 1e-6))
        if self.has("stutter"): p = 0.1; lt = (lt % (2 * p)) if lt < 6 * p else lt - 4 * p
        if self.has("freeze"): lt = min(lt, 0.4 * d)
        if self.has("ramp"): x = d * (1 - (1 - u) ** 2.2) * 1.25
        else: x = lt
        if self.has("reverse"): x = (d * (1.25 if self.has("ramp") else 1.0)) - x
        return self.inp + x * self.speed

class CutList:
    """Renders the footage layer from cut-list rows, with the cut grammar on every cut:
      outgoing shot's last 2 frames: zoom x1.06 + radial zoom blur 0.10
      incoming shot's first 3 frames: zoom 1.12 -> 1.0, zoom blur 0.18 -> 0, a 14 px shake decaying e^(-t/0.07)
      a 2-frame brightness flash on the cut
    Optional beat FX (hyper sections): a punch on every beat, scale 1 + 0.07 e^(-t/0.12),
    and a 14 px colour split on every downbeat (every 4 beats), decaying over 0.15 s."""
    def __init__(self, rows, grammar=True, beats=None, beat_punch=0.07, downbeat_split=14, fx_from=0.0, fx_to=1e9, fx_windows=None):
        self.shots = sorted([r if isinstance(r, Shot) else Shot(*r) for r in rows], key=lambda s: s.start)
        self.grammar, self.beats = grammar, beats or []
        self.beat_punch, self.downbeat_split = beat_punch, downbeat_split
        self.windows = fx_windows or [(fx_from, fx_to)]          # beat FX run only inside these (start, end) windows

    def _win(self, t):
        for a, b in self.windows:
            if a <= t < b: return a
        return None

    def index(self, t):
        for i, s in enumerate(self.shots):
            if s.start - 1e-6 <= t < s.end - 1e-6: return i
        return None

    def render(self, t):
        i = self.index(t)
        if i is None: return np.zeros((H, W, 3), np.uint8)
        s = self.shots[i]; f = frame_of(t); lt = t - s.start; lf = int(round(lt * FPS))
        last = int(round((s.end - t) * FPS)) - 1; u = clamp01(lt / max(s.dur, 1e-6))
        img = s.clip.frame(s.src_time(lt))
        # 2 camera: eased zoom around the focus, plus punch / shake / handheld
        zu = u ** 2.2 if s.has("pushin") else ease_in_out(u)          # pushin: accelerating push into a match cut
        z = lerp(s.z0, s.z1, zu); rot = dx = dy = 0.0; zb = 0.0
        if s.clip.kind == "image" and not s.has("locked"):           # locked: no handheld (code packshots over a set plate)
            rot = 1.2 * math.sin(9 * t) * 0.5 + 2.5 * math.exp(-lt / 0.12) * (1 if i % 2 else -1)
        if s.has("punch"): z *= 1 + 0.12 * math.exp(-lt / 0.05)
        if s.has("shake"):
            r = rng(f, 9); a = 22 * W / 1080 * math.exp(-lt / 0.12)
            dx += float(r.uniform(-a, a)) + 4 * math.sin(31 * t); dy += float(r.uniform(-a, a)) + 4 * math.cos(27 * t)
        w0 = self._win(t)
        if self.beats and self.beat_punch and w0 is not None:
            past = [b for b in self.beats if w0 - 1e-6 <= b <= t + 1e-6]
            if past: z *= 1 + self.beat_punch * math.exp(-(t - past[-1]) / 0.12)
        g = self.grammar and not s.has("hard")
        if g and i > 0 and lf < 3:
            z *= lerp(1.12, 1.0, lf / 3); zb = max(zb, 0.18 * (1 - lf / 3))
            r = rng(f, 7); a = 14 * W / 1080 * math.exp(-lt / 0.07); dx += float(r.uniform(-a, a)); dy += float(r.uniform(-a, a))
        nxt = self.shots[i + 1] if i + 1 < len(self.shots) else None
        if g and nxt is not None and not nxt.has("hard") and last < 2: z *= 1.06; zb = max(zb, 0.10)
        if s.has("zblur"): zb = max(zb, 0.22 * (1 - u))
        img = camera(img, z, s.fx, s.fy, rot, dx, dy)
        if zb: img = zblur(img, zb, s.fx, s.fy)
        # 3 look tags
        for c, hexc in TINTS.items():
            if s.has(c): img = tint(img, hexc, float(s.arg(c)[0]) if s.arg(c) else 0.6)
        if s.has("duo"):
            a = s.arg("duo"); img = duotone(img, *(("#" + a[0].lstrip("#"), "#" + a[1].lstrip("#")) if len(a) >= 2 else ()))
        if s.has("flat"):
            g3 = cv2.cvtColor(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
            img = cv2.addWeighted(img, 0.35, g3, 0.65, 0); img = cv2.convertScaleAbs(img, alpha=0.78, beta=22)
        if s.has("bwflick"): img = bwflick(img, lf)
        if s.has("smear"): img = smear(img, f)
        if s.has("glitch"): img = glitch(img, f)
        if s.has("negative") and lf < 2: img = negative(img, amber="amber" in s.arg("negative"))
        if self.beats and self.downbeat_split and w0 is not None:
            downs = [b for b in self.beats[::4] if w0 - 1e-6 <= b <= t + 1e-6]
            if downs and t - downs[-1] < 0.3: img = rgb_split(img, self.downbeat_split * W / 1080 * math.exp(-(t - downs[-1]) / 0.15))
        # 5 light leak on big hits
        if s.has("leak") and lt < 0.45: img = leak(img, lt / 0.45)
        if s.has("whiteout") and s.end - t < 0.4: img = whiteout(img, 1 - (s.end - t) / 0.4)
        return img

    def flash_now(self, t):
        """step 9: flash frames on cuts (call after Finish)."""
        i = self.index(t)
        if i is None: return False
        s = self.shots[i]; lf = int(round((t - s.start) * FPS))
        return lf < 2 and ((self.grammar and i > 0 and not s.has("hard")) or s.has("flash"))

# ------------------------------------------------------------------ overlays (HTML -> PNG sequences via render_html.py)
class Overlay:
    """A transparent PNG sequence rendered by render_html.py, placed on the film timeline.
    start: film time of the sequence's frame 0. speed: page seconds per film second (UI_SP = natural length / section
    length, so the page plays at (t - start) x UI_SP; the inverse of ui2t)."""
    def __init__(self, folder, start=0.0, speed=1.0, fps=None):
        self.files = sorted(glob.glob(os.path.join(folder, "*.png")))
        if not self.files: sys.exit(f"filmkit: no PNG frames in {folder} (run render_html.py first)")
        self.start, self.speed, self.fps = start, speed, fps or FPS; self.cache = {}
        # empty (fully transparent) frames compress to the smallest PNGs: skip decoding them
        sizes = [os.path.getsize(f) for f in self.files]; small = min(sizes)
        probe = cv2.imread(self.files[sizes.index(small)], cv2.IMREAD_UNCHANGED)
        empty_ok = probe is not None and probe.ndim == 3 and probe.shape[2] == 4 and probe[..., 3].max() == 0
        self.empty = {k for k, sz in enumerate(sizes) if empty_ok and sz <= small * 1.02 + 64}

    def rgba(self, t):
        k = int(round((t - self.start) * self.speed * self.fps))
        if k < 0 or k >= len(self.files) or k in self.empty: return None
        if k not in self.cache:
            im = cv2.imread(self.files[k], cv2.IMREAD_UNCHANGED)
            if im is None: return None
            if im.dtype != np.uint8: im = (im / 257).astype(np.uint8)                 # 16-bit PNG
            if im.ndim == 2: im = cv2.cvtColor(im, cv2.COLOR_GRAY2BGRA)                # grayscale PNG
            elif im.shape[2] == 3: im = np.dstack([im, np.full(im.shape[:2], 255, np.uint8)])
            elif im.shape[2] == 2: im = cv2.merge([im[..., 0]] * 3 + [im[..., 1]])     # grayscale + alpha
            if len(self.cache) > 8: self.cache.pop(next(iter(self.cache)))
            self.cache[k] = im
        return self.cache[k]

    def over(self, img, t, opacity=1.0, zoom=1.0, fx=0.5, fy=0.5):
        """composite onto img. zoom>1 crops into a 2x-rendered sequence (render_html.py --scale 2) so text stays sharp."""
        o = self.rgba(t)
        if o is None: return img
        if zoom > 1.0:
            oh, ow = o.shape[:2]; cw, ch = int(ow / zoom), int(oh / zoom)
            x0 = int(min(max(fx * ow - cw / 2, 0), ow - cw)); y0 = int(min(max(fy * oh - ch / 2, 0), oh - ch))
            o = o[y0:y0 + ch, x0:x0 + cw]
        if o.shape[1] != W or o.shape[0] != H: o = cv2.resize(o, (W, H), interpolation=cv2.INTER_AREA)
        a = (o[..., 3:4].astype(np.float32) / 255.0) * opacity
        return (img * (1 - a) + o[..., :3] * a).astype(np.uint8)


# ------------------------------------------------------------------ whole-frame hits AFTER the type is composited
def hits(img, t, events):
    """Whole-frame hits that also hit the type (red duotone, negatives and smears hit the text too).
    events: [(time, kind, frames)], kind in negative | negative:amber | duo | red | pink | teal | warm | glitch | smear | white"""
    f = frame_of(t)
    for (t0, kind, n) in events:
        k = f - frame_of(t0)
        if 0 <= k < n:
            if kind.startswith("negative"): img = negative(img, amber=kind.endswith("amber"))
            elif kind == "duo": img = duotone(img)
            elif kind in TINTS: img = tint(img, TINTS[kind], 0.85)
            elif kind == "glitch": img = glitch(img, f)
            elif kind == "smear": img = smear(img, f)
            elif kind == "white": img = whiteout(img, 1 - k / n)
    return img

# ------------------------------------------------------------------ runner: stills mode + video mode
def next_version(name, folder="out"):
    os.makedirs(folder, exist_ok=True); v = 1
    while os.path.exists(os.path.join(folder, f"{name}_v{v}.mp4")): v += 1
    return os.path.join(folder, f"{name}_v{v}.mp4")

def stills(render, times, out):
    if not times: sys.exit("filmkit: no still times given")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True); tiles = []
    for t in times:
        im = render(t); sc = 360 / W; im = cv2.resize(im, (360, int(H * sc)), interpolation=cv2.INTER_AREA)
        cv2.putText(im, f"{t:.2f}s", (8, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2); tiles.append(im)
    cols = min(8, len(tiles)); rows = math.ceil(len(tiles) / cols); th, tw = tiles[0].shape[:2]
    sheet = np.zeros((rows * th, cols * tw, 3), np.uint8)
    for k, im in enumerate(tiles): sheet[(k // cols) * th:(k // cols + 1) * th, (k % cols) * tw:(k % cols + 1) * tw] = im
    cv2.imwrite(out, sheet, [cv2.IMWRITE_JPEG_QUALITY, 88]); print("stills ->", out)

def video(render, duration, out, crf=18):
    N = int(round(duration * FPS))
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-pix_fmt", "yuv420p",
                          "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-movflags", "+faststart", out],
                         stdin=subprocess.PIPE)
    try:
        for f in range(N):
            p.stdin.write(np.ascontiguousarray(render(f / FPS)).tobytes())
            if f % (FPS * 2) == 0: print(f"  render {f / FPS:5.1f} / {duration:.1f} s", flush=True)
        p.stdin.close()
    except BrokenPipeError:              # ffmpeg stopped early; its exit code below says why
        pass
    if p.wait() != 0: sys.exit(f"ffmpeg failed (exit {p.returncode}); {out} is not complete")
    print("video ->", out); return out

def run(render, duration, name="film"):
    """CLI: `python3 edit.py` renders the next version; `python3 edit.py sheet.jpg 1.2,3.4` renders stills only."""
    a = sys.argv[1:]
    if a and a[0].endswith((".jpg", ".png")):
        times = [float(x) for x in a[1].split(",")] if len(a) > 1 else [duration * k / 16 for k in range(16)]
        stills(render, times, a[0])
    else:
        video(render, duration, a[0] if a else next_version(name))
