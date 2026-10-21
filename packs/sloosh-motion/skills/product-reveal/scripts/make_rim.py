#!/usr/bin/env python3
"""make_rim.py: build the hook "rim-light only" plate from the lit hero plate, pixel-aligned (no extra generation).

Usage:  python3 <skill>/scripts/make_rim.py plates/lit.png plates/lit_cut.png plates/rim.png [--width 7] [--ghost 0.04] [--tint F2E6D0]
  lit.png      the approved full-frame hero plate (product on black, key-lit)
  lit_cut.png  the same frame with only the product opaque (python3 <skill>/scripts/cutout.py plates/lit.png plates/lit_cut.png --keep)
  rim.png      output: black frame where only the product's outer edge glows (strongest on the left and right sides, like
               two back rims), plus a faint ghost of the lit product so the shape reads at 360 px.
Because rim.png is derived from lit.png, RV.lightUp() (or a filmkit cross-fade) can blend them with zero misalignment.
Credit-light hook: a rim-lit still made from the hero still, with no extra generation.
Needs Pillow + numpy.
"""
import sys
import numpy as np
from PIL import Image, ImageFilter, ImageChops

def arg(k, d): return type(d)(sys.argv[sys.argv.index(k) + 1]) if k in sys.argv else d

def main():
    if len(sys.argv) < 4 or sys.argv[1].startswith("--"):
        sys.exit(__doc__)
    lit_p, cut_p, out_p = sys.argv[1:4]
    w = arg("--width", 7); ghost = arg("--ghost", 0.04); tint = arg("--tint", "F2E6D0").lstrip("#")
    lit = Image.open(lit_p).convert("RGB"); a = Image.open(cut_p).convert("RGBA").split()[3]
    if a.size != lit.size: a = a.resize(lit.size, Image.LANCZOS)
    edge = ImageChops.subtract(a, a.filter(ImageFilter.MinFilter(2 * (w // 2) + 1)))         # inner edge band
    W, H = lit.size; bb = a.getbbox() or (0, 0, W, H)
    x = np.linspace(0, 1, W); cx0, cx1 = bb[0] / W, bb[2] / W
    side = np.clip(1 - (np.minimum(np.abs(x - cx0), np.abs(x - cx1)) / max(1e-3, (cx1 - cx0) * 0.35)), 0.18, 1)  # rims hug the sides
    e = np.array(edge, np.float32) / 255 * side[None, :]
    e = np.array(Image.fromarray((e * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2)), np.float32) / 255
    if len(tint) != 6: sys.exit("make_rim.py: --tint must be a 6-digit hex colour, for example F2E6D0")
    col = np.array([int(tint[i:i + 2], 16) for i in (0, 2, 4)], np.float32)
    L = np.array(lit, np.float32); A = np.array(a, np.float32)[..., None] / 255
    out = L * A * ghost + col[None, None, :] * e[..., None] * 0.9
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(out_p)
    print("rim ->", out_p)

if __name__ == "__main__":
    main()
