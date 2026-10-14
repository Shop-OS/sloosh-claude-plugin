#!/usr/bin/env python3
"""Procedural studio-style placeholder images, clearly tagged MOCK.

usage: python3 mocks.py <out_dir> <spec.json>

spec.json: [{"name": "mock_fashion", "title": "Fashion Campaign",
             "palette": ["#F0B8A8", "#E0937F", "#C8735F", "#9A5444"],
             "object": "capsule|bottle|box|sphere|ring|trio|flatlay|exploded|grid",
             "object_colors": ["#F6EFE6", "#B5A493"], "w": 1200, "h": 900}]
palette = wall top, wall bottom, floor near, floor far. Users replace files 1:1 later.
"""
import json
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONTS = [
    "/System/Library/Fonts/SFNSMono.ttf",
    "/System/Library/Fonts/Supplemental/Courier New.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "C:/Windows/Fonts/consola.ttf",
]
FONT = next((f for f in FONTS if os.path.exists(f)), None)


def font(size):
    # Pillow's built-in font keeps mocks working where no listed font exists.
    return ImageFont.truetype(FONT, size) if FONT else ImageFont.load_default(size=size)


def rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)


def studio(w, h, pal, horizon=0.64, light=(0.5, 0.35), seed=0):
    y = np.linspace(0, 1, h)[:, None]
    x = np.linspace(0, 1, w)[None, :]
    wt, wb, fa, fb = map(rgb, pal)
    t = np.clip(y / horizon, 0, 1)
    wall = wt[None, None] * (1 - t[..., None]) + wb[None, None] * t[..., None]
    ft = np.clip((y - horizon) / (1 - horizon), 0, 1)
    floor = fa[None, None] * (1 - ft[..., None]) + fb[None, None] * ft[..., None]
    img = np.where((y < horizon)[..., None], wall, floor) * np.ones((h, w, 1))
    d = np.sqrt(((x - light[0]) * 1.2) ** 2 + (y - light[1]) ** 2)
    img = img * (0.72 + 0.42 * np.exp(-(d ** 2) / 0.18))[..., None]
    img += np.random.default_rng(seed).normal(0, 3.2, img.shape)
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB")


def shadow(img, cx, cy, rx, ry, s=0.55):
    w, h = img.size
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=int(255 * s))
    m = m.filter(ImageFilter.GaussianBlur(max(rx, ry) * 0.35))
    return Image.composite(Image.new("RGB", (w, h), (8, 8, 10)), img, m)


def shaded(img, box, c1, c2, radius=24):
    x0, y0, x1, y1 = [int(v) for v in box]
    w, h = x1 - x0, y1 - y0
    a, b = rgb(c1), rgb(c2)
    t = np.linspace(0, 1, w)
    sh = np.clip(0.55 + 0.6 * np.exp(-((t - 0.32) ** 2) / 0.02) + 0.25 * t, 0, 1.35)
    col = (a[None] * (1 - t[:, None]) + b[None] * t[:, None]) * sh[:, None]
    tile = Image.fromarray(np.clip(np.repeat(col[None], h, axis=0), 0, 255).astype(np.uint8), "RGB")
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=255)
    img.paste(tile, (x0, y0), mask)


def sphere(img, cx, cy, r, c1, c2):
    n = int(r * 2)
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    dx, dy = (xx - r) / r, (yy - r) / r
    dd = dx ** 2 + dy ** 2
    nz = np.sqrt(np.clip(1 - dd, 0, 1))
    light = np.clip(-0.45 * dx - 0.55 * dy + 0.7 * nz, 0, 1)
    col = rgb(c2)[None, None] * (1 - light[..., None]) + rgb(c1)[None, None] * light[..., None]
    col += (np.clip(light, 0.92, 1) - 0.92)[..., None] * 900
    tile = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8), "RGB")
    mask = Image.fromarray(((dd <= 1) * 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(1.2))
    img.paste(tile, (int(cx - r), int(cy - r)), mask)


def label(img, title):
    w, h = img.size
    d = ImageDraw.Draw(img, "RGBA")
    s = max(14, int(w * 0.018))
    f = font(s)
    tw = d.textlength("MOCK", font=f)
    pad = s * 0.55
    d.rounded_rectangle([s, s, s + tw + pad * 2, s + s + pad * 1.4], radius=s * 0.5, fill=(10, 10, 10, 170))
    d.text((s + pad, s + pad * 0.62), "MOCK", font=f, fill=(254, 204, 21, 255))
    d.text((s, h - s * 2.2), f"{title}  ·  replace", font=font(int(s * 0.9)), fill=(255, 255, 255, 150))


def render(spec, i):
    W, H = spec.get("w", 1200), spec.get("h", 900)
    img = studio(W, H, spec["palette"], seed=i)
    oc = spec.get("object_colors", ["#FFFFFF", "#9B9B9B"])
    cx, base = W * 0.5, H * 0.72
    u = H / 900
    o = spec.get("object", "bottle")
    if o == "sphere":
        img = shadow(img, cx, base + 10 * u, 190 * u, 34 * u); sphere(img, cx, base - 170 * u, 180 * u, *oc)
    elif o == "box":
        img = shadow(img, cx, base + 6 * u, 230 * u, 30 * u); shaded(img, (cx - 190 * u, base - 330 * u, cx + 190 * u, base), oc[0], oc[1], 10)
    elif o == "bottle":
        img = shadow(img, cx, base + 6 * u, 130 * u, 24 * u); shaded(img, (cx - 95 * u, base - 380 * u, cx + 95 * u, base), oc[0], oc[1], int(40 * u))
        shaded(img, (cx - 38 * u, base - 470 * u, cx + 38 * u, base - 370 * u), oc[1], oc[1], int(14 * u))
    elif o == "capsule":
        img = shadow(img, cx, base + 6 * u, 170 * u, 26 * u); shaded(img, (cx - 120 * u, base - 560 * u, cx + 120 * u, base), oc[0], oc[1], int(120 * u))
    elif o == "ring":
        img = shadow(img, cx, base + 6 * u, 150 * u, 22 * u, 0.6); sphere(img, cx, base - 150 * u, 150 * u, *oc); sphere(img, cx, base - 150 * u, 92 * u, "#1a160f", "#0a0806")
    elif o == "trio":
        for k, dx in enumerate((-230, 0, 230)):
            img = shadow(img, cx + dx * u, base + 6 * u, 110 * u, 20 * u, 0.7)
            shaded(img, (cx + (dx - 80) * u, base - (470 - k * 30) * u, cx + (dx + 80) * u, base), oc[0], oc[1], int(80 * u))
    elif o == "exploded":
        for k in range(4):
            yy = base - (120 + k * 110) * u
            shaded(img, (cx + (-150 + k * 22) * u, yy - 70 * u, cx + (150 + k * 22) * u, yy), oc[0], oc[1], 12)
    elif o == "flatlay":
        for (bx, by, bw, bh, c) in [(0.22, 0.19, 0.25, 0.42, oc[0]), (0.52, 0.17, 0.27, 0.27, oc[1]), (0.53, 0.48, 0.22, 0.33, "#2E2E2E"), (0.25, 0.66, 0.2, 0.19, "#B0573B")]:
            shaded(img, (bx * W, by * H, (bx + bw) * W, (by + bh) * H), c, c, 18)
    label(img, spec.get("title", spec["name"]))
    return img


def main():
    out, spec_path = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    for i, spec in enumerate(json.load(open(spec_path))):
        p = os.path.join(out, f"{spec['name']}.jpg")
        render(spec, i).save(p, quality=92)
        print(p)


if __name__ == "__main__":
    main()
