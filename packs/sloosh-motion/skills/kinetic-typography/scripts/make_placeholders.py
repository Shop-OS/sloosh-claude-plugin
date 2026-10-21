#!/usr/bin/env python3
"""make_placeholders.py: placeholder plate + subject matte so a film with tl.PLATE runs before the real still exists.
  python3 make_placeholders.py <film-folder>
Writes plates/plate.jpg (a dim studio gradient with a figure-like silhouette) and plates/plate_matte.png (its alpha).
Replace both with the approved plate still and its cut-out (scripts/cutout.py) before delivery."""
import os, sys


def main():
    import numpy as np, cv2
    film = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
    sys.path.insert(0, os.path.join(film, "lib")); sys.path.insert(0, film)
    os.chdir(film)
    import tl
    W, H = tl.W, tl.H; os.makedirs("plates", exist_ok=True)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    bg = np.zeros((H, W, 3), np.float32); g = np.clip(1 - np.hypot((xx - W * .5) / W, (yy - H * .35) / H) * 1.6, 0, 1)
    bg[:] = (40, 52, 70); bg += g[..., None] * np.array([90, 110, 140], np.float32)
    m = np.zeros((H, W), np.uint8)
    cx, s = W // 2, min(W, H) / 1080
    cv2.ellipse(m, (cx, int(H * .36)), (int(120 * s), int(150 * s)), 0, 0, 360, 255, -1)                    # head
    cv2.ellipse(m, (cx, int(H * .36 + 420 * s)), (int(300 * s), int(330 * s)), 0, 180, 360, 255, -1)        # shoulders
    cv2.rectangle(m, (cx - int(300 * s), int(H * .36 + 420 * s)), (cx + int(300 * s), H), 255, -1)          # body
    m = cv2.GaussianBlur(m, (0, 0), 2)
    fig = np.zeros_like(bg); fig[:] = (95, 120, 170); fig += (yy[..., None] / H) * np.array([-40, -40, -40], np.float32)
    img = bg * (1 - m[..., None] / 255.0) + fig * (m[..., None] / 255.0)
    img += np.random.default_rng(1).normal(0, 5, img.shape)
    cv2.imwrite("plates/plate.jpg", np.clip(img, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 90])
    cv2.imwrite("plates/plate_matte.png", m); print("placeholders -> plates/plate.jpg plates/plate_matte.png")


if __name__ == "__main__":
    main()
