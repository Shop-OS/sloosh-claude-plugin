#!/usr/bin/env python3
"""cutout.py: subject matte for "type behind the subject" (the plate's person or product sits IN FRONT of the type).
  python3 cutout.py plates/plate.jpg plates/plate_matte.png [--box x0,y0,x1,y1] [--rembg]
Default: OpenCV GrabCut seeded with --box (fractions of the image, default 0.15,0.08,0.85,1.0: a centred subject).
--rembg uses the rembg module instead, only if it is already installed. It is opt-in: ask the user before anyone
installs it (it also fetches a model on first use). Without it, or if it fails, the script falls back to GrabCut.
Always LOOK at the matte (and a test still) before using it: hair and fingers need a clean edge; feather is 2 px.
The matte must come from the SAME approved still as the plate (same pixels)."""
import sys


def grabcut(img, box):
    import numpy as np, cv2
    h, w = img.shape[:2]
    s = 900 / max(h, w); sm = cv2.resize(img, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)
    mask = np.zeros(sm.shape[:2], np.uint8)
    r = (int(box[0] * sm.shape[1]), int(box[1] * sm.shape[0]), int((box[2] - box[0]) * sm.shape[1]), int((box[3] - box[1]) * sm.shape[0]))
    bgd, fgd = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    cv2.grabCut(sm, mask, r, bgd, fgd, 6, cv2.GC_INIT_WITH_RECT)
    m = np.where((mask == 1) | (mask == 3), 255, 0).astype(np.uint8)
    return cv2.resize(m, (w, h), interpolation=cv2.INTER_LINEAR)


def with_rembg(img):
    import numpy as np, cv2
    try:
        from rembg import remove
    except ImportError:
        print("rembg is not installed. Using GrabCut. Ask the user before installing rembg (use a virtual environment).")
        return None
    try:
        rgba = remove(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        return np.array(rgba)[..., 3]
    except Exception as e:
        print(f"rembg failed ({e}). Using GrabCut.")
        return None


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    import cv2
    src, dst = sys.argv[1], sys.argv[2]
    box = [0.15, 0.08, 0.85, 1.0]
    if "--box" in sys.argv:
        box = [float(v) for v in sys.argv[sys.argv.index("--box") + 1].split(",")]
    img = cv2.imread(src, cv2.IMREAD_COLOR)
    if img is None:
        sys.exit(f"cannot read {src}")
    m, how = None, "grabcut"
    if "--rembg" in sys.argv:
        m = with_rembg(img)
        if m is not None:
            how = "rembg"
    if m is None:
        m = grabcut(img, box)
    m = cv2.GaussianBlur(m, (0, 0), 2)
    cv2.imwrite(dst, m); print(f"matte ({how}) -> {dst}  coverage {m.mean() / 2.55:.0f}%")


if __name__ == "__main__":
    main()
