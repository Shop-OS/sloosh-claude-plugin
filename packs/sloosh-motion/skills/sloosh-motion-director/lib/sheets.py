#!/usr/bin/env python3
"""sheets.py: contact sheets for studying references and for QA by looking.

  python3 lib/sheets.py ref   refs/ref.mp4                 # 1 fps overview of the whole reference (+ cut list printed)
  python3 lib/sheets.py dense refs/ref.mp4 10.5 21 --fps 8 # dense sheets of a key moment, frame number burned in
  python3 lib/sheets.py cuts  refs/ref.mp4                 # every cut as frame number + time (for the cut list)
  python3 lib/sheets.py clip  clips/c3.mp4                 # 3 fps sheet of a generated clip: pick its clean window
  python3 lib/sheets.py film  out/film_v2.mp4 [a b] --fps 5   # section sheets of a render, in order
Sheets are written next to the input in a sheets/ folder. Open each sheet and look at it.
"""
import math, os, sys
import cv2, numpy as np

def frames_at(path, times):
    cap = cv2.VideoCapture(path); fps = cap.get(cv2.CAP_PROP_FPS) or 30; out = []
    for t in times:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(round(t * fps))); ok, fr = cap.read()
        if ok: out.append((t, int(round(t * fps)), fr))
    cap.release(); return out, fps

def tile(items, out, cols=6, width=300, label=lambda t, n: f"{t:.2f}s  f{n}"):
    if not items: print("no frames"); return
    tiles = []
    for t, n, fr in items:
        h, w = fr.shape[:2]; im = cv2.resize(fr, (width, int(h * width / w)), interpolation=cv2.INTER_AREA)
        cv2.rectangle(im, (0, 0), (width, 24), (0, 0, 0), -1)
        cv2.putText(im, label(t, n), (6, 17), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA); tiles.append(im)
    th, tw = tiles[0].shape[:2]; rows = math.ceil(len(tiles) / cols)
    sheet = np.full((rows * th, cols * tw, 3), 20, np.uint8)
    for k, im in enumerate(tiles): sheet[(k // cols) * th:(k // cols) * th + im.shape[0], (k % cols) * tw:(k % cols + 1) * tw] = im
    os.makedirs(os.path.dirname(out), exist_ok=True); cv2.imwrite(out, sheet, [cv2.IMWRITE_JPEG_QUALITY, 85]); print("sheet ->", out)

def duration(path):
    cap = cv2.VideoCapture(path); n = cap.get(cv2.CAP_PROP_FRAME_COUNT); f = cap.get(cv2.CAP_PROP_FPS) or 30; cap.release(); return n / f

def cuts(path, thresh=0.35):
    """scene cuts by histogram distance between consecutive frames"""
    cap = cv2.VideoCapture(path); fps = cap.get(cv2.CAP_PROP_FPS) or 30; prev = None; i = 0; out = []
    while True:
        ok, fr = cap.read()
        if not ok: break
        h = cv2.calcHist([cv2.cvtColor(cv2.resize(fr, (160, 90)), cv2.COLOR_BGR2HSV)], [0, 1], None, [32, 32], [0, 180, 0, 256]); cv2.normalize(h, h)
        if prev is not None and cv2.compareHist(prev, h, cv2.HISTCMP_BHATTACHARYYA) > thresh: out.append((i, i / fps))
        prev = h; i += 1
    cap.release(); return out, fps

def outname(path, tag):
    d = os.path.join(os.path.dirname(os.path.abspath(path)), "sheets"); return os.path.join(d, f"{os.path.splitext(os.path.basename(path))[0]}_{tag}.jpg")

def main():
    a = sys.argv[1:]
    if len(a) < 2: sys.exit(__doc__)
    mode, path = a[0], a[1]; opt, nums, i = {}, [], 2
    while i < len(a):                                   # by index: the token after each --flag is its value, never a time
        if a[i].startswith("--"): opt[a[i]] = a[i + 1] if i + 1 < len(a) else ""; i += 2
        else: nums.append(float(a[i])); i += 1
    D = duration(path)
    if mode == "ref":
        items, _ = frames_at(path, [k + 0.5 for k in range(int(D))]); tile(items, outname(path, "1fps"), cols=7, width=260)
        cl, fps = cuts(path); print(f"{len(cl)} cuts ({D:.2f} s, {fps:.0f} fps):", ", ".join(f"f{n}={t:.2f}s" for n, t in cl))
    elif mode == "dense":
        s = nums[0] if nums else 0.0; e = nums[1] if len(nums) > 1 else D; f = float(opt.get("--fps", 8)); ts = list(np.arange(s, min(e, D), 1 / f))
        if not ts: sys.exit(f"no frames between {s} and {e} s (the video is {D:.2f} s)")
        for p in range(0, len(ts), 24):
            items, _ = frames_at(path, ts[p:p + 24]); tile(items, outname(path, f"dense_{s:.1f}_{p // 24}"), cols=8, width=240)
    elif mode == "cuts":
        cl, fps = cuts(path); print("frame,time"); [print(f"{n},{t:.3f}") for n, t in cl]
    elif mode == "clip":
        f = float(opt.get("--fps", 3)); items, _ = frames_at(path, list(np.arange(0, D, 1 / f))); tile(items, outname(path, "3fps"), cols=6, width=240)
    elif mode == "film":
        s = nums[0] if nums else 0.0; e = nums[1] if len(nums) > 1 else D; f = float(opt.get("--fps", 5)); ts = list(np.arange(s, min(e, D), 1 / f))
        if not ts: sys.exit(f"no frames between {s} and {e} s (the video is {D:.2f} s)")
        for p in range(0, len(ts), 30):
            items, _ = frames_at(path, ts[p:p + 30]); tile(items, outname(path, f"film_{ts[p]:.1f}"), cols=10, width=200)
    else: sys.exit(__doc__)

if __name__ == "__main__":
    main()
