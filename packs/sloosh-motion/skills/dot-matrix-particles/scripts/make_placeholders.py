#!/usr/bin/env python3
"""make_placeholders.py: free stand-ins for the dot-matrix-particles example film, so tl.py / edit.py run
before (or without) Sloosh generations. They mimic what the real stills and clips must be: the subject on PURE BLACK,
one hard key from camera-left (8:1), so luminance alone isolates the subject and gives the point cloud its depth.
Every frame is tagged "PLACEHOLDER" in a corner.

  python3 <this skill>/scripts/make_placeholders.py <film_dir> [--force]

Writes plates/portrait.jpg, plates/product.jpg, clips/c1.mp4 (head turns three-quarter -> lens, blinks),
clips/c2.mp4 (product, slow orbit: the highlight band travels). Half resolution; filmkit scales them.
An existing file is kept (a real shot may already be there); --force replaces it.
"""
import json, os, shutil, subprocess, sys
import numpy as np, cv2

film, W, H, FPS, K = ".", 2, 2, 30, 2       # set by main() from tl.json; K = the width of a 9:16 frame of this height
FORCE = False
yy = xx = None

def tag(img, name):
    cv2.putText(img, "PLACEHOLDER " + name, (12, H - 14), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (70, 70, 70), 1, cv2.LINE_AA); return img

def portrait(turn=0.0, blink=0.0):
    """head-and-shoulders, hard key from camera-left, pure black background. turn -1 (three-quarter) .. 0 (lens)."""
    a = np.zeros((H, W, 3), np.float32); cx = W * 0.5 + K * 0.04 * turn; cy = H * 0.36; rx, ry = K * 0.19, H * 0.135
    nx, ny = (xx - cx) / rx, (yy - cy) / ry; head = nx ** 2 + ny ** 2 < 1
    nz = np.sqrt(np.clip(1 - nx ** 2 - ny ** 2, 0, 1)); lx, lz = -0.75 + 0.3 * turn, 0.65                      # key from the left
    shade = np.clip(nx * lx + nz * lz - ny * 0.15, 0, 1) ** 1.3
    skin = np.float32([150, 175, 215])
    a[head] = (skin * (0.06 + 1.1 * shade[..., None]))[head]
    hair = head & (ny < -0.45 + 0.1 * np.sin(nx * 6)); a[hair] *= 0.25
    for ex in (-0.36, 0.36):                                                                                  # eyes, nose, mouth
        e = ((xx - (cx + (ex + 0.08 * turn) * rx)) / (rx * 0.16)) ** 2 + ((yy - (cy + 0.05 * ry)) / (ry * 0.07 * (1 - 0.9 * blink))) ** 2 < 1
        a[e] = (40, 35, 30); a[e & (((xx - (cx + (ex + 0.08 * turn) * rx)) ** 2 + (yy - (cy + 0.05 * ry)) ** 2) < (rx * 0.04) ** 2)] = (230, 230, 230)
    cv2.line(a, (int(cx + 0.05 * turn * rx), int(cy + 0.15 * ry)), (int(cx - 0.06 * rx), int(cy + 0.42 * ry)), (40, 50, 70), 3)
    cv2.ellipse(a, (int(cx), int(cy + 0.62 * ry)), (int(rx * 0.28), int(ry * 0.06)), 0, 0, 180, (60, 60, 120), 3)
    neck = (np.abs(xx - W * 0.5) < K * 0.08) & (yy > cy + ry * 0.8) & (yy < H * 0.6)
    sh = ((xx - W * 0.5) / (K * 0.46)) ** 2 + ((yy - H * 0.82) / (H * 0.24)) ** 2 < 1
    body = (neck | sh) & ~head; bshade = np.clip(0.9 - (xx - W * 0.5 + K * 0.3) / K, 0.05, 1)
    a[body] = (np.float32([30, 30, 34]) * (0.15 + 1.0 * bshade[..., None]))[body]
    return a

def product(spin=0.3, zoom=1.0):
    """bottle on pure black: two strip-softbox edge highlights, a travelling band (spin 0..1), an accent cap."""
    a = np.zeros((H, W, 3), np.float32); cx = W * 0.5; bw, bh = K * 0.3 * zoom, H * 0.42 * zoom; top = H * 0.5 - bh * 0.42
    body = (np.abs(xx - cx) < bw / 2) & (yy > top) & (yy < top + bh); rel = (xx - cx) / (bw / 2)
    s = 0.12 + 0.9 * np.exp(-((rel - (spin * 2.4 - 1.2)) / 0.16) ** 2) + 0.8 * np.exp(-((np.abs(rel) - 0.9) / 0.05) ** 2)
    s *= 0.75 + 0.25 * np.cos((yy - top) / bh * 3.1)
    a[body] = (np.float32([120, 150, 190]) * s[..., None])[body]
    shoulder = (np.abs(xx - cx) < bw * 0.25) & (yy > top - bh * 0.12) & (yy <= top); a[shoulder] = (np.float32([120, 150, 190]) * (0.3 + 0.7 * s[..., None]))[shoulder]
    cap = (np.abs(xx - cx) < bw * 0.2) & (yy > top - bh * 0.3) & (yy <= top - bh * 0.12); a[cap] = (np.float32([60, 120, 230]) * (0.35 + 0.8 * s[..., None]))[cap]
    label = body & (yy > top + bh * 0.45) & (yy < top + bh * 0.65) & (np.abs(rel) < 0.7); a[label] *= 0.35
    return a

def fin(a, seed=0): return np.clip(a + np.random.default_rng(seed).normal(0, 2, a.shape), 0, 255).astype(np.uint8)
def keep(path):
    if FORCE or not os.path.exists(path): return False
    print("kept", os.path.relpath(path, film)); return True
def still(name, a):
    if keep(os.path.join(film, "plates", name + ".jpg")): return
    cv2.imwrite(os.path.join(film, "plates", name + ".jpg"), tag(fin(a), name), [cv2.IMWRITE_JPEG_QUALITY, 92]); print("plate", name)
def clip(name, fn, dur=5.0):
    if keep(os.path.join(film, "clips", name + ".mp4")): return
    n = int(dur * FPS); p = subprocess.Popen(["ffmpeg", "-y" if FORCE else "-n", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", os.path.join(film, "clips", name + ".mp4")], stdin=subprocess.PIPE)
    for i in range(n): p.stdin.write(tag(fin(fn(i / (n - 1)), i), name).tobytes())
    p.stdin.close()
    if p.wait() != 0: sys.exit("ffmpeg could not write clips/" + name + ".mp4")
    print("clip", name)

def main():
    global film, W, H, FPS, K, yy, xx, FORCE
    args = [a for a in sys.argv[1:] if a != "--force"]; FORCE = len(args) < len(sys.argv) - 1
    film = os.path.abspath(args[0] if args else ".")
    tl_path = os.path.join(film, "tl.json")
    if not os.path.isfile(tl_path): sys.exit("no tl.json in " + film + ": run python3 tl.py in the film folder first")
    if shutil.which("ffmpeg") is None: sys.exit("ffmpeg is not on PATH: ask the user to install it, then run this again")
    with open(tl_path) as fh: tl = json.load(fh)
    W, H = tl["W"] // 4 * 2, tl["H"] // 4 * 2; FPS = tl.get("FPS", 30)       # half size, kept even for H.264
    K = min(W, H * 9 / 16)                                                    # the subject keeps its 9:16 proportions in any frame
    for d in ("plates", "clips"): os.makedirs(os.path.join(film, d), exist_ok=True)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    still("portrait", portrait(0.0)); still("product", product(0.35))
    clip("c1", lambda u: portrait(turn=-1 + min(1, u * 1.6), blink=max(0.0, 1 - abs(u - 0.8) / 0.04)))
    clip("c2", lambda u: product(spin=u, zoom=1 + 0.06 * u))

if __name__ == "__main__":
    main()
