"""glitchkit.py: the glitch-fx style toolkit for edit.py (Sloosh motion pack).

Glitch is done in CODE on clean AI footage, per frame, after the camera and before the finish. Every effect is a pure
function of (frame, film frame number), seeded with fk.rng, so the same t always gives the same frame.
Copy this file into the film's lib/ (next to filmkit.py) and `import glitchkit as gk`.

Layers in render(t), in this order:
  img = cuts.render(t)                   footage + camera + cut grammar (filmkit)
  img = gk.apply_tags(img, cuts, t)      sustained shot treatments from cut-list tags  gl:sort gl:wave gl:vhs gl:xray ...
  img = TR.apply(img, t)                 glitch transitions on cuts  (gk.Transitions: linewipe slicecut blockcut mosaic)
  img = gk.over(img, HUD, t)             the mono HUD layer (ui/hud.html)
  img = gk.over(img, TYPE, t, tears=..)  the type; its entrances tear on their own (type-only slices + RGB)
  img = GH.apply(img, t)                 whole-frame hits AFTER the type, so the type tears with the frame (gk.Hits)
  img = gk.scan(img); img = finish(img, f)

Hit kinds (tl.GLITCH rows: (time, kind, frames[, {params}]); kinds may be joined with '+', e.g. "slices+rgb"):
  slices  rgb  blocks  sort  wave  static  tear  noise (coloured block confetti, no sampling)  invert (every frame)
  strobe  (invert on 2-frame groups: frames 0-1, 4-5, 8-9 -> 3 flashes)   psych (pre-drop psych strobe)
  white   (flash)   thermal   xray   mirror   error (red ERROR card, Cyber Hard only, once)
Cut-list tags (sustained, whole shot): gl:sort[:cols]  gl:wave[:amp]  gl:vhs  gl:xray (x-ray scan reveal at the shot
  start, then a radiograph flicker)  gl:thermal  gl:static[:mix]  gl:scan  gl:ca[:px]  gl:mono[:#hex] (B/W + one hue)  gl:mirror
Budget: gk.budget(tl.GLITCH, tl.LEN, tl.B, preset) prints the hit report and the violations (run it before rendering).
"""
import math
import numpy as np
import cv2
import filmkit as fk

FLASH_KINDS = ("invert", "strobe", "psych", "white", "static", "error")

# ------------------------------------------------------------------ small helpers
def _wh(img): return img.shape[1], img.shape[0]
def _k(lf, n): return 1.0 - 0.5 * lf / max(1, n - 1)          # intensity decays 100% -> 50% across a hit
_cache = {}

def _rows_mask(H, gap, op):
    key = ("scan", H, gap, op)
    if key not in _cache:
        m = np.ones((H, 1, 1), np.float32); m[::gap] = 1 - op; _cache[key] = m
    return _cache[key]

# ------------------------------------------------------------------ primitives (img uint8 BGR; k = intensity 0..1)
def rgb(img, k=1.0, px=None, dy=0):
    """R and B channels pulled apart horizontally (G fixed). px defaults to 1.4% of width."""
    W, H = _wh(img); px = int(round((px if px is not None else W * 0.014) * k))
    if px < 1: return img
    out = img.copy(); out[:, px:, 2] = img[:, :-px, 2]; out[:, :-px, 0] = img[:, px:, 0]
    if dy: out[..., 0] = np.roll(out[..., 0], dy, axis=0)
    return out

def slices(img, f, k=1.0, n=12, amp=0.09, seed=5, tear=True):
    """horizontal bands jump sideways: n bands, ~42% move, offset up to amp x width; some bands tear a channel."""
    W, H = _wh(img); r = fk.rng(f, seed); out = img.copy(); A = amp * W * k
    edges = [0, *sorted(int(x) for x in r.integers(0, H, n - 1)), H]
    for a, b in zip(edges[:-1], edges[1:]):
        if b - a < 2 or r.random() > 0.42: continue
        sh = int(r.uniform(-1, 1) * A); band = np.roll(img[a:b], sh, axis=1)
        if tear and r.random() < 0.5: band[..., 0] = np.roll(band[..., 0], int(sh * 0.15) + 3, axis=1)
        out[a:b] = band
    return out

def blocks(img, f, k=1.0, bs=None, cover=0.18, tint=None, seed=6):
    """macroblock corruption: blocks copied from offset positions, some channel-swapped, posterised or tinted."""
    W, H = _wh(img); bs = bs or max(24, W // 22); r = fk.rng(f, seed); out = img.copy()
    nb = int((H // bs) * (W // bs) * cover * k); tc = fk.hex2bgr(tint) if tint else None
    for _ in range(nb):
        by, bx = int(r.integers(0, H // bs)) * bs, int(r.integers(0, W // bs)) * bs
        w = min(bs * int(r.integers(1, 5)), W - bx)
        sy = int(np.clip(by + int(r.integers(-3, 4)) * bs, 0, H - bs)); sx = int(np.clip(bx + int(r.integers(-6, 7)) * bs, 0, W - w))
        src = img[sy:sy + bs, sx:sx + w]; q = r.random()
        if q < 0.25: src = src[..., ::-1]
        elif q < 0.38 and tc is not None: src = (src * 0.35 + tc * 0.65).astype(np.uint8)
        elif q < 0.5: src = (src // 64) * 64
        out[by:by + bs, bx:bx + w] = src
    return out

def sort(img, f, k=1.0, thr=150, cols=0.35, length=260, seed=7, every=3):
    """pixel-sort drips: bright pixels streak DOWN in a share of columns. Vectorised (running max with decay, computed
    in log space at half resolution): ~40-125 ms at 1080x1920, machine-dependent. Columns re-pick every `every` frames."""
    W, H = _wh(img); s = 2; sm = cv2.resize(img, (W // s, H // s), interpolation=cv2.INTER_AREA).astype(np.float32)
    h, w = sm.shape[:2]; lum = sm @ np.float32([0.0722, 0.7152, 0.2126])
    colm = fk.rng(f // every, seed).random(w) < cols * k; bright = (lum > thr) & colm[None, :]
    d = 1 - 1 / max(6.0, length * k / s); ld = math.log(d); iy = (np.arange(h, dtype=np.float32) * ld)[:, None]
    def drip(v):
        L = np.where(bright, np.log(v + 1.0), -1e9).astype(np.float32) - iy
        return np.exp(np.maximum.accumulate(L, axis=0) + iy) - 1.0
    al = drip(lum); take = colm[None, :] & (al > lum + 8)
    acc = np.dstack([drip(sm[..., c]) for c in range(3)])
    res = np.where(take[..., None], acc, sm)
    up = cv2.resize(np.clip(res, 0, 255).astype(np.uint8), (W, H), interpolation=cv2.INTER_LINEAR)
    m = cv2.resize(take.astype(np.uint8) * 255, (W, H), interpolation=cv2.INTER_NEAREST)[..., None]
    return np.where(m > 0, up, img)

def wave(img, t, k=1.0, amp=0.035, wl=None, hz=1.0):
    """sine row displacement (liquid / drugged): rows shift by amp x width, wavelength ~1/6 frame, phase drifting."""
    W, H = _wh(img); wl = wl or H / 6; key = ("grid", W, H)
    if key not in _cache: _cache[key] = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
    xx, yy = _cache[key]; sh = (amp * W * k * np.sin(2 * np.pi * yy[:, :1] / wl + 2 * np.pi * hz * t)).astype(np.float32)
    return cv2.remap(img, xx - sh, yy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)

def static(img, f, k=1.0, mix=0.75):
    """analog snow + a bright rolling band (signal lost)."""
    W, H = _wh(img); r = fk.rng(f, 8)
    n = cv2.resize(r.integers(0, 256, (H // 2, W // 2), dtype=np.uint8), (W, H), interpolation=cv2.INTER_NEAREST)
    a = mix * k; out = cv2.addWeighted(img, 1 - a, cv2.cvtColor(n, cv2.COLOR_GRAY2BGR), a, 0)
    y0 = int(r.integers(0, H)); out[y0:y0 + H // 12] = cv2.add(out[y0:y0 + H // 12], (60, 60, 60, 0))
    return out

def tear(img, f, k=1.0, tint="#ffd6e6"):
    """white / pink dash streaks plus thin slice shifts (datamosh-tear look)."""
    W, H = _wh(img); r = fk.rng(f, 10); out = img.copy(); tc = tuple(int(x) for x in fk.hex2bgr(tint))
    for _ in range(int(40 * k) + 4):
        y, x = int(r.integers(0, H)), int(r.integers(0, W)); ln = int(r.integers(W // 30, W // 6)); th = int(r.integers(2, 6))
        out[y:y + th, x:x + ln] = tc if r.random() < 0.5 else (255, 255, 255)
    for _ in range(int(6 * k) + 1):
        y = int(r.integers(0, H - 40)); h = int(r.integers(6, 40)); out[y:y + h] = np.roll(out[y:y + h], int(r.integers(-W // 8, W // 8)), axis=1)
    return out

def noise(img, f, k=1.0, colors=("#39E6FF", "#FF2D7A", "#FFFFFF"), rows=8, bs=None, seed=9):
    """block-noise confetti: rows of neon blocks and white dashes OVER the frame (no sampling). Palette accents only."""
    W, H = _wh(img); bs = bs or max(16, W // 45); r = fk.rng(f, seed); out = img.copy(); cols = [fk.hex2bgr(c) for c in colors]
    for _ in range(max(1, round(rows * k))):
        y = int(r.integers(0, H // bs)) * bs; x = int(r.random() * W * 0.4); end = x + W * (0.3 + r.random() * 0.7)
        while x < end:
            w = bs * (1 + int(r.integers(0, 3))); c = cols[int(r.integers(0, len(cols)))]
            if r.random() < 0.6:
                hh = bs // 2 if r.random() < 0.3 else bs; a = 0.55 + 0.45 * r.random()
                out[y:y + hh, x:x + w] = (out[y:y + hh, x:x + w] * (1 - a) + c * a).astype(np.uint8)
            x += w + bs * int(r.integers(0, 3))
    for _ in range(int(18 * k)):
        y, x = int(r.integers(0, H)), int(r.integers(0, W)); out[y:y + 2 + int(r.integers(0, 3)), x:x + 40 + int(r.random() * 220)] = 255
    return out

def invert(img): return 255 - img

def mirror(img):
    """mirror totem: the left half reflected onto the right (Cyber Hard, 1-2 beats)."""
    out = img.copy(); W = img.shape[1]; out[:, W - W // 2:] = img[:, :W // 2][:, ::-1]; return out

def error_card(img, f, red="#D0182A", word="ERROR"):
    """full-frame red card, outlined warning triangle, spaced mono caps (Cyber Hard only, once, 4-8 frames)."""
    from PIL import Image, ImageDraw, ImageFont
    import os
    W, H = _wh(img); key = ("err", W, H, red, word)
    if key not in _cache:
        im = Image.new("RGB", (W, H), tuple(int(red.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))); d = ImageDraw.Draw(im); u = min(W, H) / 1080
        cx, cy, s = W / 2, H * 0.42, 180 * u
        d.line([(cx, cy - s), (cx + s * 1.1, cy + s * 0.8), (cx - s * 1.1, cy + s * 0.8), (cx, cy - s)], fill=(255, 190, 190), width=int(14 * u), joint="curve")
        d.line([(cx, cy - s * 0.35), (cx, cy + s * 0.3)], fill=(255, 190, 190), width=int(16 * u)); d.ellipse([cx - 11 * u, cy + s * 0.5 - 11 * u, cx + 11 * u, cy + s * 0.5 + 11 * u], fill=(255, 190, 190))
        fp = "fonts/jetbrains-mono-latin-500-normal.woff2"
        ft = None
        if os.path.exists(fp):
            try: ft = ImageFont.truetype(fp, int(64 * u))      # needs Pillow built with FreeType + WOFF2 support
            except (OSError, ValueError): ft = None
        if ft is None:
            try: ft = ImageFont.load_default(size=int(64 * u))   # Pillow >= 10.1
            except TypeError: ft = ImageFont.load_default()
        txt = " ".join(word)
        try: d.text((cx, cy + s * 1.5), txt, fill=(255, 255, 255), font=ft, anchor="mm")
        except ValueError:                                        # old bitmap fonts do not support anchors
            tw = d.textlength(txt, font=ft) if hasattr(d, "textlength") else 8 * len(txt)
            d.text((cx - tw / 2, cy + s * 1.5), txt, fill=(255, 255, 255), font=ft)
        _cache[key] = cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2BGR)
    return slices(_cache[key], f, 0.5, amp=0.04) if f % 3 == 0 else _cache[key].copy()

def scan(img, gap=4, op=0.22):
    """CRT scanlines: a dark 1 px row every `gap` px (never under 3 px at 1080 wide: phones moire)."""
    out = img.copy(); out[::gap] = cv2.convertScaleAbs(img[::gap], alpha=1 - op); return out

def zblur(img, strength, fx=0.5, fy=0.5):
    """radial zoom blur computed at half resolution (4x cheaper than filmkit.zblur; fine for hits)."""
    W, H = _wh(img); sm = cv2.resize(img, (W // 2, H // 2), interpolation=cv2.INTER_AREA)
    fk_W, fk_H = fk.W, fk.H; fk.W, fk.H = W // 2, H // 2
    try: sm = fk.zblur(sm, strength, fx, fy, n=5)
    finally: fk.W, fk.H = fk_W, fk_H
    return cv2.resize(sm, (W, H), interpolation=cv2.INTER_LINEAR)

def xray(img):
    """radiograph look: mono, inverted, contrast-stretched, mapped black -> deep blue -> ice -> white."""
    g = 255 - cv2.cvtColor(img, cv2.COLOR_BGR2GRAY); g = cv2.equalizeHist(g).astype(np.float32) / 255.0
    key = "xlut"
    if key not in _cache:
        x = np.linspace(0, 1, 256)[:, None]; stops = np.array([[8, 4, 2], [70, 30, 10], [255, 200, 127], [255, 250, 240]], np.float32)
        pos = np.array([0, 0.35, 0.75, 1.0]); _cache[key] = np.stack([np.interp(x[:, 0], pos, stops[:, c]) for c in range(3)], 1).astype(np.uint8)
    return _cache[key][(g * 255).astype(np.uint8)]

def thermal(img, drift=0.0):
    """false-colour heat map (turbo) with a slow hue drift in degrees."""
    th = cv2.applyColorMap(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.COLORMAP_TURBO)
    if drift:
        hsv = cv2.cvtColor(th, cv2.COLOR_BGR2HSV); hsv[..., 0] = ((hsv[..., 0].astype(np.int16) + int(drift / 2)) % 180).astype(np.uint8)
        th = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return th

def mono(img, keep="#FF2D7A", sim=28):
    """black-and-white world, ONE hue kept (the product's colour)."""
    W, H = _wh(img); sm = cv2.resize(img, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    hsv = cv2.cvtColor(sm, cv2.COLOR_BGR2HSV); hk = cv2.cvtColor(np.uint8([[fk.hex2bgr(keep)]]), cv2.COLOR_BGR2HSV)[0, 0, 0]
    d = np.abs(hsv[..., 0].astype(np.int16) - int(hk)); d = np.minimum(d, 180 - d)
    m = ((d < sim // 2) & (hsv[..., 1] > 60)).astype(np.uint8) * 255; m = cv2.resize(cv2.GaussianBlur(m, (0, 0), 1.5), (W, H))
    g = cv2.cvtColor(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
    return cv2.add(cv2.multiply(img, cv2.merge([m] * 3), scale=1 / 255), cv2.multiply(g, cv2.merge([255 - m] * 3), scale=1 / 255))

def vhs(img, f, k=1.0):
    """VHS: half-res soft chroma shifted sideways, slight luma smear, saturation, a tracking band, noise, scanlines."""
    W, H = _wh(img); r = fk.rng(f, 12)
    y, cr, cb = cv2.split(cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb))
    s = max(6, W // 120)
    cr = cv2.blur(cv2.resize(cv2.resize(cr, (W // 4, H)), (W, H)), (5, 1)); cb = cv2.blur(cv2.resize(cv2.resize(cb, (W // 4, H)), (W, H)), (5, 1))
    cr = np.roll(cr, s, axis=1); cb = np.roll(cb, -s, axis=1); y = cv2.blur(y, (3, 1))
    cr = np.clip(128 + (cr.astype(np.int16) - 128) * 1.15, 0, 255).astype(np.uint8); cb = np.clip(128 + (cb.astype(np.int16) - 128) * 1.15, 0, 255).astype(np.uint8)
    out = cv2.cvtColor(cv2.merge([y, cr, cb]), cv2.COLOR_YCrCb2BGR)
    by = int((f * 7) % (H + 200)) - 100; bh = H // 30                                   # tracking band rolling down
    if 0 < by < H - bh: out[by:by + bh] = np.roll(out[by:by + bh], int(r.integers(8, 30) * k), axis=1); out[by:by + 3] = 235
    n = cv2.resize(r.integers(0, int(18 * k) + 1, (H // 2, W // 2), dtype=np.uint8), (W, H), interpolation=cv2.INTER_NEAREST)
    out = cv2.subtract(cv2.add(out, cv2.merge([n] * 3)), int(9 * k))
    return scan(out, 3, 0.18)

def psych(img, f, lf, n):
    """psych strobe (before the drop): inverted on alternate 2-frame groups (3 flashes in 12 frames), zoom
    blur and colour split growing, the frame darkening toward the breath."""
    u = lf / max(1, n - 1)
    if (lf // 2) % 2 == 0: img = 255 - img
    img = zblur(img, 0.06 + 0.22 * u)
    img = rgb(img, 1.0, px=img.shape[1] * (0.01 + 0.025 * u))
    return cv2.convertScaleAbs(img, alpha=1 - 0.55 * u)

def xray_scan(img, lt, f, dur=0.36, warm="#FFB347"):
    """x-ray scan reveal: a scan line descends with an ease-out over `dur` s. Above it the frame is the x-ray
    version; the line glows (14 px core, 90 px warm halo) with an RGB split around it. Afterwards a radiograph flicker."""
    W, H = _wh(img); u = fk.ease_out(lt / dur); X = xray(img)
    if u >= 1:                                                                     # radiograph flicker on the lightbox
        r = fk.rng(f, 21); g = 0.82 + 0.3 * r.random()
        if r.random() < 0.12: g = 1.35
        return cv2.convertScaleAbs(X, alpha=g)
    y = int(u * H); out = img.copy(); out[:y] = X[:y]
    a, b = max(0, y - 140), min(H, y + 140)
    band = rgb(out[a:b], 1.0, px=W * 0.018).astype(np.float32)
    d = (np.arange(a, b, dtype=np.float32) - y)[:, None, None]
    core = np.exp(-(d / 7.0) ** 2) * 255; halo = np.exp(-(d / 45.0) ** 2) * fk.hex2bgr(warm) * 0.85
    out[a:b] = np.clip(band + core + halo, 0, 255).astype(np.uint8)
    return out

# ------------------------------------------------------------------ transitions (a = outgoing, b = incoming, u 0..1)
def line_wipe(a, b, u, glow=12):
    """a 3 px white line sweeps left -> right; to its left the new shot. The cleanest glitch transition (5 frames)."""
    W, H = _wh(a); x = int(round(u * W)); out = a.copy(); out[:, :x] = b[:, :x]
    lo, hi = max(0, x - 4 * glow), min(W, x + 4 * glow)
    if hi > lo:
        d = np.arange(lo, hi, dtype=np.float32) - x; g = (np.exp(-(d / glow) ** 2) * 200 + np.exp(-(d / 1.6) ** 2) * 255)[None, :, None]
        out[:, lo:hi] = np.clip(out[:, lo:hi] + g, 0, 255).astype(np.uint8)
    return out

def slice_cut(a, b, u, f, n=14, amp=0.12, seed=31):
    """bands switch from a to b in random order; bands mid-switch are shifted and torn."""
    W, H = _wh(a); r = np.random.default_rng(seed); edges = np.linspace(0, H, n + 1).astype(int); out = a.copy()
    th = r.random(n); jit = fk.rng(f, seed)
    for i in range(n):
        y0, y1 = edges[i], edges[i + 1]; src = b if u > th[i] else a
        dist = abs(u - th[i])
        out[y0:y1] = np.roll(src[y0:y1], int(jit.uniform(-1, 1) * amp * W * max(0, 1 - dist * 4)), axis=1) if dist < 0.25 else src[y0:y1]
    return rgb(out, max(0.0, 1 - abs(u - 0.5) * 2))

def block_cut(a, b, u, block=None, seed=3):
    """macroblock switch a -> b in random order (fk.mosaic_wipe is the centre-out version)."""
    W, H = _wh(a); block = block or max(32, W // 18); gh, gw = math.ceil(H / block), math.ceil(W / block)
    order = np.random.default_rng(seed).random((gh, gw))
    m = cv2.resize((order < u).astype(np.uint8), (gw * block, gh * block), interpolation=cv2.INTER_NEAREST)[:H, :W, None]
    return np.where(m > 0, b, a)

class Transitions:
    """Glitch transitions on cuts: rows (cut_time, kind, frames). kind: linewipe | slicecut | blockcut | mosaic.
    `cuts` is the CutList, or any callable src(t) that renders the footage layer (e.g. cuts + gl: tags).
    The incoming row in SHOTS should carry `hard` (no zoom-blur grammar fighting the wipe). The outgoing shot is held
    on its last frame for the wipe (cached), the incoming shot plays."""
    def __init__(self, cuts, rows):
        self.src = cuts.render if hasattr(cuts, "render") else cuts; self.rows, self.hold = sorted(rows), {}
    def apply(self, img, t):
        f = fk.frame_of(t)
        for (tc, kind, n) in self.rows:
            k = f - fk.frame_of(tc)
            if 0 <= k < n:
                if tc not in self.hold: self.hold[tc] = self.src(tc - 1.0 / fk.FPS)
                a, u = self.hold[tc], (k + 1) / (n + 1)
                if kind == "linewipe": return line_wipe(a, img, u)
                if kind == "slicecut": return slice_cut(a, img, u, f)
                if kind == "blockcut": return block_cut(a, img, u)
                if kind == "mosaic": return fk.mosaic_wipe(a, img, u)
        return img

# ------------------------------------------------------------------ sustained shot tags (gl:*)
def _gl(shot):
    out = {}
    for tg in shot.tags:
        if tg.startswith("gl:"):
            p = tg.split(":"); out[p[1]] = p[2:]
    return out

def apply_tags(img, cuts, t):
    """sustained treatments named in the cut list (one per shot; swap treatments on a cut or a line wipe)."""
    i = cuts.index(t)
    if i is None: return img
    s = cuts.shots[i]; g = _gl(s)
    if not g: return img
    lt, f = t - s.start, fk.frame_of(t)
    if "xray" in g: img = xray_scan(img, lt, f)
    if "sort" in g: img = sort(img, f, cols=float(g["sort"][0]) if g["sort"] else 0.35)
    if "wave" in g: img = wave(img, t, amp=float(g["wave"][0]) if g["wave"] else 0.035)
    if "vhs" in g: img = vhs(img, f)
    if "thermal" in g: img = thermal(img, drift=40 * lt)
    if "static" in g: img = static(img, f, mix=float(g["static"][0]) if g["static"] else 0.35)
    if "mono" in g: img = mono(img, "#" + g["mono"][0].lstrip("#") if g["mono"] else "#FF2D7A")
    if "ca" in g: img = rgb(img, 1.0, px=float(g["ca"][0]) if g["ca"] else 3)
    if "scan" in g: img = scan(img)
    if "mirror" in g: img = mirror(img)
    return img

# ------------------------------------------------------------------ hits (whole frame, AFTER the type)
class Hits:
    """Whole-frame glitch hits that also hit the type. rows: (time, kind, frames[, {params}]).
    Intensity decays 100% -> 50% across a hit. palette: the accent colours used by `noise` and `blocks`."""
    def __init__(self, rows, palette=("#39E6FF", "#FF2D7A", "#FFFFFF")):
        self.rows = [r if len(r) > 3 else (*r, {}) for r in rows]; self.palette = palette
    def apply(self, img, t):
        f = fk.frame_of(t)
        for (t0, kind, n, p) in self.rows:
            lf = f - fk.frame_of(t0)
            if not (0 <= lf < n): continue
            k = _k(lf, n)
            for m in kind.split("+"):
                if m == "slices": img = slices(img, f, k, n=p.get("n", 12), amp=p.get("amp", 0.09), seed=p.get("seed", 5))
                elif m == "rgb": img = rgb(img, k, px=p.get("px"))
                elif m == "blocks": img = blocks(img, f, k, cover=p.get("cover", 0.18), tint=p.get("tint", self.palette[0]))
                elif m == "sort": img = sort(img, f, k, cols=p.get("cols", 0.5))
                elif m == "wave": img = wave(img, t, k, amp=p.get("amp", 0.05))
                elif m == "static": img = static(img, f, k)
                elif m == "tear": img = tear(img, f, k)
                elif m == "noise": img = noise(img, f, k, colors=p.get("colors", self.palette))
                elif m == "invert": img = invert(img)
                elif m == "strobe": img = invert(img) if (lf // 2) % 2 == 0 else img
                elif m == "psych": img = psych(img, f, lf, n)
                elif m == "white": img = fk.whiteout(img, 1 - lf / max(1, n))
                elif m == "thermal": img = thermal(img, drift=30 * lf)
                elif m == "xray": img = xray(img)
                elif m == "error": img = error_card(img, f)
                elif m == "mirror": img = mirror(img)
        return img

# ------------------------------------------------------------------ type layer: composite, tear on entrances
class Layer(fk.Overlay):
    """fk.Overlay that skips decoding fully transparent frames (render_html writes them byte-identical), so a type or
    HUD layer that is empty most of the film costs nothing on those frames. Same arguments as fk.Overlay."""
    def __init__(self, folder, start=0.0, speed=1.0, fps=None):
        super().__init__(folder, start, speed, fps); import os
        sizes = [os.path.getsize(f) for f in self.files]; smin = min(sizes); first = self.files[sizes.index(smin)]
        im = cv2.imread(first, cv2.IMREAD_UNCHANGED); self.empty = set()
        if im is not None and im.ndim == 3 and im.shape[2] == 4 and im[..., 3].max() == 0:   # opaque frames are never empty
            ref = open(first, "rb").read()
            self.empty = {k for k, (f, z) in enumerate(zip(self.files, sizes)) if z == smin and open(f, "rb").read() == ref}
    def rgba(self, t):
        k = int(round((t - self.start) * self.speed * self.fps))
        return None if k in self.empty else super().rgba(t)

def tear_rgba(o, f, k=1.0, amp=0.07, n=10, seed=41):
    """slices + RGB split on the TYPE layer only (its entrances), before compositing."""
    o = slices(o, f, k, n=n, amp=amp, seed=seed, tear=False)
    W = o.shape[1]; px = max(1, int(W * 0.012 * k)); out = o.copy()
    out[:, px:, 2] = o[:, :-px, 2]; out[:, :-px, 0] = o[:, px:, 0]
    out[..., 3] = np.maximum(o[..., 3], np.maximum(np.roll(o[..., 3], px, 1), np.roll(o[..., 3], -px, 1)))
    return out

def over(img, ov, t, opacity=1.0, tears=()):
    """composite a filmkit Overlay; during a tear window (time, frames) the layer is torn first (type that tears)."""
    o = ov.rgba(t)
    if o is None: return img
    if o.shape[1] != img.shape[1] or o.shape[0] != img.shape[0]: o = cv2.resize(o, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_AREA)
    f = fk.frame_of(t)
    for (t0, n) in tears:
        lf = f - fk.frame_of(t0)
        if 0 <= lf < n: o = tear_rgba(o, f, _k(lf, n)); break
    al = o[..., 3]; rows = np.flatnonzero(al.max(1))
    if rows.size == 0: return img
    cols = np.flatnonzero(al[rows[0]:rows[-1] + 1].max(0)); y0, y1, x0, x1 = rows[0], rows[-1] + 1, cols[0], cols[-1] + 1
    a = o[y0:y1, x0:x1, 3:4].astype(np.float32) * (opacity / 255.0); out = img.copy()
    out[y0:y1, x0:x1] = (img[y0:y1, x0:x1] * (1 - a) + o[y0:y1, x0:x1, :3] * a).astype(np.uint8)
    return out

# ------------------------------------------------------------------ the budget (run before rendering)
BUDGETS = {   # per 15 s: hit clusters, frames per hit (drop stack may use 6), strobe/psych uses, full-frame flashes per 1 s
    "layer":  dict(clusters=5, frames=4, drop_frames=6, strobes=1, flashes=3, min_gap=0.9),
    "signal": dict(clusters=9, frames=4, drop_frames=6, strobes=2, flashes=3, min_gap=0.9),
    "hard":   dict(clusters=14, frames=6, drop_frames=8, strobes=3, flashes=3, min_gap=0.0),
}

def budget(rows, length, beat, preset="signal", drop=None, fps=None):
    """Prints the hit report and returns the list of violations (empty = within budget). Rules:
    every hit starts or ends on the 16th-note grid (+-1 frame); clusters (hits < 0.15 s apart) within the per-15 s
    budget; frames per hit; strobes; no family twice in a row; >= min_gap calm between clusters; photosensitivity:
    never more than 3 full-frame flashes in any 1 s."""
    fps = fps or fk.FPS; Bd = BUDGETS[preset]; rows = sorted(r[:3] for r in rows); bad = []
    grid = beat / 4; scale = length / 15.0
    on = lambda x: abs(x / grid - round(x / grid)) * grid <= 1.01 / fps
    clusters = []
    for r in rows:
        if clusters and r[0] - (clusters[-1][-1][0] + clusters[-1][-1][2] / fps) < 0.15: clusters[-1].append(r)
        else: clusters.append([r])
    for (t, kind, n) in rows:
        if not (on(t) or on(t + n / fps)): bad.append(f"{t:.3f} {kind}: not on the 16th grid")
        lim = Bd["drop_frames"] if drop is not None and abs(t - drop) < 0.2 else Bd["frames"]
        if kind.split("+")[0] in ("strobe", "psych"): lim = 14
        if n > lim: bad.append(f"{t:.3f} {kind}: {n} frames > {lim}")
    if len(clusters) > Bd["clusters"] * scale + 0.01: bad.append(f"{len(clusters)} hit clusters > {Bd['clusters'] * scale:.0f} for {length:.1f} s")
    st = sum(1 for r in rows if r[1].split("+")[0] in ("strobe", "psych"))
    if st > Bd["strobes"]: bad.append(f"{st} strobes/psych > {Bd['strobes']}")
    fam = [c[0][1].split("+")[0] for c in clusters]
    for a, b, c in zip(fam, fam[1:], clusters[1:]):
        if a == b: bad.append(f"{c[0][0]:.3f}: family '{b}' twice in a row")
    for c0, c1 in zip(clusters, clusters[1:]):
        gap = c1[0][0] - (c0[-1][0] + c0[-1][2] / fps)
        if gap < Bd["min_gap"] - 1e-6: bad.append(f"{c1[0][0]:.3f}: only {gap:.2f} s calm after the previous burst")
    flash = np.zeros(int(length * fps) + 2, bool)                                   # photosensitivity
    for (t, kind, n) in rows:
        f0 = int(round(t * fps))
        for lf in range(n):
            m = kind.split("+")
            if any(x in ("invert", "white", "static", "error") for x in m) or ("strobe" in m or "psych" in m) and (lf // 2) % 2 == 0:
                if 0 <= f0 + lf < len(flash): flash[f0 + lf] = True
    edges = np.flatnonzero(flash[1:] & ~flash[:-1]) + 1
    for e in edges:
        cnt = int(np.sum((edges >= e) & (edges < e + fps)))
        if cnt > Bd["flashes"]: bad.append(f"{e / fps:.2f}: {cnt} full-frame flashes within 1 s (max {Bd['flashes']})"); break
    hitf = sum(r[2] for r in rows); clean = 1 - hitf / (length * fps)
    print(f"glitch budget [{preset}]: {len(rows)} hits in {len(clusters)} clusters, {hitf} hit frames, clean {clean:.0%}, "
          f"{len(edges)} flashes")
    for b in bad: print("  !!", b)
    if not bad: print("  ok: within budget")
    return bad
