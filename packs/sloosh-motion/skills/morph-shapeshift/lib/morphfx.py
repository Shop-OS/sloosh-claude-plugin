"""morphfx.py: morph-shapeshift additions to the core compositor (filmkit). Copy into the film's lib/.

Virtual sources you can put in the cut list like any clip (register first, then use the name as the row's source):
  mx.flow("flow_k6_k0", "plates/k6.jpg", "plates/k0.jpg", dur=0.5)     CODE MORPH: optical-flow warp + blend between two
        keyframes (both must share pose/camera; the composition-master rule makes that true). No generation needed.
  mx.shatter("sh_k2_k3", "plates/k2.jpg", "plates/k3.jpg", dur=0.5)     SLICED SHATTER: A splits into slices that fly
        apart (alternating directions, centre-out stagger, motion blur, a hot edge) revealing B settling from 1.08x.
Each name behaves as a 'video' source of length dur (in_point 0, speed 1). Pure: same t -> same frame.

Figure lock (the figure sits at the same spot and size in every world):
  python3 lib/morphfx.py lock plates/k1.jpg plates/k2.jpg ... --ref plates/k0.jpg      -> plates/locked/*.jpg + out/lock_check.jpg
  python3 lib/morphfx.py lock clips/t3.mp4 --ref plates/k0.jpg                          -> clips/locked/t3.mp4 (per frame, smoothed)
  Measures the figure (largest region that differs from the backdrop): the centroid and sqrt(area) of its upper body
  (or bbox centre + height when the figure is fully in frame, for a falling figure), then scales and moves it onto the reference. LOOK at
  out/lock_check.jpg (cyan = measured box, before | after). Wrong measurement? put boxes in lock.json:
  {"plates/k5.jpg": [cx, cy, size]} (pixels at film size) and re-run. A locked clip lands in clips/locked/tN.mp4;
  edit.py uses it in place of clips/tN.mp4 when it exists. The --ref may be a still or a clip (its first frame).
"""
import json, math, os, sys
import numpy as np, cv2
import filmkit as fk

# ------------------------------------------------------------------ virtual sources
class _Virtual:
    kind = "video"; fps = 60.0
    def __init__(self, dur): self.duration = dur; self.n = int(dur * 60)

def register(name, src):
    for fit in ("cover", "vert_full", "vert_blurbg"): fk.Clip._all[(name, fit)] = src
    return name

def _img(path):
    return fk.Clip.get(path).frame(0.0) if not isinstance(path, tuple) else fk.Clip.get(path[0]).frame(path[1])

class FlowMorph(_Virtual):
    def __init__(self, a, b, dur=0.5, scale=4):
        super().__init__(dur); self.a, self.b, self.sc, self.F = a, b, scale, None
    def _flows(self):
        if self.F is None:
            A, B = _img(self.a), _img(self.b); s = self.sc
            g = lambda x: cv2.cvtColor(cv2.resize(x, (fk.W // s, fk.H // s), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
            ga, gb = g(A), g(B); prm = dict(pyr_scale=0.5, levels=5, winsize=31, iterations=5, poly_n=7, poly_sigma=1.5, flags=0)
            fab = cv2.calcOpticalFlowFarneback(ga, gb, None, **prm); fba = cv2.calcOpticalFlowFarneback(gb, ga, None, **prm)
            up = lambda f: cv2.resize(f, (fk.W, fk.H)) * s
            yy, xx = np.mgrid[0:fk.H, 0:fk.W].astype(np.float32); self.F = (A, B, up(fab), up(fba), xx, yy)
        return self.F
    def frame(self, t):
        A, B, fab, fba, xx, yy = self._flows(); u = fk.clamp01(t / self.duration); u = u * u * (3 - 2 * u)
        wa = cv2.remap(A, xx - u * fab[..., 0], yy - u * fab[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        wb = cv2.remap(B, xx - (1 - u) * fba[..., 0], yy - (1 - u) * fba[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        w = fk.clamp01((u - 0.2) / 0.6)
        return cv2.addWeighted(wa, 1 - w, wb, w, 0)

class Shatter(_Virtual):
    def __init__(self, a, b, dur=0.5, n=11, seed=3, vertical=True):
        super().__init__(dur); self.a, self.b, self.nn, self.seed, self.vertical = a, b, n, seed, vertical
    def frame(self, t):
        A, B = _img(self.a), _img(self.b); u = fk.clamp01(t / self.duration)
        out = fk.camera(B, fk.lerp(1.08, 1.0, fk.ease_out(u, 3)))            # B settles in behind
        L = fk.W if self.vertical else fk.H; n = self.nn; edges = np.linspace(0, L, n + 1).astype(int)
        r = np.random.default_rng(self.seed)
        for k in range(n):
            delay = 0.35 * abs(k - (n - 1) / 2) / ((n - 1) / 2) + 0.05 * r.random()   # centre-out
            v = fk.clamp01((u - delay) / max(1e-3, 0.62 - delay * 0.4)); v = v ** 2.2
            if v >= 1: continue
            a0, a1 = edges[k], edges[k + 1]; sl = A[:, a0:a1] if self.vertical else A[a0:a1]
            off = int(v * (fk.H if self.vertical else fk.W) * 1.15) * (1 if k % 2 else -1)
            blur = int(1 + v * 90) | 1
            sl = cv2.blur(sl, (1, blur) if self.vertical else (blur, 1))
            if self.vertical:
                y0, y1 = max(0, off), min(fk.H, fk.H + off)
                if y1 > y0: out[y0:y1, a0:a1] = sl[y0 - off:y1 - off]; out[max(0, y0):y0 + 3, a0:a1] = 255
            else:
                x0, x1 = max(0, off), min(fk.W, fk.W + off)
                if x1 > x0: out[a0:a1, x0:x1] = sl[:, x0 - off:x1 - off]
        if u < 0.35: out = fk.rgb_split(out, 16 * fk.W / 1080 * (1 - u / 0.35))
        return out

def flow(name, a, b, dur=0.5): return register(name, FlowMorph(a, b, dur))
def shatter(name, a, b, dur=0.5, **k): return register(name, Shatter(a, b, dur, **k))

# ------------------------------------------------------------------ figure lock
def measure(img):
    """(cx, top, size, mode): the figure = largest region that differs from the backdrop's border colour."""
    h, w = img.shape[:2]; s = 360 / max(h, w); sm = cv2.resize(img, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)
    lab = cv2.cvtColor(cv2.GaussianBlur(sm, (0, 0), 2), cv2.COLOR_BGR2LAB).astype(np.float32)
    hh, ww = lab.shape[:2]; yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32) / max(hh, ww)
    edge = np.zeros((hh, ww), bool); edge[:4] = True; edge[:, :4] = True; edge[:, -4:] = True   # top + sides (the figure may touch the bottom)
    A = np.stack([np.ones_like(xx), xx, yy], -1)                                       # backdrop = a plane per LAB channel, fitted on
    coef = np.linalg.lstsq(A[edge], lab[edge], rcond=None)[0]                          # the border, so a lit or graded backdrop stays out
    d = np.clip(np.linalg.norm(lab - A @ coef, axis=2), 0, 255).astype(np.uint8)
    t, _ = cv2.threshold(d, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU); hi = (d > t).astype(np.uint8)
    nc, cc, cst, _ = cv2.connectedComponentsWithStats(((d > min(t, 18)) & (hi == 0)).astype(np.uint8))   # a low floor adds dark skin,
    keep = np.unique(cc[cv2.dilate(hi, np.ones((3, 3), np.uint8)) > 0])                 # hair and garments that touch the Otsu figure,
    keep = [j for j in keep if j > 0 and cst[j, cv2.CC_STAT_WIDTH] < ww - 2]           # but not a full-width floor or wall
    m = ((hi > 0) | np.isin(cc, keep)).astype(np.uint8) * 255
    k = max(3, int(0.05 * sm.shape[1])); m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))
    n, lab_, st, _ = cv2.connectedComponentsWithStats(m)
    if n < 2: return (w / 2, h * 0.2, w * 0.5, "w")
    i = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA])); x, y, bw, bh = st[i, :4]
    cs, _ = cv2.findContours((lab_ == i).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    blob = np.zeros(m.shape, np.uint8); cv2.drawContours(blob, cs, -1, 1, -1); blob = blob > 0       # filled outline: a wireframe or dark key counts its whole body
    if y + bh < sm.shape[0] - 2: return ((x + bw / 2) / s, y / s, bh / s, "h")           # fully in frame: centre + height
    up = blob[: int(0.6 * sm.shape[0])]; ys, xs = np.nonzero(up)                      # cropped by the frame: upper-body
    if len(xs) < 10: return ((x + bw / 2) / s, y / s, bw / s, "w")                     # centroid + sqrt(area) (robust to
    return (xs.mean() / s, ys.mean() / s, math.sqrt(len(xs)) / s, "w")                # dark hair on a dark backdrop)

def lock_matrix(src, ref):
    s = ref[2] / max(src[2], 1e-3); M = np.float32([[s, 0, ref[0] - s * src[0]], [0, s, ref[1] - s * src[1]]]); return M

def _sheet(pairs, out):
    tiles = []
    for im, m in pairs:
        if im is None: continue
        t = im.copy(); cx, cy, size, mode = m; c = (255, 255, 0)
        cv2.drawMarker(t, (int(cx), int(cy)), c, cv2.MARKER_CROSS, 60, 6)
        if mode == "w": cv2.rectangle(t, (int(cx - size / 2), int(cy - size / 2)), (int(cx + size / 2), int(cy + size / 2)), c, 4)
        else: cv2.line(t, (int(cx), int(cy)), (int(cx), int(cy + size)), c, 6)
        tiles.append(cv2.resize(t, (240, int(240 * t.shape[0] / t.shape[1]))))
    cv2.imwrite(out, np.hstack(tiles)); print("check ->", out)

def lock_cli(files, ref, outdir=None):
    over = json.load(open("lock.json")) if os.path.exists("lock.json") else {}
    def meas(path, img): return tuple(over[path]) + ("w",) if path in over else measure(img)
    R = fk.Clip.get(ref).frame(0) if not ref.lower().endswith(".mp4") else _first_frame(ref)
    rm = meas(ref, R); pairs = []
    for f in files:
        od = outdir or os.path.join(os.path.dirname(f), "locked"); os.makedirs(od, exist_ok=True); dst = os.path.join(od, os.path.basename(f))
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            im = fk.Clip.get(f).frame(0); m = meas(f, im)
            if m[3] != rm[3]: m = measure_as(im, rm[3])
            M = lock_matrix(m, rm); outim = cv2.warpAffine(im, M, (fk.W, fk.H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))   # black, never smeared edges
            cv2.imwrite(dst, outim, [cv2.IMWRITE_JPEG_QUALITY, 94])
            chk = cv2.warpAffine(im, M, (fk.W, fk.H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)   # re-measure without the black
            pairs += [(im, m), (outim, measure(chk))]                                    # margin, which would join the figure
            print(f"lock {f}: dx {M[0, 2]:.0f} dy {M[1, 2]:.0f} scale {M[0, 0]:.3f} -> {dst}")
        else:                                                                # video: per-frame, smoothed over 7 frames
            cap = cv2.VideoCapture(f); fps = cap.get(cv2.CAP_PROP_FPS) or 30; frames = []
            while True:
                ok, fr = cap.read()
                if not ok: break
                frames.append(fk.cover(fr, fk.W, fk.H))
            if not frames: print(f"lock {f}: no frames could be read, skipped"); continue
            ms = np.array([measure(fr)[:3] for fr in frames]); k = 7; pad = np.pad(ms, ((k // 2, k // 2), (0, 0)), mode="edge")
            ms = np.array([pad[i:i + k].mean(0) for i in range(len(ms))])
            vw = cv2.VideoWriter(dst, cv2.VideoWriter_fourcc(*"mp4v"), fps, (fk.W, fk.H))
            for fr, m in zip(frames, ms): vw.write(cv2.warpAffine(fr, lock_matrix(tuple(m), rm), (fk.W, fk.H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0)))
            vw.release(); pairs += [(frames[0], measure(frames[0]))]; print(f"lock {f}: {len(frames)} frames -> {dst}")
    os.makedirs("out", exist_ok=True); _sheet([(R, rm)] + pairs, "out/lock_check.jpg")

def _first_frame(path):
    cap = cv2.VideoCapture(path); ok, fr = cap.read(); cap.release()
    if not ok: sys.exit("cannot read the first frame of " + path)
    return fk.cover(fr, fk.W, fk.H)

def measure_as(im, mode):
    m = measure(im); return m if m[3] == mode else (m[0], m[1], m[2], mode)

if __name__ == "__main__":
    sys.path.insert(0, os.getcwd()); import tl; fk.setup(tl.W, tl.H, tl.FPS)
    a = sys.argv[1:]
    if not a or a[0] != "lock" or "--ref" not in a: sys.exit(__doc__)
    i = a.index("--ref"); ref = a[i + 1]; rest = a[1:i] + a[i + 2:]
    od = None
    if "--out" in rest: j = rest.index("--out"); od = rest[j + 1]; rest = rest[:j] + rest[j + 2:]
    lock_cli(rest, ref, od)
