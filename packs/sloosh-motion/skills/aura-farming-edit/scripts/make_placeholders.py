#!/usr/bin/env python3
"""make_placeholders.py: stand-in keyframes and clips so the example edit runs before the real Sloosh shots land.

  python3 <this skill>/scripts/make_placeholders.py [film_dir] [--n 14] [--w 540 --h 960]

Writes plates/k01..kNN.jpg (keyframe stills), plates/sheet.jpg (identity sheet) and clips/c01..cNN.mp4 (5 s, 24 fps):
a dark graded world with moving streaks, a lit head (two eyes) and a body, each shot in its own hue, with its
role label burned in so the contact sheet shows which row of the cut list is on screen. Replace them with the
approved stills and generated clips under the same names (clips can be any size; filmkit cover-fits them).
"""
import os, sys, math
import numpy as np
import cv2

ROLES = ["EYES", "GARAGE", "HELMET", "HANDS", "POWER WALK", "PROFILE", "LAUNCH", "CROWD", "AERIAL",
         "GESTURE", "PEAK", "STATUS", "CALM CHAOS", "LENS", "EXTRA 15", "EXTRA 16", "EXTRA 17"]
# head scale, head y (fraction of H), body on?, world speed: close-ups have big heads, world shots none
LOOK = {"EYES": (2.6, .40, 0, .2), "HELMET": (1.8, .45, 0, .3), "HANDS": (0, 0, 0, .3), "LAUNCH": (0, 0, 0, 2.5),
        "CROWD": (0, 0, 0, 1.6), "AERIAL": (0, 0, 0, 1.0), "LENS": (1.5, .38, 1, .2), "GESTURE": (1.0, .20, 1, .8),
        "CALM CHAOS": (0.8, .33, 1, 3.0), "PROFILE": (1.1, .36, 1, 1.2), "POWER WALK": (0.9, .30, 1, .6)}

def frame(i, k, t, w, h):
    role = ROLES[i % len(ROLES)]; hs, hy, body, speed = LOOK.get(role, (1.0, .34, 1, .8)); m = min(w, h)   # sizes follow the short side, so every aspect gets the same framing
    hue = (i * 23 + 100) % 180
    yy = np.linspace(0, 1, h)[:, None, None]
    hsv = np.zeros((h, w, 3), np.uint8); hsv[..., 0] = hue; hsv[..., 1] = 150; hsv[..., 2] = (30 + 70 * (1 - yy[..., 0]) * np.ones((h, w))).astype(np.uint8)
    img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    rng = np.random.default_rng(i)
    for s in range(26):                                             # the world: streaks moving past
        y = int(rng.uniform(0, h)); L = int(rng.uniform(40, 220)); x = int((rng.uniform(0, w + L) + t * speed * 260 * (1 + s % 3)) % (w + L)) - L
        c = tuple(int(v) for v in rng.uniform(90, 255, 3)); cv2.line(img, (x, y), (x + L, y), c, int(rng.uniform(2, 7)))
    if hs:
        cx = int(w * (0.5 + 0.04 * math.sin(t * 0.8))); cy = int(h * hy); r = int(m * 0.11 * hs)
        if body: cv2.ellipse(img, (cx, cy + int(r * 3.2)), (int(r * 1.5), int(r * 2.4)), 0, 0, 360, (30, 30, 34), -1)
        cv2.circle(img, (cx, cy), r, (150, 170, 205), -1); cv2.circle(img, (cx - r // 3, cy), r // 9 + 1, (20, 20, 20), -1)
        cv2.circle(img, (cx + r // 3, cy), r // 9 + 1, (20, 20, 20), -1)
        cv2.ellipse(img, (cx, cy + r // 2), (r // 3, r // 10 + 1), 0, 0, 180, (60, 60, 120), 2)
    elif role == "HANDS":
        cv2.rectangle(img, (int(w / 2 - m * .25), int(h * .45)), (int(w / 2 + m * .25), int(h * .45 + m * .3)), (40, 40, 48), -1)
    elif role in ("LAUNCH", "AERIAL"):
        x = int(w * (0.2 + 0.05 * t)); cv2.rectangle(img, (x, int(h * .55)), (x + int(m * .6), int(h * .55 + m * .16)), (20, 20, 230), -1)
    lab = f"c{i + 1:02d} {role}"
    cv2.putText(img, lab, (16, h - 30), cv2.FONT_HERSHEY_SIMPLEX, m / 560, (255, 255, 255), max(2, m // 270), cv2.LINE_AA)
    cv2.putText(img, f"{t:.2f}s", (16, h - 30 - int(40 * m / 540)), cv2.FONT_HERSHEY_SIMPLEX, m / 900, (200, 255, 255), 2, cv2.LINE_AA)
    return img

def main():
    a = sys.argv[1:]; root = a[0] if a and not a[0].startswith("--") else "."
    opt = {a[i]: a[i + 1] for i in range(len(a) - 1) if a[i].startswith("--")}
    n, w, h = int(opt.get("--n", 14)), int(opt.get("--w", 540)), int(opt.get("--h", 960))
    os.makedirs(os.path.join(root, "plates"), exist_ok=True); os.makedirs(os.path.join(root, "clips"), exist_ok=True)
    for i in range(n):
        cv2.imwrite(os.path.join(root, "plates", f"k{i + 1:02d}.jpg"), frame(i, 0, 0.0, w * 2, h * 2), [cv2.IMWRITE_JPEG_QUALITY, 88])
        vw = cv2.VideoWriter(os.path.join(root, "clips", f"c{i + 1:02d}.mp4"), cv2.VideoWriter_fourcc(*"mp4v"), 24, (w, h))
        for f in range(120): vw.write(frame(i, f, f / 24, w, h))
        vw.release()
    sheet = np.hstack([cv2.resize(frame(13, 0, 0.0, w, h), (w, h)), cv2.resize(frame(5, 0, 0.0, w, h), (w, h)), cv2.resize(frame(4, 0, 0.0, w, h), (w, h))])
    cv2.putText(sheet, "IDENTITY SHEET (placeholder)", (16, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.imwrite(os.path.join(root, "plates", "sheet.jpg"), sheet)
    print(f"placeholders -> {root}/plates/k01..k{n:02d}.jpg, sheet.jpg, {root}/clips/c01..c{n:02d}.mp4")

if __name__ == "__main__":
    main()
