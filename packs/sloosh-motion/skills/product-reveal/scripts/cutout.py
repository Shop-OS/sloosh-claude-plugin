#!/usr/bin/env python3
"""cutout.py: cut the REAL product out of a photo (or out of the approved hero still) and measure it.

  python3 <skill>/scripts/cutout.py photo.jpg plates/product_cut.png             # GrabCut (default engine)
  python3 <skill>/scripts/cutout.py photo.jpg plates/product_cut.png --box 120,200,960,1700   # seed GrabCut with a box
  python3 <skill>/scripts/cutout.py photo.jpg plates/product_cut.png --matte mask.png         # the user's own mask
  python3 <skill>/scripts/cutout.py my_cutout.png plates/product_cut.png                      # an RGBA cutout: its alpha is used
  python3 <skill>/scripts/cutout.py photo.jpg plates/product_cut.png --rembg                  # opt-in, see below
  python3 <skill>/scripts/cutout.py plates/hero.jpg plates/hero_cut.png --bbox --floor 1330     # also prints tl.PACK

Engines, in this order:
  1. --matte mask.png   the user's own mask (white = product, black = background), same size as the photo.
  2. an RGBA input with real transparency (the user's own cutout): its alpha channel is used as it is.
  3. --rembg            only when the user asked for it. rembg is not installed by this skill. It downloads a
                        segmentation model the first time it runs. Ask the user before installing it, and install it
                        in a virtual environment. If it is missing, this script stops and says so.
  4. GrabCut (default)  OpenCV only, nothing downloaded. Works on clean studio photos (a plain light or dark
                        background). Seeded from the colour difference to the photo's border, or from --box x0,y0,x1,y1.
--bbox prints the product's box in the hero still as a PACK.update(...) line for tl.py, so the code packshot stands
exactly where the generated product stood on the set. Paste it under the PACK defaults in tl.py. The values use the
same units as ui/packshot.html: px of a frame whose short side is 1080 (9:16, 16:9, 1:1 and 4:5).
--floor <y> (the floor line, in the same units, read off the still) cuts away everything below that line, such as a
glossy floor reflection, so the cutout ends at the product's base.
--keep keeps the full frame (no trim): use it for a mask that must stay pixel-aligned with its plate (make_rim.py,
a matte for type behind a still).
Check the result on a contact sheet: hair-thin parts (straps, stems, wires, clip arms) are where cutouts fail. If
GrabCut fails, ask the user for their own cutout or a mask, or offer the plain matte: --box around the product with
--plain, which keeps the box as a soft-edged rectangle (good enough under a dark vignette, never for a light set).
Needs Python 3.9+, numpy and opencv-python.
"""
import sys
import numpy as np
import cv2


def opt(a, k, d=None):
    return a[a.index(k) + 1] if k in a and a.index(k) + 1 < len(a) else d


def rembg_cut(path):
    try:
        from rembg import remove
        from PIL import Image
    except ImportError:
        sys.exit("cutout.py: --rembg needs the rembg package, which is not installed. It downloads a model on first "
                 "use. Ask the user before installing it in a virtual environment, or run without --rembg (GrabCut), "
                 "or use the user's own cutout or mask (--matte).")
    return np.array(remove(Image.open(path).convert("RGB")).convert("RGBA"))[..., [2, 1, 0, 3]]


def largest(a):
    n, lab, st, _ = cv2.connectedComponentsWithStats(a)
    if n > 1:
        a = np.where(lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA]), 255, 0).astype(np.uint8)
    return a


def grabcut(img, box=None):
    h, w = img.shape[:2]
    if box is not None:
        x0, y0 = max(0, min(w - 2, box[0])), max(0, min(h - 2, box[1]))
        x1, y1 = max(x0 + 1, min(w, box[2])), max(y0 + 1, min(h, box[3]))
        mask = np.zeros((h, w), np.uint8)
        bg, fgm = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
        cv2.grabCut(img, mask, (x0, y0, max(1, x1 - x0), max(1, y1 - y0)), bg, fgm, 5, cv2.GC_INIT_WITH_RECT)
    else:
        border = np.concatenate([img[:8].reshape(-1, 3), img[-8:].reshape(-1, 3),
                                 img[:, :8].reshape(-1, 3), img[:, -8:].reshape(-1, 3)])
        d = np.linalg.norm(img.astype(np.float32) - np.median(border, 0), axis=2)
        mask = np.where(d > 28, cv2.GC_PR_FGD, cv2.GC_PR_BGD).astype(np.uint8)
        mask[:8], mask[-8:], mask[:, :8], mask[:, -8:] = cv2.GC_BGD, cv2.GC_BGD, cv2.GC_BGD, cv2.GC_BGD
        if not (mask == cv2.GC_PR_FGD).any():
            sys.exit("cutout.py: GrabCut found nothing that differs from the photo's border. Try --box x0,y0,x1,y1, "
                     "the user's own cutout, or --matte.")
        bg, fgm = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
        try:
            cv2.grabCut(img, mask, None, bg, fgm, 5, cv2.GC_INIT_WITH_MASK)
        except cv2.error as e:
            sys.exit("cutout.py: GrabCut failed ({}). Try --box, the user's own cutout or --matte.".format(str(e).strip()[:120]))
    a = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
    return cv2.GaussianBlur(largest(a), (0, 0), 0.8)


def plain(img, box):
    h, w = img.shape[:2]
    x0, y0, x1, y1 = box
    a = np.zeros((h, w), np.uint8)
    a[max(0, y0):min(h, y1), max(0, x0):min(w, x1)] = 255
    return cv2.GaussianBlur(a, (0, 0), max(2.0, 0.01 * w))


def main():
    a = sys.argv[1:]
    if len(a) < 2 or a[0].startswith("--"):
        sys.exit(__doc__)
    src, out = a[0], a[1]
    raw = cv2.imread(src, cv2.IMREAD_UNCHANGED)
    if raw is None:
        sys.exit("cutout.py: cannot read " + src)
    if raw.ndim == 2:
        raw = cv2.cvtColor(raw, cv2.COLOR_GRAY2BGR)
    box = opt(a, "--box")
    box = tuple(int(float(v)) for v in box.split(",")) if box else None
    if box is not None and len(box) != 4:
        sys.exit("cutout.py: --box needs x0,y0,x1,y1")
    img = raw[..., :3] if raw.shape[2] == 4 else raw
    matte = opt(a, "--matte")
    if matte:
        m = cv2.imread(matte, cv2.IMREAD_GRAYSCALE)
        if m is None:
            sys.exit("cutout.py: cannot read the matte " + matte)
        if m.shape[:2] != img.shape[:2]:
            m = cv2.resize(m, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_LINEAR)
        rgba, eng = np.dstack([img, m]), "the user's matte"
    elif raw.shape[2] == 4 and int(raw[..., 3].min()) < 250:
        rgba, eng = raw.copy(), "the user's cutout (alpha kept)"
    elif "--rembg" in a:
        rgba, eng = rembg_cut(src), "rembg"
    elif "--plain" in a:
        if box is None:
            sys.exit("cutout.py: --plain needs --box x0,y0,x1,y1")
        rgba, eng = np.dstack([img, plain(img, box)]), "plain matte"
    else:
        rgba, eng = np.dstack([img, grabcut(img, box)]), "grabcut"
    hh, ww = rgba.shape[:2]
    s = 1080.0 / min(ww, hh)                                         # px of the still -> PACK units (see --bbox)
    if "--floor" in a:
        try:
            fl = float(opt(a, "--floor"))
        except (TypeError, ValueError):
            sys.exit("cutout.py: --floor needs a number (the floor line y)")
        rgba[max(0, int(fl / s)):, :, 3] = 0
    ys, xs = np.where(rgba[..., 3] > 40)
    if len(xs) == 0:
        sys.exit("cutout.py: nothing was cut out. Try --box, the user's own cutout or --matte.")
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    cv2.imwrite(out, rgba if "--keep" in a else rgba[y0:y1, x0:x1])
    print("{}: cutout -> {}".format(eng, out))
    if "--bbox" in a:
        print("PACK.update(cx={:.0f}, bottom={:.0f}, height={:.0f})".format((x0 + x1) / 2 * s, y1 * s, (y1 - y0) * s))


if __name__ == "__main__":
    main()
