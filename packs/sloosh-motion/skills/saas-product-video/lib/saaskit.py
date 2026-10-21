"""saaskit.py: the saas-product-video additions to filmkit (both modes), used by edit.py.
Copy it into the film's lib/ (scripts/use_example.sh does). Everything is a pure function of the frame or of t.

  rush(img, u, fx, fy)           rush into a screen: zoom blur growing with u (0..1), fading to white over the last 60%
                                 (pair it with the row's zoom 1.1 -> 1.9, focus on the screen)
  whip_at(img, t, times)         a 3-frame horizontal whip blur (up to 170 px at 1920) centred on each time in `times`
  punch_in(t, t0, amt, tau)      an eased hit-zoom value for Overlay.over(zoom=...) on a page (1 + amt e^(-(t-t0)/tau))
  Reframe(folder, keys, start, speed)  a page rendered at 16:9 (2x) shown in a 9:16, 1:1 or 4:5 film: an aspect-correct crop
                                 that follows the focus keys [(t, fx, fy, zoom)] (film time), so the UI never squashes
                                 (zoom below 1 shrinks the whole page over a blurred copy of itself)
"""
import math
import cv2
import numpy as np
import filmkit as fk

def rush(img, u, fx=0.5, fy=0.5):
    u = fk.clamp01(u)
    img = fk.zblur(img, 0.30 * u * u, fx, fy)
    w = fk.ease_in_out((u - 0.4) / 0.6) if u > 0.4 else 0.0
    return fk.whiteout(img, w / 0.9) if w > 0 else img

def whip_at(img, t, times, frames=3, px=170):
    for T in times:
        k = 1.0 - abs(t - T) * fk.FPS / frames
        if k > 0: img = fk.whip(img, px * fk.W / 1920 * k)
    return img

def punch_in(t, t0, amt=0.06, tau=0.15):
    return 1.0 + amt * math.exp(-(t - t0) / tau) if t >= t0 else 1.0

def _ramp(n, lo, hi, e):
    k = np.arange(n, dtype=np.float32); r = np.ones(n, np.float32)
    if lo: r = np.minimum(r, (k + 1) / e)
    if hi: r = np.minimum(r, (n - k) / e)
    return r

class Reframe(fk.Overlay):
    """A 16:9 page (rendered at 1920x1080, ideally --scale 2) inside a film of another aspect. keys: [(t, fx, fy, zoom)]
    in film time; fx/fy are the focus as a fraction of the page; zoom 1 shows the page's full height. Below 1 the whole
    page shrinks into the frame over a blurred copy of itself (a feathered seam), so a wide moment (a lockup) stays whole."""
    def __init__(self, folder, keys, start=0.0, speed=1.0):
        super().__init__(folder, start, speed); self.keys = sorted(keys)

    def focus(self, t):
        k = self.keys
        if t <= k[0][0]: return k[0][1:]
        for a, b in zip(k, k[1:]):
            if t <= b[0]:
                u = fk.ease_in_out((t - a[0]) / max(1e-6, b[0] - a[0])); return tuple(fk.lerp(x, y, u) for x, y in zip(a[1:], b[1:]))
        return k[-1][1:]

    def over(self, img, t, opacity=1.0, zoom=1.0, **_):
        o = self.rgba(t)
        if o is None: return img
        fx, fy, z = self.focus(t); z *= zoom; oh, ow = o.shape[:2]                  # zoom: the drop punch on top of the key
        ch = oh / max(z, 1e-3); cw = ch * fk.W / fk.H                               # the crop in page px (bigger than the page below zoom 1)
        def org(f, c, n): return min(max(f * n - c / 2, 0), n - c) if c <= n else (n - c) / 2
        x0, y0 = org(fx, cw, ow), org(fy, ch, oh)
        if cw <= ow and ch <= oh:
            o = cv2.resize(o[int(y0):int(y0 + ch), int(x0):int(x0 + cw)], (fk.W, fk.H), interpolation=cv2.INTER_AREA)
        else:                                                                       # zoom < 1: page over its own blurred cover
            cv_w = min(ow, oh * fk.W / fk.H); cx = int(min(max(fx * ow - cv_w / 2, 0), ow - cv_w))
            fill = cv2.resize(o[:, cx:cx + int(cv_w)], (max(1, fk.W // 16), max(1, fk.H // 16)), interpolation=cv2.INTER_AREA)
            out = cv2.resize(cv2.GaussianBlur(fill, (0, 0), 5), (fk.W, fk.H), interpolation=cv2.INTER_LINEAR).astype(np.float32)
            s = fk.H / ch; pw, ph = max(1, round(ow * s)), max(1, round(oh * s)); px, py = int(round(-x0 * s)), int(round(-y0 * s))
            pg = cv2.resize(o, (pw, ph), interpolation=cv2.INTER_AREA).astype(np.float32); e = max(2.0, 0.03 * min(pw, ph))
            pg[..., 3] *= np.outer(_ramp(ph, py > 0, py + ph < fk.H, e), _ramp(pw, px > 0, px + pw < fk.W, e))
            X0, Y0, X1, Y1 = max(0, px), max(0, py), min(fk.W, px + pw), min(fk.H, py + ph)
            if X1 > X0 and Y1 > Y0:
                p = pg[Y0 - py:Y1 - py, X0 - px:X1 - px]; a = p[..., 3:4] / 255.0; r = out[Y0:Y1, X0:X1]
                r[..., :3] = r[..., :3] * (1 - a) + p[..., :3] * a; r[..., 3:4] = r[..., 3:4] * (1 - a) + 255.0 * a
            o = out.astype(np.uint8)
        a = (o[..., 3:4].astype(np.float32) / 255.0) * opacity
        return (img * (1 - a) + o[..., :3] * a).astype(np.uint8)
