#!/usr/bin/env python3
"""Paint out baked-in text (or any small region) using the clean band next to it.

usage: python3 cleanplate.py <in> <out.jpg> --box x0,y0,x1,y1 [--logical-width W] [--from above|below]

--box is in logical pixels; if the input is an HD (2x) file pass --logical-width with the
original width so the box scales. The band of the same height directly above (or below)
the box is feathered over it, then lightly softened. Works well on plain walls and skies.
"""
import argparse
import numpy as np
from PIL import Image, ImageFilter


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp")
    ap.add_argument("out")
    ap.add_argument("--box", required=True)
    ap.add_argument("--logical-width", type=float, default=0)
    ap.add_argument("--from", dest="src", default="above", choices=["above", "below"])
    o = ap.parse_args()
    im = Image.open(o.inp).convert("RGB")
    W, H = im.size
    k = W / o.logical_width if o.logical_width else 1.0
    x0, y0, x1, y1 = [float(v) * k for v in o.box.split(",")]
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    h = y1 - y0
    gap = int(6 * k)
    arr = np.asarray(im).astype(np.float32)
    if o.src == "above":
        band = arr[max(0, y0 - h - gap): y0 - gap, x0:x1]
    else:
        band = arr[y1 + gap: min(H, y1 + gap + h), x0:x1]
    band = band[:h]
    if band.shape[0] < h:
        raise SystemExit("not enough clean area next to the box")
    mask = np.ones((h, x1 - x0), np.float32)
    fe = max(2, int(14 * k))
    ramp = np.linspace(0, 1, fe)
    mask[:fe] *= ramp[:, None]
    mask[-fe:] *= ramp[::-1][:, None]
    mask[:, :fe] *= ramp[None, :]
    mask[:, -fe:] *= ramp[::-1][None, :]
    region = arr[y0:y1, x0:x1]
    arr[y0:y1, x0:x1] = region * (1 - mask[..., None]) + band * mask[..., None]
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    blur = out.filter(ImageFilter.GaussianBlur(1.2 * k))
    m = Image.new("L", (W, H), 0)
    m.paste(255, (x0, y0, x1, y1))
    m = m.filter(ImageFilter.GaussianBlur(6 * k))
    out = Image.composite(blur, out, m.point(lambda v: int(v * 0.35)))
    out.save(o.out, quality=93)
    print(o.out)


if __name__ == "__main__":
    main()
