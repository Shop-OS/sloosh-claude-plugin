#!/usr/bin/env python3
"""label_macro.py: the READABLE label macro as a code shot, made from the REAL cutout (never from a generator).

  python3 <skill>/scripts/label_macro.py plates/product_cut.png clips/label_macro.mp4 [--zoom 2.8] [--focus 0.5,0.64]
          [--dur 4] [--sweeps 0.3:1.2,2.2:1.0] [--peak 0.55] [--width 0.10]

Crops the real cutout around the label at --zoom x the packshot size (tl.PACK height; 2-3x reads as a macro), centres
the label (--focus = label centre as x,y fractions of the cutout's box; measure it once on the photo), lays it on the
film's BASE -> LIT glow, and moves a specular band across it, masked to the product alpha (same look as RV.sweep).
The clip is static apart from the sweeps: the push comes from the cut-list row (zoom_from -> zoom_to), so every
letter is the real printed letter in every frame. W, H, FPS, BASE, LIT and PACK are read from tl.json (run tl.py first).
Use the full-resolution cutout: the label must stay sharp at 2-3x. Works for 9:16, 16:9, 1:1 and 4:5.
Needs Python 3.9+, numpy, opencv-python and ffmpeg on the PATH.
"""
import json, os, shutil, subprocess, sys
import numpy as np
import cv2

def arg(a, k, d):
    return a[a.index(k) + 1] if k in a else d

def hex2rgb(h):
    h = h.lstrip("#"); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32)

def main():
    a = sys.argv[1:]
    if len(a) < 2 or a[0].startswith("--"): sys.exit(__doc__)
    src, out = a[0], a[1]
    tl = json.load(open("tl.json")) if os.path.exists("tl.json") else {}
    W, H, FPS = int(tl.get("W", 1080)), int(tl.get("H", 1920)), int(tl.get("FPS", 30))
    base, lit = hex2rgb(tl.get("BASE", "#050505")), hex2rgb(tl.get("LIT", "#2A241D"))
    if shutil.which("ffmpeg") is None: sys.exit("label_macro: ffmpeg is missing. Ask the user to install it.")
    k = min(W, H) / 1080.0                                           # PACK units, as in ui/packshot.html
    pack_h = float(tl.get("PACK", {}).get("height", 0.49 * H)) * (k if "PACK" in tl else 1)
    zoom = float(arg(a, "--zoom", 2.8)); fx, fy = map(float, arg(a, "--focus", "0.5,0.64").split(","))
    dur = float(arg(a, "--dur", 4.0)); peak = float(arg(a, "--peak", 0.55)); bw = float(arg(a, "--width", 0.10))
    sweeps = [tuple(map(float, s.split(":"))) for s in arg(a, "--sweeps", "0.3:1.2,2.2:1.0").split(",")]

    cut = cv2.imread(src, cv2.IMREAD_UNCHANGED)
    if cut is None or cut.ndim != 3 or cut.shape[2] != 4: sys.exit(f"label_macro: {src} must be an RGBA cutout")
    ys, xs = np.where(cut[..., 3] > 8)
    if len(xs) == 0: sys.exit(f"label_macro: {src} is fully transparent. Make the cutout again (cutout.py).")
    cut = cut[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    s = zoom * pack_h / cut.shape[0]                                  # px per cutout px
    M = np.float32([[s, 0, W / 2 - fx * cut.shape[1] * s], [0, s, H / 2 - fy * cut.shape[0] * s]])
    big = cv2.warpAffine(cut, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    rgb = big[..., :3][..., ::-1].astype(np.float32)                 # BGR -> RGB
    al = (big[..., 3:4].astype(np.float32) / 255.0)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    g = np.exp(-(((xx - W / 2) / (0.55 * W)) ** 2 + ((yy - H / 2) / (0.45 * H)) ** 2))[..., None]
    bg = base + (lit - base) * g
    still = rgb * al + bg * (1 - al)
    # a straight band, tilted ~10 deg off vertical (RV.sweep angle 100), crossing left -> right
    d = (xx + 0.18 * (yy - H / 2)) / W                                 # band coordinate, 0..1 across the frame

    def frame(t):
        img = still.copy()
        for t0, ln in sweeps:
            if t0 <= t <= t0 + ln:
                u = 0.5 - 0.5 * np.cos(np.pi * (t - t0) / ln)          # ease in-out
                c = -0.25 + 1.5 * u
                band = (peak * np.exp(-((d - c) / bw) ** 2))[..., None] * al   # masked to the product
                img = 255 - (255 - img) * (1 - band)                     # screen
        return np.clip(img, 0, 255).astype(np.uint8)[..., ::-1]

    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(int(round(dur * FPS))): p.stdin.write(np.ascontiguousarray(frame(i / FPS)).tobytes())
    p.stdin.close()
    if p.wait() != 0: sys.exit("label_macro: ffmpeg failed to write " + out)
    print(f"label macro -> {out}  ({dur:.1f} s, zoom {zoom}x of the packshot, sweeps {sweeps})")

if __name__ == "__main__":
    main()
