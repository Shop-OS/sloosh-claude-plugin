"""dotskit.py: the dot-matrix-particles style toolkit for edit.py. Frame-exact and fast (20-90 ms per 1080x1920 frame).

Sloosh makes CLEAN footage only (realistic stills on pure black -> clips animated from them). This module turns any
camera frame into dots AFTER filmkit's camera, so the grid is fixed to the screen and the image moves under it (that is
what makes it read as a real LED wall). Copy this file into the film's lib/ and `import dotskit as dk`.

Renderers (frame in, frame out; uint8 BGR at the film size):
  led(img, p, ramp=..)          LED panel: brightness by luminance through a colour ramp, unlit dots, row gap
  halftone(img, p, ink, angle)  print halftone: dot AREA by luminance (r = rmax * sqrt(L)), 0 or 45 deg screen
  ascii(img, cell, ink, t)      density-class glyphs, scramble flicker within the same density
  dither(img, p, tones, noise)  Bayer 8x8 ordered dither, 2-4 tones, noise -> clean resolve
  scanlines(img, ...)           rows of light pushed up by luminance (oscilloscope portrait)
  point_cloud(img, yaw, ..)     3D cloud from luminance depth, perspective, travelling scan band, implode
  thermal_reveal(img, lt)       thermal reveal: turbo heat map revealed by a moving gradient, hue drift, then real
  dot_grid(..)                  faint dot grid with an LED scan sweep (end cards)
Particles: points(img, p) -> sources; text_points(rgba) -> wordmark targets (sampled from the RENDERED type page, so
  the particles land exactly on the HTML wordmark); Assemble(...) -> particles fly into the wordmark.
Type: LEDText: copy rendered as a lit LED board (Archivo 125/900 rasterised to cells), switch-on sweep, auto-fit, marquee.
Modifiers: reveal_radial / reveal_sweep / reveal_random, burst / ripple / sweep fields (callables on cell coords).
Edit glue: apply_tags(img, cuts, t, PAL) reads `dots:*` cut-list tags; Transitions(cuts, rows) for halftone / dither
  wipes; FigureLock + lock_shots (figure lock: same spot and size in every shot).
"""
import math, os, glob
import numpy as np
import cv2
import filmkit as fk

TAU = 2 * math.pi
_cache = {}

# ------------------------------------------------------------------ helpers
def hexrgb(h): return fk.hex2bgr(h)                      # BGR float32
def win(t, a, d, ease=None):
    x = min(1.0, max(0.0, (t - a) / d)) if d > 0 else float(t >= a)
    if ease == "out": return 1 - (1 - x) ** 4
    if ease == "expo": return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)
    if ease == "in": return x ** 3
    if ease == "inout": return 0.5 - 0.5 * math.cos(math.pi * x)
    return x

def ramp_lut(stops):
    """N-stop colour ramp (dark -> ink -> hot) as a 256 x 3 BGR LUT."""
    S = np.array([hexrgb(s) for s in stops], np.float32); x = np.linspace(0, len(S) - 1, 256)
    k = np.minimum(len(S) - 2, x.astype(int)); f = (x - k)[:, None]; return (S[k] * (1 - f) + S[k + 1] * f).astype(np.float32)

def hash2(x, y, s):
    """stateless hash of integer arrays -> 0..1 (vectorised)."""
    h = (x.astype(np.int64) * 374761393 + y.astype(np.int64) * 668265263 + int(s) * 1442695041) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF; h ^= h >> 16; return (h & 0xFFFFFFFF).astype(np.float64) / 4294967296.0

def geom(W, H, p):
    cols, rows = W // p, H // p; return cols, rows, (W - cols * p) // 2, (H - rows * p) // 2

AUTO = True       # auto-exposure: the brightest 0.5% of cells map to full brightness (a dim plate still lights the panel)
def expose(L, floor=0.3):
    if not AUTO: return L
    return np.clip(L / max(floor, float(np.percentile(L, 99.5))), 0, 1)

def cells(img, p, gamma=1.0, lift=0.0, gain=1.0):
    """luminance (rows x cols, 0..1, auto-exposed) and colour (rows x cols x 3) of the frame on a p-pixel grid + geometry."""
    H, W = img.shape[:2]; cols, rows, ox, oy = geom(W, H, p)
    sm = cv2.resize(img[oy:oy + rows * p, ox:ox + cols * p], (cols, rows), interpolation=cv2.INTER_AREA)
    L = expose(cv2.cvtColor(sm, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0)
    if lift or gain != 1 or gamma != 1: L = np.clip((L - lift) / (1 - lift) * gain, 0, 1) ** gamma
    return L, sm, (cols, rows, ox, oy)

def cellxy(cols, rows):
    key = ("xy", cols, rows)
    if key not in _cache:
        ny, nx = np.mgrid[0:rows, 0:cols].astype(np.float32); _cache[key] = ((nx + 0.5) / cols, (ny + 0.5) / rows)
    return _cache[key]

def _disk(p, r, soft=0.9):
    yy, xx = np.mgrid[0:p, 0:p].astype(np.float32) + 0.5; d = np.hypot(xx - p / 2, yy - p / 2)
    return np.clip((r - d) / soft + 0.5, 0, 1)

def _place(img_shape, tile_img, ox, oy, bg):
    H, W = img_shape[:2]; out = np.empty((H, W, 3), np.uint8); out[:] = bg.astype(np.uint8)
    h, w = tile_img.shape[:2]; out[oy:oy + h, ox:ox + w] = tile_img; return out

def _value(L, reveal=None, field=None, mask_field=False, invert=False, threshold=None):
    v = (1 - L) * (L > 0.02) if invert else L.copy()
    if threshold is not None: v = np.where(v < threshold, 0, v)
    nx, ny = cellxy(L.shape[1], L.shape[0])
    if reveal is not None: v = v * reveal(nx, ny)
    if field is not None: v = v + field(nx, ny) * (np.clip(L * 4, 0, 1) if mask_field else 1)
    return v

# ------------------------------------------------------------------ modifiers (return f(nx, ny) on cell centres 0..1)
def _asp(): return fk.H / fk.W
def reveal_radial(u, x=0.5, y=0.5, soft=0.12, maxr=1.25):
    R = maxr * u; a = _asp(); return lambda nx, ny: np.clip((R - np.hypot(nx - x, (ny - y) * a)) / soft + 0.5, 0, 1)
def reveal_sweep(u, angle=90, soft=0.15):
    r = math.radians(angle); ca, sa = math.cos(r), math.sin(r)
    return lambda nx, ny: np.clip((u * (1.5 + soft) - ((nx - .5) * sa - (ny - .5) * ca + .75)) / soft + 0.5, 0, 1)
def reveal_random(u, seed=5, soft=0.25):
    return lambda nx, ny: np.clip((u * (1 + soft) - hash2((nx * 4096).astype(int), (ny * 4096).astype(int), seed)) / soft, 0, 1)
def burst(x=0.5, y=0.4, rays=8, width=0.05, core=0.09, amp=1.0, spin=0.0):
    """light burst with dot rays (the DROP). amp animates it 0.15 -> 1.65."""
    a = _asp()
    def f(nx, ny):
        dx, dy = nx - x, (ny - y) * a; r = np.hypot(dx, dy); th = np.arctan2(dy, dx) + spin
        ray = np.abs(np.cos(th * rays / 2)) ** (1 / max(0.01, width)) * np.exp(-r / (0.55 * amp + 1e-3))
        return amp * (np.exp(-(r * r) / (2 * core * core * amp * amp + 1e-4)) * 1.4 + ray * 0.9)
    return f
def ripple(x=0.5, y=0.5, t=0.0, wavelength=0.05, speed=0.6, amp=0.22, decay=2.4):
    a = _asp(); front = t * speed
    def f(nx, ny):
        r = np.hypot(nx - x, (ny - y) * a); return np.where(r > front, 0, amp * np.sin((r - front) / wavelength * TAU) * np.exp(-(front - r) * decay))
    return f
def sweep(pos=0.5, width=0.03, amp=0.6):
    return lambda nx, ny: amp * np.exp(-((ny - pos) ** 2) / (2 * width * width))

# ------------------------------------------------------------------ renderers
def led(img, p=12, ramp=("#070403", "#5A1E0C", "#FFB45A", "#FFF3DC"), unlit=0.07, size=0.8, row_gap=2, color=False, mix=0.6,
        reveal=None, field=None, invert=False, gamma=1.0, square=False, L=None):
    """LED panel: every cell a dot whose brightness follows luminance through `ramp`; off LEDs stay visible at `unlit`."""
    H, W = img.shape[:2]
    if L is None: L, sm, (cols, rows, ox, oy) = cells(img, p, gamma)
    else: sm = None; cols, rows, ox, oy = geom(W, H, p)
    v = np.clip(_value(L, reveal, field, invert=invert), 0, 1.5); v = unlit + (1 - unlit) * np.clip(v, 0, 1)
    lut = ramp_lut(ramp); col = lut[(v * 255).astype(np.uint8)]
    if color and sm is not None: col = col * mix + sm.astype(np.float32) * (1 - mix) * v[..., None]
    key = ("ledmask", p, size, row_gap, square, cols, rows)
    if key not in _cache:
        r = (p - row_gap) * 0.5 * size; t = np.ones((p, p), np.float32) * (abs(np.arange(p) + .5 - p / 2) < r)[None, :] * (abs(np.arange(p) + .5 - (p - row_gap) / 2) < r)[:, None] if square else _disk(p, r)
        if not square and row_gap: t = np.roll(t, -row_gap // 2, axis=0)
        _cache[key] = np.tile(t, (rows, cols))[..., None]
    m = _cache[key]; bg = lut[0]
    up = cv2.resize(col, (cols * p, rows * p), interpolation=cv2.INTER_NEAREST)
    return _place(img.shape, (bg + (up - bg) * m).astype(np.uint8), ox, oy, bg)

def _halftone_straight(img, p, ink, bg, size, min_r, reveal, field, color, K=24, gamma=1.0):
    H, W = img.shape[:2]; L, sm, (cols, rows, ox, oy) = cells(img, p, gamma)
    v = np.clip(_value(L, reveal, field, mask_field=True), 0, 1.6)
    key = ("hbank", p, size, K)
    if key not in _cache:
        rmax = p * 0.5 * size; _cache[key] = np.stack([_disk(p, rmax * k / K) * (rmax * k / K >= min_r) for k in range(K + 1)])
    idx = np.clip(np.round(np.sqrt(v / 1.0) * K), 0, K).astype(np.int32)
    cov = _cache[key][idx].transpose(0, 2, 1, 3).reshape(rows * p, cols * p)[..., None]
    bgc = hexrgb(bg)
    if color: c = cv2.resize(sm, (cols * p, rows * p), interpolation=cv2.INTER_NEAREST).astype(np.float32)
    else: c = hexrgb(ink)
    return _place(img.shape, (bgc + (c - bgc) * cov).astype(np.uint8), ox, oy, bgc)

def halftone(img, p=12, ink="#FFB45A", bg="#070403", size=1.12, angle=0, min_r=0.6, reveal=None, field=None, color=False, gamma=1.0):
    """print halftone: dot area by luminance. angle 0 = billboard grid, 45 = print/editorial (rendered on a rotated
    frame, so the screen is truly at 45 deg). Print styles never glow: no bloom after this."""
    if not angle: return _halftone_straight(img, p, ink, bg, size, min_r, reveal, field, color, gamma=gamma)
    H, W = img.shape[:2]; D = int(math.ceil(math.hypot(W, H))); D += (-D) % p
    M = cv2.getRotationMatrix2D((W / 2, H / 2), -angle, 1.0); M[0, 2] += (D - W) / 2; M[1, 2] += (D - H) / 2
    big = cv2.warpAffine(img, M, (D, D), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0))
    out = _halftone_straight(big, p, ink, bg, size, min_r, None, None, color, gamma=gamma)
    Mi = cv2.invertAffineTransform(M)
    return cv2.warpAffine(out, Mi, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=tuple(float(c) for c in hexrgb(bg)))

CLASSES = [" ", ".,'`", ":;-~", "=+<>^\"", "?7tfjl1i/", "xzsvcrnu", "aeo23569", "kdbpqhyg$", "AKXVYZ4%&", "#@MW08B"]
def _wide_axes(ft):
    """Archivo variable font: weight 900, width 125, set by axis name (axis order differs between builds)."""
    try:
        want = {"weight": 900, "wght": 900, "width": 125, "wdth": 125}; vals = []
        for ax in ft.get_variation_axes():
            nm = ax.get("name", b""); nm = nm.decode("ascii", "ignore") if isinstance(nm, bytes) else str(nm)
            v = want.get(nm.strip().lower(), ax.get("default", ax.get("minimum", 0)))
            vals.append(min(max(v, ax.get("minimum", v)), ax.get("maximum", v)))
        ft.set_variation_by_axes(vals)
    except Exception:
        pass

def _font(size, kind="mono"):
    """film fonts first (fonts/*.woff2, vendored by new_film.sh), then system fonts, then Pillow's default.
    Pillow reads woff2 only when its FreeType has brotli; otherwise the next font in the list is used."""
    from PIL import ImageFont
    pats = {"mono": ["fonts/jetbrains-mono-latin-500-normal.woff2", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
                     "/System/Library/Fonts/Menlo.ttc", "/System/Library/Fonts/Monaco.ttf"],
            "wide": ["fonts/archivo-latin-wdth-normal.woff2", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                     "/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/Library/Fonts/Arial Bold.ttf",
                     "/System/Library/Fonts/Helvetica.ttc"]}[kind]
    for f in pats:
        if not os.path.exists(f): continue
        try: ft = ImageFont.truetype(f, size)
        except OSError: continue
        if kind == "wide" and f.endswith("woff2"): _wide_axes(ft)
        return ft
    try: return ImageFont.load_default(size)
    except TypeError: return ImageFont.load_default()

def _glyphs(cw, ch):
    key = ("glyphs", cw, ch)
    if key not in _cache:
        from PIL import Image, ImageDraw
        chars = sorted(set("".join(CLASSES))); ft = _font(int(ch * 0.92)); tiles = []
        for c in chars:
            im = Image.new("L", (cw, ch), 0); d = ImageDraw.Draw(im); d.text((cw / 2, ch / 2), c, fill=255, font=ft, anchor="mm"); tiles.append(np.asarray(im, np.float32) / 255)
        idx = {c: i for i, c in enumerate(chars)}; ml = max(len(c) for c in CLASSES)
        table = np.array([[idx[c[j % len(c)]] for j in range(ml)] for c in CLASSES], np.int32)
        _cache[key] = (np.stack(tiles), table, ml)
    return _cache[key]

def ascii(img, cell=20, ink="#FFD9A8", bg="#070403", t=0.0, scramble=12, floor=0.08, seed=9, reveal=None, field=None, gamma=1.0):
    """ASCII portrait: glyph density by luminance; scramble changes glyphs within the same density class 12x/s, so
    it shimmers without changing the picture. Decorative only: never for text the viewer must read."""
    H, W = img.shape[:2]; ch = cell; cw = max(8, int(round(cell * 0.6)))
    cols, rows = W // cw, H // ch; ox, oy = (W - cols * cw) // 2, (H - rows * ch) // 2
    sm = cv2.resize(img[oy:oy + rows * ch, ox:ox + cols * cw], (cols, rows), interpolation=cv2.INTER_AREA)
    L = expose(cv2.cvtColor(sm, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0)
    if gamma != 1: L = L ** gamma
    L = np.clip(_value(L, reveal, field), 0, 1)
    tiles, table, ml = _glyphs(cw, ch); cls = np.clip(1 + (L * (len(CLASSES) - 1)).astype(int), 1, len(CLASSES) - 1)
    yy, xx = np.mgrid[0:rows, 0:cols]; fr = int(t * scramble) if scramble else 0
    pick = (hash2(xx, yy, seed + fr * 7919) * ml).astype(int); g = table[cls, pick]
    a = tiles[g] * ((0.35 + 0.65 * L) * (L >= floor))[..., None, None]
    cov = a.transpose(0, 2, 1, 3).reshape(rows * ch, cols * cw)[..., None]
    bgc, ic = hexrgb(bg), hexrgb(ink)
    return _place(img.shape, (bgc + (ic - bgc) * cov).astype(np.uint8), ox, oy, bgc)

B8 = np.array([0,32,8,40,2,34,10,42,48,16,56,24,50,18,58,26,12,44,4,36,14,46,6,38,60,28,52,20,62,30,54,22,
               3,35,11,43,1,33,9,41,51,19,59,27,49,17,57,25,15,47,7,39,13,45,5,37,63,31,55,23,61,29,53,21], np.float32).reshape(8, 8)
def dither(img, p=4, tones=("#0A0A0A", "#6E6E6A", "#F2F2EE"), noise=0.0, t=0.0, fps=12, reveal=None, gamma=1.0):
    """Bayer 8x8 ordered dither in 2-4 tones; `noise` 1 -> 0 resolves random noise into the clean picture."""
    H, W = img.shape[:2]; L, _, (cols, rows, ox, oy) = cells(img, p, gamma); L = np.clip(_value(L, reveal), 0, 1)
    if noise:
        yy, xx = np.mgrid[0:rows, 0:cols]; L = L * (1 - noise) + hash2(xx, yy, int(t * fps)).astype(np.float32) * noise
    th = (np.tile(B8, (rows // 8 + 1, cols // 8 + 1))[:rows, :cols] + 0.5) / 64; nT = len(tones) - 1
    v = L * nT; k = np.minimum(nT, np.floor(v) + (v - np.floor(v) > th)).astype(int)
    T = np.array([hexrgb(c) for c in tones], np.uint8); small = T[k]
    return _place(img.shape, cv2.resize(small, (cols * p, rows * p), interpolation=cv2.INTER_NEAREST), ox, oy, T[0].astype(np.float32))

def scanlines(img, row=8, px=6, ink="#FFC24A", bg="#000000", amp=18, width=2, wobble=2.5, t=0.0, thr=0.08, gamma=1.0):
    """oscilloscope portrait: one line of light per row, pushed up by luminance (cv2.polylines, anti-aliased)."""
    H, W = img.shape[:2]; cols, rows = W // px, H // row
    L = expose(cv2.cvtColor(cv2.resize(img, (cols, rows), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0)
    if gamma != 1: L = L ** gamma
    out = np.empty((H, W, 3), np.uint8); out[:] = hexrgb(bg).astype(np.uint8); xs = (np.arange(cols) + 0.5) * px; polys = []
    for y in range(rows):
        Ly = L[y]; on = Ly >= thr
        if not on.any(): continue
        yy = y * row + row / 2 - Ly * amp + np.sin(np.arange(cols) * 0.42 + t * 6.9 + y * 1.7) * wobble * Ly
        idx = np.flatnonzero(on); splits = np.flatnonzero(np.diff(idx) > 1) + 1
        for seg in np.split(idx, splits):
            if len(seg) > 1: polys.append(np.stack([xs[seg], yy[seg]], 1).astype(np.int32))
    cv2.polylines(out, polys, False, tuple(int(c) for c in hexrgb(ink)), width, cv2.LINE_AA)
    return out

def _splat(H, W, xs, ys, w, sigma=1.2):
    acc = np.zeros((H, W), np.float32); xi, yi = xs.astype(np.int32), ys.astype(np.int32)
    ok = (xi >= 0) & (yi >= 0) & (xi < W) & (yi < H); np.add.at(acc, (yi[ok], xi[ok]), w[ok])
    return cv2.GaussianBlur(acc, (0, 0), sigma) * (2 * math.pi * sigma * sigma) * 0.55

def point_cloud(img, yaw=0.0, pitch=0.06, p=7, depth=0.42, scale=None, cy=0.52, ink="#FFB45A", hot="#FFF3DC", bg="#070403",
                scan_y=None, scan_w=0.022, reveal=1.0, base=0.3, lum_gain=0.7, implode=0.0, thr=0.05, sigma=1.3):
    """3D point cloud: points where the subject is lit, depth from smoothed luminance (so the plate needs a hard key),
    yaw/pitch rotation with perspective, a hot scan band, `reveal` builds it top-down, `implode` collapses it to a core."""
    H, W = img.shape[:2]; L, _, (cols, rows, ox, oy) = cells(img, p)
    Z = cv2.blur(L, (5, 5)); ys, xs = np.nonzero(L > thr); Lv = L[ys, xs]; asp = rows / cols
    X = xs / cols - 0.5; Y = (ys / rows - 0.5) * asp; Zp = (Z[ys, xs] - 0.5) * depth
    keep = Y <= (reveal * 1.4 - 0.7) * asp if reveal < 1 else np.ones_like(Y, bool)
    cyw, syw, cp, sp = math.cos(yaw), math.sin(yaw), math.cos(pitch), math.sin(pitch)
    x = X * cyw + Zp * syw; z = -X * syw + Zp * cyw; y = Y * cp - z * sp; z = Y * sp + z * cp
    F = 2.2; per = F / (F + z); S = (scale or W * 0.92) * (1 - 0.88 * implode)
    sx = W / 2 + x * S * per; sy = H * cy + y * S * per
    a = (base + lum_gain * Lv) * np.clip(0.55 + 1.8 * (per - 0.85), 0.25, 1) * (1 + 2.5 * implode)
    hotw = np.zeros_like(a)
    if scan_y is not None:
        d = np.abs(Y / asp - scan_y); b = np.exp(-(d * d) / (2 * scan_w * scan_w)); hotw = b * (d < 3 * scan_w); a = a * (1 - hotw)
    A = _splat(H, W, sx[keep], sy[keep], a[keep], sigma); Hh = _splat(H, W, sx[keep], sy[keep], hotw[keep] * 1.4, sigma)
    out = hexrgb(bg) + np.clip(A, 0, 1.2)[..., None] * (hexrgb(ink) - hexrgb(bg)) + np.clip(Hh, 0, 1.2)[..., None] * hexrgb(hot)
    return np.clip(out, 0, 255).astype(np.uint8)

def thermal(img, drift=0.0):
    """turbo false colour on luminance; black stays black (the map is multiplied by a soft luminance key)."""
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY); g = cv2.normalize(g, None, 0, 255, cv2.NORM_MINMAX)
    th = cv2.applyColorMap(g, cv2.COLORMAP_TURBO)
    th = cv2.multiply(th, cv2.merge([np.clip(g.astype(np.float32) * 4, 0, 255).astype(np.uint8)] * 3), scale=1 / 255)
    if drift:
        hsv = cv2.cvtColor(th, cv2.COLOR_BGR2HSV); hsv[..., 0] = ((hsv[..., 0].astype(np.int16) + int(drift / 2)) % 180).astype(np.uint8)
        th = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return th

def thermal_reveal(img, lt, dur=0.9, hold=0.5, soft=0.18, to_real=0.4):
    """thermal reveal: the heat-map version rises bottom -> top through a soft gradient mask over `dur` s with a
    slow hue drift, holds, then cross-fades into the real frame over `to_real` s."""
    H, W = img.shape[:2]; th = thermal(img, drift=24 * lt); u = win(lt, 0, dur, "out")
    m = np.clip((u * (1 + soft) - (1 - (np.arange(H, dtype=np.float32) + .5) / H)) / soft, 0, 1)[:, None, None]
    edge = np.exp(-((m - 0.5) / 0.08) ** 2) * 0.9 * (u < 1)                        # the front glows in the heat colours
    out = np.clip(th * (m + edge), 0, 255).astype(np.uint8)
    k = win(lt, dur + hold, to_real, "inout")
    return cv2.addWeighted(out, 1 - k, img, k, 0) if k > 0 else out

def dot_grid(shape, p=30, r=1.7, alpha=0.14, ink="#FFB45A", bg="#070403", sweep_pos=None, sweep_w=0.035, sweep_amp=0.35):
    """faint end-card dot grid; a slow LED scan line (sweep_pos 0..1 top -> bottom) keeps the card alive."""
    H, W = shape[:2]; cols, rows, ox, oy = geom(W, H, p); a = np.full((rows, 1), alpha, np.float32)
    if sweep_pos is not None: a = a + sweep_amp * np.exp(-((((np.arange(rows) + .5) / rows - sweep_pos) / sweep_w) ** 2) / 2)[:, None]
    key = ("grid", p, r, cols, rows)
    if key not in _cache: _cache[key] = np.tile(_disk(p, r), (rows, cols))
    m = (_cache[key] * np.repeat(np.repeat(a, p, 0), cols * p, 1))[..., None]; bgc = hexrgb(bg)
    return _place(shape, (bgc + (hexrgb(ink) - bgc) * np.clip(m, 0, 1)).astype(np.uint8), ox, oy, bgc)

def bloom(img, strength=0.7, radius=20):
    """light styles glow (LED, ASCII, point cloud): quarter-res blur added back. Never on print styles."""
    H, W = img.shape[:2]; sm = cv2.resize(img, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    g = cv2.resize(cv2.GaussianBlur(sm, (0, 0), radius / 4), (W, H), interpolation=cv2.INTER_LINEAR)
    return cv2.addWeighted(img, 1.0, g, strength, 0)

# ------------------------------------------------------------------ particles
def points(img, p=12, thr=0.06):
    """particles from the same p-grid the halftone/LED used (seamless hand-off): array of [x, y, lum, b, g, r]."""
    L, sm, (cols, rows, ox, oy) = cells(img, p); ys, xs = np.nonzero(L > thr)
    return np.column_stack([ox + (xs + .5) * p, oy + (ys + .5) * p, L[ys, xs], sm[ys, xs].astype(np.float32)]).astype(np.float32)

def text_points(rgba, step=6, thr=128):
    """wordmark targets sampled from a RENDERED type frame (fk.Overlay(...).rgba(t)): particles land exactly on the
    HTML wordmark that fades in over them."""
    a = rgba[::step, ::step, 3]; ys, xs = np.nonzero(a > thr)
    return np.column_stack([xs * step + step / 2, ys * step + step / 2, np.ones(len(xs)), rgba[ys * step, xs * step, :3].astype(np.float32)]).astype(np.float32)

def pair(A, B, seed=17, key=lambda P: P[:, 0] * 0.7 + P[:, 1] * 0.3):
    """resample both sets to n = max(len) with a seeded pick, sort both by the same key: coherent flow, no crossings."""
    n = max(len(A), len(B)); r = np.random.default_rng(seed)
    pick = lambda S: S if len(S) == n else np.concatenate([S, S[r.integers(0, len(S), n - len(S))]])
    a, b = pick(A), pick(B); a, b = a[np.argsort(key(a), kind="stable")], b[np.argsort(key(b), kind="stable")]
    return a, b, np.random.default_rng(seed + 1).random(n).astype(np.float32)

def _disk_k(r):
    r = max(0.6, r); n = int(math.ceil(r)) * 2 + 1; return _disk(n, r, 0.8)

def morph(shape, pairs, u, ink_a="#FFB45A", ink_b="#FFF3DC", bg="#070403", size_a=13.4, size=3.2, stagger=0.45, swirl=170, alpha=1.0):
    """particles fly from A (halftone dots, diameter size_a * sqrt(lum)) to B (the wordmark), staggered, with a
    perpendicular swirl mid-flight. Drawn additively in 4 size buckets (disk kernels)."""
    H, W = shape[:2]; A, Bp, h = pairs; kk = np.clip((u - h * stagger) / (1 - stagger), 0, 1); e = 0.5 - 0.5 * np.cos(np.pi * kk)
    dx, dy = Bp[:, 0] - A[:, 0], Bp[:, 1] - A[:, 1]; ln = np.hypot(dx, dy) + 1e-6; bul = np.sin(e * np.pi) * swirl * (h - 0.5) * 2
    x = A[:, 0] + dx * e - dy / ln * bul; y = A[:, 1] + dy * e + dx / ln * bul
    d = size_a * np.sqrt(A[:, 2]) * (1 - np.clip(e * 2.2, 0, 1)) + size * np.clip(e * 2.2, 0, 1)
    w = alpha * (1.0 * (1 - e) + (0.35 + 0.65 * Bp[:, 2]) * e)
    acc_a = np.zeros((H, W), np.float32); acc_b = np.zeros((H, W), np.float32)
    edges = np.quantile(d, [0, .25, .5, .75, 1.0]) if len(d) else [0, 1]
    for i in range(len(edges) - 1):
        sel = (d >= edges[i]) & ((d < edges[i + 1]) if i < len(edges) - 2 else (d <= edges[i + 1]))
        if not sel.any(): continue
        k = _disk_k(float(np.median(d[sel])) / 2)
        for acc, ww in ((acc_a, w * (1 - e)), (acc_b, w * e)):
            s = np.zeros((H, W), np.float32); xi, yi = x[sel].astype(int), y[sel].astype(int); ok = (xi >= 0) & (yi >= 0) & (xi < W) & (yi < H)
            np.add.at(s, (yi[ok], xi[ok]), ww[sel][ok]); acc += cv2.filter2D(s, -1, k)
    bgc = hexrgb(bg); out = bgc + np.clip(acc_a, 0, 1)[..., None] * (hexrgb(ink_a) - bgc) + np.clip(acc_b, 0, 1.3)[..., None] * hexrgb(ink_b)
    return np.clip(out, 0, 255).astype(np.uint8)

def dissolve(shape, P, u, ink="#FFD08A", bg="#070403", size=4, wind=None, turb=80, spread=0.5, order="x", seed=3):
    """image-as-particles blown away (u 0 intact -> 1 gone); pass 1 - u to assemble from dust."""
    H, W = shape[:2]; wind = wind or (W * 0.9, -H * 0.1); n = len(P); r = np.random.default_rng(seed); h, h2 = r.random(n), r.random(n)
    ordv = {"x": P[:, 0] / W, "-x": 1 - P[:, 0] / W, "y": P[:, 1] / H}.get(order, h); ordv = np.clip(ordv * 0.8 + h * 0.2, 0, 1)
    kk = np.clip((u - ordv * (1 - spread)) / spread, 0, 1); e = kk * kk
    x = P[:, 0] + wind[0] * e * (0.6 + 0.8 * h) + np.sin(h2 * 40 + kk * 7) * turb * kk
    y = P[:, 1] + wind[1] * e * (0.6 + 0.8 * h2) + np.cos(h * 40 + kk * 5) * turb * kk
    a = (1 - kk ** 1.4) * (0.35 + 0.65 * P[:, 2]); A = _splat(H, W, x, y, a, sigma=size / 2.4)
    bgc = hexrgb(bg); return np.clip(bgc + np.clip(A, 0, 1)[..., None] * (hexrgb(ink) - bgc), 0, 255).astype(np.uint8)

class Assemble:
    """particles from the halftone of the shot -> the wordmark. src_frame: the REAL camera frame at the hand-off time
    (cuts.render(t_from)); target_rgba: the type layer's frame where the wordmark is fully in. Same pitch as the
    halftone before it and size_a = its dot diameter: the hand-off is invisible."""
    def __init__(self, src_frame, target_rgba, t_from, t_to, p=12, size_a=None, fade_from=None, fade=0.45, PAL=None, seed=17):
        PAL = PAL or {}; self.pairs = pair(points(src_frame, p), text_points(target_rgba), seed)
        self.t0, self.t1, self.fade_from, self.fade = t_from, t_to, fade_from or t_to, fade
        self.size_a = size_a or p * 1.12; self.PAL = PAL
    def render(self, shape, t):
        u = win(t, self.t0, self.t1 - self.t0); al = 1 - win(t, self.fade_from, self.fade, "out")
        P = self.PAL; return morph(shape, self.pairs, u, P.get("INK", "#FFB45A"), P.get("HOT", "#FFF3DC"), P.get("BG", "#070403"), self.size_a, alpha=al)

# ------------------------------------------------------------------ LED board type (a dot-matrix display face in code)
class LEDText:
    """copy rendered as a lit LED board. Each line is rasterised with Archivo 125/900 at cell resolution (cap height
    `cap` cells), measured, auto-fit to the safe width (cap shrinks to `min_cap`, then it scrolls as a marquee).
    In: a left -> right switch-on sweep over 0.25 s with a flicker front. Out: rows switch off top -> bottom in 0.15 s.
      board = dk.LEDText(["MADE OF", "LIGHT"], p=12, cap=11, y=300, safe=(120, 960))
      img = board.over(img, t, t_in, t_out)"""
    def __init__(self, lines, p=12, cap=11, y=300, safe=(120, 960), line_gap=3, ramp=("#070403", "#5A1E0C", "#FFB45A", "#FFF3DC"),
                 unlit=0.07, min_cap=7, panel=0.82, scroll_cps=14):
        from PIL import Image, ImageDraw
        self.p, self.y, self.ramp, self.unlit, self.panel, self.scroll = p, y, ramp, unlit, panel, scroll_cps
        maxc = int((safe[1] - safe[0]) // p); self.safe = safe; rasters = []
        for ln in lines:
            c = cap
            while True:
                S = 8; ft = _font(int(c * S / 0.72), "wide"); x0, y0, x1, y1 = ft.getbbox(ln)
                im = Image.new("L", (x1 - x0 + 2 * S, int(c * S / 0.72 * 1.05)), 0)
                ImageDraw.Draw(im).text((S - x0, int(c * S / 0.72 * 0.98)), ln, fill=255, font=ft, anchor="ls")
                a = np.asarray(im, np.float32) / 255; h = int(round(a.shape[0] / S)); w = int(round(a.shape[1] / S))
                cellm = cv2.resize(a, (w, h), interpolation=cv2.INTER_AREA) > 0.42
                rows = np.flatnonzero(cellm.any(1)); cellm = cellm[rows[0]:rows[-1] + 1] if rows.size else cellm
                if cellm.shape[1] <= maxc or c <= min_cap: break
                c -= 1
            rasters.append(cellm)
        self.cols = maxc; self.rows = sum(r.shape[0] for r in rasters) + line_gap * (len(rasters) - 1) + 2
        self.board = np.zeros((self.rows, max(maxc, max(r.shape[1] for r in rasters))), np.float32); yy = 1; self.wide = []
        for r in rasters:
            off = max(0, (maxc - r.shape[1]) // 2); self.board[yy:yy + r.shape[0], off:off + r.shape[1]] = r; self.wide.append(r.shape[1] > maxc); yy += r.shape[0] + line_gap
        self.lut = ramp_lut(ramp); r0 = (p - 2) * 0.5 * 0.8; self.tile = np.roll(_disk(p, r0), -1, axis=0)
    def over(self, img, t, t_in, t_out):
        if t < t_in or t >= t_out + 0.15: return img
        p, R, C = self.p, self.rows, self.cols; b = self.board
        if any(self.wide): sh = int((t - t_in) * self.scroll) % b.shape[1]; b = np.roll(b, -sh, axis=1)
        b = b[:, :C]; xx = (np.arange(C) + .5) / C; yy = (np.arange(R) + .5) / R
        u = win(t, t_in, 0.25); front = np.clip((u * 1.25 - xx) / 0.08, 0, 1)[None, :]
        fl = hash2(np.arange(C)[None, :] + 0 * np.arange(R)[:, None], np.arange(R)[:, None] + 0 * np.arange(C)[None, :], int(t * 30))
        lit = b * front * np.where((front > 0) & (front < 1), fl > 0.4, 1)
        if t >= t_out: lit = lit * (yy[:, None] > win(t, t_out, 0.15))
        v = self.unlit + (1 - self.unlit) * lit; col = self.lut[(v * 255).astype(np.uint8)]
        up = cv2.resize(col, (C * p, R * p), interpolation=cv2.INTER_NEAREST); m = np.tile(self.tile, (R, C))[..., None]
        x0 = int(self.safe[0] + ((self.safe[1] - self.safe[0]) - C * p) / 2); y0 = int(self.y); H, W = img.shape[:2]
        h, w = min(R * p, H - y0), min(C * p, W - x0); out = img.copy(); reg = out[y0:y0 + h, x0:x0 + w].astype(np.float32)
        bg = self.lut[0]; panel = reg * (1 - self.panel) + bg * self.panel
        out[y0:y0 + h, x0:x0 + w] = np.clip(panel + (up[:h, :w] - bg) * m[:h, :w] * (up[:h, :w].sum(2, keepdims=True) > 0), 0, 255).astype(np.uint8)
        return out

# ------------------------------------------------------------------ overlays
def _bytes(path):
    with open(path, "rb") as fh: return fh.read()

class Layer(fk.Overlay):
    """fk.Overlay that skips decoding fully transparent frames (render_html writes them byte-identical)."""
    def __init__(self, folder, start=0.0, speed=1.0, fps=None):
        super().__init__(folder, start, speed, fps)
        sizes = [os.path.getsize(f) for f in self.files]; smin = min(sizes); first = self.files[sizes.index(smin)]
        im = cv2.imread(first, cv2.IMREAD_UNCHANGED); self.empty = set()
        if im is not None and (im.ndim < 3 or im.shape[2] < 4 or im[..., 3].max() == 0):
            ref = _bytes(first)
            self.empty = {k for k, (f, z) in enumerate(zip(self.files, sizes)) if z == smin and _bytes(f) == ref}
    def rgba(self, t):
        k = int(round((t - self.start) * self.speed * self.fps))
        return None if k in self.empty else super().rgba(t)

def over(img, ov, t, opacity=1.0):
    """composite an Overlay, only inside its alpha bounding box (cheap for small type)."""
    o = ov.rgba(t)
    if o is None: return img
    if o.shape[:2] != img.shape[:2]: o = cv2.resize(o, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_AREA)
    al = o[..., 3]; rows = np.flatnonzero(al.max(1))
    if rows.size == 0: return img
    cols = np.flatnonzero(al[rows[0]:rows[-1] + 1].max(0)); y0, y1, x0, x1 = rows[0], rows[-1] + 1, cols[0], cols[-1] + 1
    a = o[y0:y1, x0:x1, 3:4].astype(np.float32) * (opacity / 255.0); out = img.copy()
    out[y0:y1, x0:x1] = (img[y0:y1, x0:x1] * (1 - a) + o[y0:y1, x0:x1, :3] * a).astype(np.uint8)
    return out

# ------------------------------------------------------------------ figure lock
def measure_figure(img, thr=40):
    """centre and height of the lit figure (pixels above `thr` luma), measured at quarter resolution. Robust to specks
    and stray highlights: the box spans the 1st-99th percentile of lit pixels."""
    H, W = img.shape[:2]; g = cv2.cvtColor(cv2.resize(img, (W // 4, H // 4), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY) > thr
    ys, xs = np.nonzero(g)
    if len(ys) < 20: return None
    lo, hi = np.percentile(ys, [1, 99]); return float(np.median(xs) * 4), float((lo + hi) * 2), float((hi - lo) * 4)

class FigureLock:
    """wraps a filmkit Clip: every source frame is scaled and moved so the figure sits at target (cx, cy) with height
    h (px), smoothed over +-smooth source frames. The cut list then applies its camera on top."""
    def __init__(self, clip, target, thr=40, smooth=3):
        self.c, self.target, self.thr, self.smooth, self.m = clip, target, thr, smooth, {}
        self.kind = clip.kind; self.duration = getattr(clip, "duration", 0)
    def _meas(self, i):
        if i not in self.m: self.m[i] = measure_figure(self.c._read(i) if self.kind == "video" else self.c.img, self.thr)
        return self.m[i]
    def frame(self, t):
        img = self.c.frame(t)
        if self.kind != "video": ms = [self._meas(0)]
        else:
            i = int(min(max(t * self.c.fps, 0), self.c.n - 1)); ms = [self._meas(j) for j in range(max(0, i - self.smooth), min(self.c.n, i + self.smooth + 1))]
        ms = [m for m in ms if m]
        if not ms: return img
        cx, cy, h = np.mean(ms, 0); tx, ty, th = self.target; s = th / max(h, 1)
        M = np.float32([[s, 0, tx - s * cx], [0, s, ty - s * cy]])
        return cv2.warpAffine(img, M, (img.shape[1], img.shape[0]), borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))

def lock_shots(cuts, target, tag="lock", **kw):
    """wrap the clips of every shot tagged `lock` (figure lock across worlds: the cuts read as one continuous figure)."""
    for s in cuts.shots:
        if s.has(tag): s.clip = FigureLock(s.clip, target, **kw)

# ------------------------------------------------------------------ edit glue: cut-list tags
def _dtags(shot):
    out = {}
    for tg in shot.tags:
        p = tg.split(":")
        if p[0] in ("dots", "rv", "burst", "ripple", "sweep", "yaw", "p", "inv", "implode", "resolve", "scan"): out[p[0]] = p[1:]
    return out

def apply_tags(img, cuts, t, PAL):
    """`dots:<renderer>` on a cut-list row turns that shot into dots (after the camera, so the grid is fixed):
      dots:led  dots:ledc (source colour)  dots:half  dots:half45  dots:ascii  dots:dither  dots:scan  dots:cloud
      dots:thermal  dots:grid (end card)  dots:paper (ink halftone on paper, 45 deg: Halftone Editorial)
    modifiers: rv:radial:x:y (switch-on from x,y over 1.1 s)  rv:sweep  burst:x:y (light burst + all LEDs on)
      ripple:x:y:t0  sweep (LED refresh band)  inv  resolve (dither noise -> clean)  yaw:a:b  implode  scan  p:<pitch>
    PAL: {"BG","MID","INK","HOT", "TONES"} from tl.py."""
    i = cuts.index(t)
    if i is None: return img
    s = cuts.shots[i]; g = _dtags(s)
    if "dots" not in g: return img
    kind = g["dots"][0]; lt = t - s.start; u = lt / max(1e-6, s.dur); f = fk.frame_of(t)
    ramp = (PAL["BG"], PAL["MID"], PAL["INK"], PAL["HOT"]); p = int(g["p"][0]) if "p" in g else 12
    reveal = field = None
    if "rv" in g:
        mode = g["rv"][0] if g["rv"] else "radial"; a = [float(x) for x in g["rv"][1:]]
        reveal = reveal_sweep(win(lt, 0, 1.1, "out")) if mode == "sweep" else reveal_radial(0.22 + 0.78 * win(lt, 0, 1.1, "expo"), *(a or [0.5, 0.35]))
    if "burst" in g:
        a = [float(x) for x in g["burst"]] or [0.5, 0.4]; bf = burst(a[0], a[1], amp=0.15 + 1.5 * win(lt, 0, 0.45, "expo"), spin=lt * 0.5)
        on = 0.95 * win(lt, 0.33, 0.22, "in"); field = lambda nx, ny: bf(nx, ny) + on
    if "ripple" in g:
        a = [float(x) for x in g["ripple"]] + [0.5, 0.55, 1.05][len(g["ripple"]):]
        field = ripple(a[0], a[1], t=max(0.0, lt - a[2])) if lt > a[2] else None
    if "sweep" in g: field = sweep(-0.1 + (lt / 1.5) % 1.2)
    if kind in ("led", "ledc"):
        out = led(img, p, ramp, reveal=reveal, field=field, invert="inv" in g, color=kind == "ledc", unlit=0.04 if "inv" in g else 0.07, gamma=0.8)
        return bloom(out, 0.75, 22)
    if kind in ("half", "half45"):
        return halftone(img, p, PAL["INK"], PAL["BG"], angle=45 if kind == "half45" else 0, reveal=reveal, field=field)
    if kind == "paper": return halftone(255 - img, 11, PAL.get("PAPER_INK", "#141414"), PAL.get("PAPER", "#EFEBE2"), angle=45, size=1.25)
    if kind == "ascii": return bloom(ascii(img, 20, PAL.get("ASCII", PAL["HOT"]), PAL["BG"], t, reveal=reveal), 0.5, 16)
    if kind == "dither":
        tones = PAL.get("TONES", (PAL["BG"], PAL["INK"], PAL["HOT"]))
        return dither(img, 4, tones, noise=1 - win(lt, 0.05, 0.6, "out") if "resolve" in g else 0.0, t=t)
    if kind == "scan": return bloom(scanlines(img, ink=PAL["INK"], bg=PAL["BG"], t=t), 0.9, 18)
    if kind == "cloud":
        a = [float(x) for x in g.get("yaw", [])] or [-0.7, 0.6]; yaw = a[0] + (a[1] - a[0]) * win(lt, 0, s.dur, "inout")
        imp = win(lt, s.dur - 0.35, 0.35, "in") if "implode" in g else 0.0
        out = point_cloud(img, yaw, ink=PAL["INK"], hot=PAL["HOT"], bg=PAL["BG"], scan_y=-0.95 + ((lt * 0.62) % 1) * 1.9,
                          reveal=win(lt, 0, 0.8, "out"), implode=imp, base=0.3 + imp)
        return bloom(out, 0.6 + imp, 20)
    if kind == "thermal": return thermal_reveal(img, lt)
    if kind == "grid": return dot_grid(img.shape, 30, 1.7, 0.10 + 0.08 * win(lt, 0, 1.0), PAL["INK"], PAL["BG"], sweep_pos=-0.1 + (lt * 0.6) % 1.2 if lt > 0.6 else None)   # loops every 2 s: the card never stops
    return img

# ------------------------------------------------------------------ transitions (layer mode on any style)
def halftone_wipe(a, b, u, p=14, ink="#FFB45A", bg="#070403"):
    """A breaks into halftone dots that swell and merge, then B condenses out of shrinking dots."""
    if u < 0.5: k = u / 0.5; return halftone(a, p, ink, bg, size=1.12 + 1.6 * k, min_r=0.6)
    k = (u - 0.5) / 0.5; h = halftone(b, p, ink, bg, size=2.72 - 1.6 * k, min_r=0.6)
    return cv2.addWeighted(h, 1 - k ** 2, b, k ** 2, 0)

def dither_cut(a, b, u, p=4):
    """A -> B through the Bayer threshold (a print-style dissolve)."""
    H, W = a.shape[:2]; key = ("bayer", W, H, p)
    if key not in _cache:
        th = (np.tile(B8, (H // (8 * p) + 2, W // (8 * p) + 2)) + 0.5) / 64
        _cache[key] = cv2.resize(th, (th.shape[1] * p, th.shape[0] * p), interpolation=cv2.INTER_NEAREST)[:H, :W, None]
    return np.where(_cache[key] < u, b, a)

class Transitions:
    """rows (cut_time, kind, frames): kind halftone | dither. `cuts` = the CutList or a callable src(t) (cuts + dots tags).
    The outgoing shot is held on its last frame; mark the
    incoming row `hard` so the zoom-blur grammar does not fight the wipe."""
    def __init__(self, cuts, rows, PAL=None):
        self.src = cuts.render if hasattr(cuts, "render") else cuts; self.rows, self.hold, self.PAL = sorted(rows), {}, PAL or {}
    def apply(self, img, t):
        f = fk.frame_of(t)
        for (tc, kind, n) in self.rows:
            k = f - fk.frame_of(tc)
            if 0 <= k < n:
                if tc not in self.hold: self.hold[tc] = self.src(tc - 1.0 / fk.FPS)
                u = (k + 1) / (n + 1)
                if kind == "halftone": return halftone_wipe(self.hold[tc], img, u, ink=self.PAL.get("INK", "#FFB45A"), bg=self.PAL.get("BG", "#070403"))
                if kind == "dither": return dither_cut(self.hold[tc], img, u)
        return img
