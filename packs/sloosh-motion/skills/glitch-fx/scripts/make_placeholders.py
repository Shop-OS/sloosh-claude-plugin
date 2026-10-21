#!/usr/bin/env python3
"""make_placeholders.py: free stand-ins for the glitch-fx example film, so tl.py / edit.py run before (or
without) Sloosh generations. They mimic what the real stills and clips must look like: one strong practical light,
deep blacks, a centred subject. Every frame is tagged "PLACEHOLDER" in a corner.

  python3 <glitch-fx>/scripts/make_placeholders.py <film_dir> [--core <director>]

<glitch-fx> is this skill's folder. <director> is the sloosh-motion-director skill folder, a sibling of this one;
it is found on its own when both skills are installed. Run tl.py first: this script reads <film_dir>/tl.json.
Needs numpy, opencv-python and ffmpeg on the user's computer. It downloads and installs nothing.

Writes plates/hero.jpg street.jpg macro.jpg product.jpg and clips/c1.mp4 (hero push-in), c2.mp4 (figure walking at
camera: the datamosh B), c3.mp4 (product turntable) and clips/mosh.mp4 (real datamosh c1 -> c2 via the director's clipfx.py).
Placeholders are half resolution (filmkit scales them); real clips arrive at the film size.
"""
import json, os, shutil, subprocess, sys

try:
    import numpy as np, cv2
except ImportError:
    np = cv2 = None

film = core = None; W = H = FPS = U = 0; xx = yy = None     # set in main()

def setup(argv):
    global film, core, W, H, FPS, U, xx, yy
    if np is None:
        sys.exit("!! numpy and opencv-python are missing. Ask the user before installing them (a virtual environment is best).")
    if shutil.which("ffmpeg") is None:
        sys.exit("!! ffmpeg is not on PATH. Ask the user to install it, then run this again.")
    args = [a for a in argv[1:]]
    if "--core" in args:
        i = args.index("--core")
        if i + 1 >= len(args): sys.exit("usage: python3 make_placeholders.py <film_dir> [--core <director>]")
        core = os.path.abspath(args[i + 1]); del args[i:i + 2]
    else:
        core = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "sloosh-motion-director"))
    if not os.path.isfile(os.path.join(core, "scripts", "clipfx.py")):
        print("!! sloosh-motion-director not found at " + core, file=sys.stderr)
        print("   Install the full sloosh-motion plugin (it ships sloosh-motion-director next to glitch-fx),", file=sys.stderr)
        print("   or pass --core <path to the sloosh-motion-director folder>.", file=sys.stderr)
        sys.exit(1)
    film = os.path.abspath(args[0] if args else ".")
    tp = os.path.join(film, "tl.json")
    if not os.path.isfile(tp): sys.exit("!! " + tp + " not found: run `python3 tl.py` inside the film folder first.")
    with open(tp) as fh: tl = json.load(fh)
    W, H = tl["W"] // 4 * 2, tl["H"] // 4 * 2; FPS = tl.get("FPS", 30)     # half size, kept even for yuv420p (4:5 is 1080x1350)
    U = min(W, H * 9 / 16)     # subject width unit: a 9:16 column, so a figure keeps its shape on 16:9, 1:1 and 4:5
    os.makedirs(os.path.join(film, "plates"), exist_ok=True); os.makedirs(os.path.join(film, "clips"), exist_ok=True)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

def glow(cx, cy, r, col, p=2.0):
    g = np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (r * r)) ** (p / 2)); return g[..., None] * np.float32(col)

def tag(img, name):
    cv2.putText(img, "PLACEHOLDER " + name, (12, H - 14), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (90, 90, 90), 1, cv2.LINE_AA); return img

def fin(a, seed=0):
    a = a + np.random.default_rng(seed).normal(0, 3, a.shape).astype(np.float32); return np.clip(a, 0, 255).astype(np.uint8)

def hero(t=0.0, flick=1.0, turn=0.0):
    """low-angle portrait looking up into a bright light above (highlights glitch beautifully)."""
    a = glow(W * 0.5, H * 0.1, W * 0.55, (235, 245, 255)) * flick + glow(W * 0.5, H * 0.45, W * 0.9, (40, 30, 25)) * 0.6
    head = ((xx - W * 0.5 - U * turn) / (U * 0.16)) ** 2 + ((yy - H * 0.42) / (H * 0.12)) ** 2 < 1
    body = (((xx - W * 0.5) / (U * 0.42)) ** 2 + ((yy - H * 0.86) / (H * 0.26)) ** 2 < 1) | ((np.abs(xx - W * 0.5) < U * 0.07) & (yy > H * 0.5) & (yy < H * 0.62))
    sil = (head | body).astype(np.float32); a = a * (1 - sil[..., None]) + sil[..., None] * glow(W * 0.5, H * 0.3, W * 0.5, (70, 80, 95))
    rim = cv2.GaussianBlur(sil, (0, 0), 3) - cv2.GaussianBlur(sil, (0, 0), 9); a += np.clip(rim, 0, 1)[..., None] * np.float32([255, 240, 220]) * 2.2 * flick
    eye_y = H * 0.41
    for ex in (-0.055, 0.055): a += glow(W * 0.5 + U * (turn + ex), eye_y, U * 0.018, (200, 210, 230)) * 0.6
    return a

def street(t=0.0, walk=None):
    """underpass: lines converging on a bright vanishing point, a backlit figure (walk = 0..1 approaches camera)."""
    a = glow(W * 0.5, H * 0.46, W * 0.35, (220, 235, 255)) + glow(W * 0.5, H * 0.46, W * 1.2, (60, 50, 40)) * 0.5
    for k in range(-6, 7):
        x2 = W * 0.5 + k * W * 0.35; cv2.line(a, (int(W * 0.5), int(H * 0.46)), (int(x2), H), (50, 55, 60), 2)
        cv2.line(a, (int(W * 0.5), int(H * 0.46)), (int(x2), 0), (35, 38, 42), 1)
    s = 0.25 if walk is None else 0.25 + 1.6 * walk ** 1.6; cx, cy = W * 0.5, H * (0.62 + 0.18 * (s - 0.25))
    head = ((xx - cx) / (U * 0.05 * s)) ** 2 + ((yy - (cy - H * 0.2 * s)) / (H * 0.03 * s)) ** 2 < 1
    torso = (np.abs(xx - cx) < U * 0.075 * s) & (yy > cy - H * 0.17 * s) & (yy < cy)
    step = 0 if walk is None else np.sin(walk * 18) * 0.035 * s
    legs = ((np.abs(xx - (cx - U * (0.03 * s - step))) < U * 0.025 * s) | (np.abs(xx - (cx + U * (0.03 * s + step))) < U * 0.025 * s)) & (yy >= cy) & (yy < cy + H * 0.16 * s)
    sil = (head | torso | legs).astype(np.float32)[..., None]
    return a * (1 - sil) + sil * 8

def product(t=0.0, spin=0.0, macro=False):
    """bottle on black: rim highlights, a moving specular band (spin 0..1), an accent cap, a floor reflection."""
    a = np.zeros((H, W, 3), np.float32) + glow(W * 0.5, H * 0.2, W * 0.6, (50, 50, 55))
    sc = 1.9 if macro else 1.0; cx, top, bw, bh = W * 0.5, H * (0.36 if not macro else 0.05), U * 0.22 * sc, H * 0.36 * sc
    body = (np.abs(xx - cx) < bw / 2) & (yy > top) & (yy < top + bh)
    cap = (np.abs(xx - cx) < bw * 0.22) & (yy > top - bh * 0.16) & (yy <= top)
    rel = (xx - cx) / (bw / 2)
    shade = (0.25 + 0.75 * np.exp(-((rel - (spin * 2.4 - 1.2)) / 0.18) ** 2) + 0.6 * np.exp(-((np.abs(rel) - 0.92) / 0.06) ** 2))
    a = np.where(body[..., None], np.float32([60, 64, 70]) * shade[..., None] * 1.8, a)
    a = np.where(cap[..., None], np.float32([90, 40, 255]) * (0.5 + 0.5 * shade[..., None]), a)
    if not macro:
        refl = np.flipud(a[int(top - 40):int(top + bh)]) * 0.18; y0 = int(top + bh); h = min(H - y0, refl.shape[0]); a[y0:y0 + h] += refl[:h]
    return a

def still(name, a): cv2.imwrite(os.path.join(film, "plates", name + ".jpg"), tag(fin(a), name), [cv2.IMWRITE_JPEG_QUALITY, 92]); print("plate", name)

def clip(name, fn, dur=5.0):
    out = os.path.join(film, "clips", name + ".mp4"); n = int(dur * FPS)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(n):
        u = i / (n - 1); fr = tag(fin(fn(u), i), name)
        p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait(); print("clip", name, f"{dur:.0f} s")

def push(a, z):
    M = cv2.getRotationMatrix2D((W / 2, H * 0.42), 0, z); return cv2.warpAffine(a, M, (W, H), borderMode=cv2.BORDER_REPLICATE)

def main(argv):
    setup(argv)
    still("hero", hero()); still("street", street()); still("macro", product(macro=True)); still("product", product())
    clip("c1", lambda u: push(hero(turn=0.02 * np.sin(u * 3), flick=0.85 + 0.15 * np.sin(u * 40) ** 2), 1 + 0.12 * u))
    clip("c2", lambda u: street(walk=u))
    clip("c3", lambda u: product(spin=u))
    cf = os.path.join(core, "scripts", "clipfx.py")
    # the real datamosh: c1's last frames pushed around by c2's motion vectors (len 0.8 s, then clean c2)
    a, b = os.path.join(film, "clips", "_a.mp4"), os.path.join(film, "clips", "_b.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "1.0", "-t", "2.0", "-i", os.path.join(film, "clips", "c1.mp4"), "-c:v", "libx264", "-preset", "veryfast", a], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "1.5", "-t", "2.5", "-i", os.path.join(film, "clips", "c2.mp4"), "-c:v", "libx264", "-preset", "veryfast", b], check=True)
    subprocess.run([sys.executable, cf, "datamosh", a, b, os.path.join(film, "clips", "mosh.mp4"), "len=0.8"], check=True, stdout=subprocess.DEVNULL)
    os.remove(a); os.remove(b); print("clip mosh (A 2.0 s + mosh 0.8 s + clean B)")

if __name__ == "__main__":
    main(sys.argv)
