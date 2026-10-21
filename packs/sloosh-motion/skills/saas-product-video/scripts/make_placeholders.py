#!/usr/bin/env python3
"""make_placeholders.py: free stand-ins for the AI camera shots, so the film's structure, pages and edit can be
built and checked (contact sheets) before the real stills and clips exist, or while they generate.

  python3 <skill>/scripts/make_placeholders.py            # run inside the film folder (reads W, H, FPS from tl.json)
  python3 <skill>/scripts/make_placeholders.py desk phone # only some shots (the feature mode uses desk and phone)

Writes, for each shot name:  plates/<name>.jpg (the "approved still") and clips/<c>.mp4 (a 5 s "AI clip"),
plus plates/ref1.jpg, plates/ref2.jpg (stand-ins for the user's own uploaded photos that the UI shows).
  desk  -> plates/desk.jpg  + clips/c1.mp4   person at a laptop, the screen is the key light (screen faces away)
  phone -> plates/phone.jpg + clips/c2.mp4   a hand holding a phone, screen glow only
  world -> plates/world.jpg + clips/c3.mp4   the customer's world: a product on a wet street at dusk
Every frame carries a small "PLACEHOLDER" label. Replace every file with the real approved stills and clips.
Deterministic; needs numpy, opencv-python and ffmpeg. It downloads nothing.
"""
import json, math, os, shutil, subprocess, sys
try:
    import cv2, numpy as np
except ImportError:
    sys.exit("make_placeholders.py needs numpy and opencv-python. Ask the user before you install them (a virtual environment is best).")

def _load_tl():
    if not os.path.exists("tl.json"):
        return {}
    with open("tl.json", encoding="utf-8") as f:
        return json.load(f)

tl = _load_tl()
FW, FH, FPS = tl.get("W", 1920), tl.get("H", 1080), tl.get("FPS", 24)
W, H = FW // 4, FH // 4                      # scenes are drawn at quarter size, then upscaled (placeholders need no detail)
S = min(W, H) / 1080.0
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)

def glow(cx, cy, r, col, k=1.0):
    g = np.exp(-(((XX - cx) ** 2 + (YY - cy) ** 2) / (2 * r * r)))[..., None]
    return g * np.array(col, np.float32)[None, None, :] * k

def vgrad(top, bot):
    t = (YY / H)[..., None]; return np.array(top, np.float32) * (1 - t) + np.array(bot, np.float32) * t

def label(img, name):
    s = min(FW, FH) / 1080.0
    cv2.putText(img, f"PLACEHOLDER  {name}", (int(24 * s), FH - int(24 * s)), cv2.FONT_HERSHEY_SIMPLEX, 0.7 * s, (200, 200, 200), max(1, int(2 * s)), cv2.LINE_AA)
    return img

def up(img):
    return cv2.resize(np.clip(img, 0, 255).astype(np.uint8), (FW, FH), interpolation=cv2.INTER_CUBIC)

def grain(img, seed):
    return np.clip(img.astype(np.float32) + cv2.resize(np.random.default_rng(seed).normal(0, 5, (FH // 3, FW // 3)).astype(np.float32), (FW, FH))[..., None], 0, 255)

def desk(u):
    """u 0..1 through the clip: slow push-in, the person leans toward the screen, the glow brightens"""
    img = vgrad((26, 22, 30), (10, 9, 12))                                    # BGR: dark room
    img += glow(W * 0.82, H * 0.18, 260 * S, (40, 70, 120), 0.8)              # warm practical lamp, far right
    cx, cy = W * (0.52 - 0.02 * u), H * 0.62
    img += glow(cx + 40 * S, cy - 120 * S, 340 * S, (190, 140, 90), 0.55 + 0.35 * u)   # the screen is the key light (cool)
    cv2.rectangle(img, (0, int(H * 0.74)), (W, H), (34, 30, 38), -1)                  # desk
    lap = np.array([[cx - 260 * S, cy + 110 * S], [cx + 260 * S, cy + 110 * S], [cx + 200 * S, cy - 210 * S], [cx - 200 * S, cy - 210 * S]], np.int32)
    cv2.fillConvexPoly(img, lap, (22, 20, 24))                                         # laptop lid, back to camera
    hx, hy = W * (0.30 + 0.03 * u), H * (0.44 + 0.02 * u)
    cv2.ellipse(img, (int(hx), int(hy)), (int(70 * S), int(88 * S)), 0, 0, 360, (60, 70, 92), -1)            # head
    cv2.ellipse(img, (int(hx + 10 * S), int(hy + 220 * S)), (int(190 * S), int(150 * S)), 0, 180, 360, (30, 30, 40), -1)  # hoodie shoulders
    img += glow(hx + 60 * S, hy, 80 * S, (150, 110, 70), 0.6 + 0.3 * u)               # screen light on the face
    return img

def phone(u):
    img = vgrad((40, 34, 44), (18, 16, 20))
    img += glow(W * 0.25, H * 0.3, 380 * S, (60, 90, 140), 0.5)
    ang = -8 + 6 * u; c = (W * 0.55, H * 0.55)
    box = cv2.boxPoints(((c[0], c[1]), (300 * S, 600 * S), ang)).astype(np.int32)
    img += glow(c[0], c[1], 260 * S, (200, 170, 140), 0.45)                           # screen glow (no UI)
    cv2.fillConvexPoly(img, box, (16, 16, 18))
    inner = cv2.boxPoints(((c[0], c[1]), (270 * S, 570 * S), ang)).astype(np.int32)
    cv2.fillConvexPoly(img, inner, (150 + 40 * u, 120 + 30 * u, 100))
    cv2.ellipse(img, (int(c[0] - 40 * S), int(c[1] + 260 * S)), (int(220 * S), int(120 * S)), ang, 0, 360, (70, 90, 130), -1)  # hand
    cv2.ellipse(img, (int(c[0] + 90 * S - 30 * S * u), int(c[1] + 60 * S - 50 * S * u)), (int(40 * S), int(90 * S)), ang - 30, 0, 360, (80, 100, 140), -1)  # thumb taps
    return img

def world(u):
    img = vgrad((120, 70, 60), (30, 24, 40))                                  # dusk sky into a wet street (BGR)
    hor = int(H * 0.55); img[hor:] = vgrad((50, 40, 50), (20, 18, 26))[hor:]
    for k in range(9):                                                        # bokeh street lights drifting
        x = (W * (0.08 + 0.11 * k) + 60 * S * u * (1 if k % 2 else -1)) % W
        img += glow(x, H * (0.30 + 0.05 * (k % 3)), 40 * S, (90, 160, 255), 0.7)
        img += glow(x, H * (0.80 + 0.04 * (k % 3)), 60 * S, (60, 110, 200), 0.35)    # reflections
    cx, cy = W * 0.5, H * 0.66
    cv2.ellipse(img, (int(cx), int(cy + 70 * S)), (int(300 * S), int(40 * S)), 0, 0, 360, (12, 10, 14), -1)
    cv2.ellipse(img, (int(cx), int(cy)), (int(260 * S), int(90 * S)), -4 + 3 * u, 180, 360, (200, 200, 210), -1)   # the product
    cv2.rectangle(img, (int(cx - 260 * S), int(cy - 10 * S)), (int(cx + 260 * S), int(cy + 40 * S)), (230, 230, 236), -1)
    img += glow(cx - 120 * S + 260 * S * u, cy - 40 * S, 70 * S, (255, 255, 255), 0.5)                 # light passing over it
    return img

SHOTS = {"desk": ("c1", desk), "phone": ("c2", phone), "world": ("c3", world)}

def write_clip(path, fn, name, sec=5.0):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{FW}x{FH}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    n = int(sec * FPS)
    for f in range(n):
        u = f / (n - 1); z = 1 + 0.06 * u
        im = fn(u); M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, z)
        im = up(cv2.warpAffine(np.clip(im, 0, 255).astype(np.uint8), M, (W, H), borderMode=cv2.BORDER_REFLECT))
        p.stdin.write(label(grain(im, f).astype(np.uint8), name).tobytes())
    p.stdin.close()
    if p.wait() != 0: sys.exit(f"make_placeholders.py: ffmpeg failed to write {path}")

def photo(path, hue, seed):
    """stand-in for a user's own uploaded photo (a product shot / a moodboard image), 4:5"""
    w, h = 800, 1000; yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    base = np.array(hue, np.float32); img = np.ones((h, w, 3), np.float32) * base * 0.55
    img += np.exp(-(((xx - w * .5) ** 2 + (yy - h * .45) ** 2) / (2 * 260 ** 2)))[..., None] * base * 0.6
    cv2.ellipse(img, (w // 2, int(h * .55)), (220, 300), 0, 0, 360, tuple(int(c * 0.35) for c in hue), -1)
    img = np.clip(img, 0, 255).astype(np.uint8)
    cv2.putText(img, "PLACEHOLDER", (24, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (235, 235, 235), 2, cv2.LINE_AA)
    cv2.imwrite(path, img, [cv2.IMWRITE_JPEG_QUALITY, 90])

if __name__ == "__main__":
    names = [a for a in sys.argv[1:] if a in SHOTS] or ([] if "--refs" in sys.argv else list(SHOTS))
    if names and not shutil.which("ffmpeg"):
        sys.exit("make_placeholders.py needs ffmpeg on PATH. Ask the user before you install it.")
    os.makedirs("plates", exist_ok=True); os.makedirs("clips", exist_ok=True)
    for nm in names:
        c, fn = SHOTS[nm]
        cv2.imwrite(f"plates/{nm}.jpg", label(grain(up(fn(0.0)), 1).astype(np.uint8), nm), [cv2.IMWRITE_JPEG_QUALITY, 90])
        write_clip(f"clips/{c}.mp4", fn, nm); print(f"plates/{nm}.jpg + clips/{c}.mp4")
    photo("plates/ref1.jpg", (90, 140, 220), 1); photo("plates/ref2.jpg", (170, 120, 200), 2); print("plates/ref1.jpg plates/ref2.jpg")
