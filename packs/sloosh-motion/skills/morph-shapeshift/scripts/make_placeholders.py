#!/usr/bin/env python3
"""make_placeholders.py: stand-in stills, transition clips and a logo, so an example film runs BEFORE any generation.

  python3 <skill>/scripts/make_placeholders.py chain   # plates/k0..k7.jpg (one figure, 8 variants, same pose), clips/t1..t3.mp4, refs/logo.png
  python3 <skill>/scripts/make_placeholders.py code    # refs/logo.png only
Run inside the film folder (reads W, H from tl.json). Every placeholder is labelled PLACEHOLDER; replace them with the
approved generated keyframes and transition clips (same names). k5 and k6 are deliberately off-centre so the
figure lock has something to fix. The logo is a stand-in mark: always trace the client's REAL logo file.
"""
import json, os, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

TL = json.load(open("tl.json")) if os.path.exists("tl.json") else {"W": 1080, "H": 1920}
W, H = TL["W"], TL["H"]
# the stand-in logo uses the film's vendored fonts (fonts/, copied by new_film.sh), else Pillow's built-in face
FONTS = ["fonts/inter-tight-latin-wght-normal.woff2", "fonts/archivo-latin-wdth-normal.woff2"]
def font(sz):
    for f in FONTS:
        if os.path.exists(f):
            try:
                ft = ImageFont.truetype(f, sz)
                try: ft.set_variation_by_axes([800])
                except Exception: pass
                return ft
            except Exception: pass                         # this Pillow build cannot read WOFF2
    try: return ImageFont.load_default(size=sz)
    except TypeError: return ImageFont.load_default()

def figure_mask(dx=0, dy=0, sc=1.0):
    """head + neck + shoulders/torso silhouette, centred; returns uint8 mask and the head box"""
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m); u = min(W, H * 9 / 16) / 1080 * sc
    cx, hy = W / 2 + dx, H * 0.27 + dy                  # eyes at ~26% of H, as the keyframe prompt asks
    d.ellipse([cx - 120 * u, hy - 160 * u, cx + 120 * u, hy + 150 * u], fill=255)                      # head
    d.rectangle([cx - 55 * u, hy + 120 * u, cx + 55 * u, hy + 230 * u], fill=255)                       # neck
    d.polygon([(cx - 330 * u, hy + 300 * u), (cx - 120 * u, hy + 215 * u), (cx + 120 * u, hy + 215 * u), (cx + 330 * u, hy + 300 * u),
               (cx + 400 * u, H * 1.05), (cx - 400 * u, H * 1.05)], fill=255)                            # torso
    d.ellipse([cx - 350 * u, hy + 230 * u, cx - 210 * u, hy + 380 * u], fill=255); d.ellipse([cx + 210 * u, hy + 230 * u, cx + 350 * u, hy + 380 * u], fill=255)
    return np.array(m), (cx, hy, u)

def studio(top, bot):
    g = np.linspace(0, 1, H)[:, None, None]; c0, c1 = np.array(top, np.float32), np.array(bot, np.float32)
    img = np.repeat((c0 * (1 - g) + c1 * g), W, axis=1)
    yy, xx = np.mgrid[0:H, 0:W]; spot = np.exp(-(((xx - W / 2) / (0.55 * W)) ** 2 + ((yy - 0.42 * H) / (0.45 * H)) ** 2))[..., None]
    return np.clip(img * (0.55 + 0.6 * spot), 0, 255)

def pattern(kind, base):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); b = np.array(base, np.float32)
    if kind == "knit": return b * (0.85 + 0.15 * (np.sin(xx / 5) * np.sin(yy / 7))[..., None])
    if kind == "scale": v = (np.sin(xx / 18 + np.sin(yy / 22) * 2) * np.sin(yy / 14)) > 0.2; return b * (0.6 + 0.5 * v[..., None])
    if kind == "denim": return b * (0.8 + 0.2 * (np.sin((xx + yy) / 3) > 0)[..., None])
    return b * (0.9 + 0.1 * np.sin(yy / 40)[..., None])

def still(name, label, jacket, kind="", bg=((26, 22, 20), (8, 8, 8)), dx=0, dy=0, sc=1.0, mode="photo"):
    m, (cx, hy, u) = figure_mask(dx, dy, sc); img = studio(*bg); a = (m > 0)[..., None]
    body = pattern(kind, jacket)
    if mode == "wire":
        lines = np.zeros((H, W), np.uint8)
        for y in range(0, H, int(26 * u) or 1): lines[y:y + 2] = 255
        for x in range(0, W, int(26 * u) or 1): lines[:, x:x + 2] = 255
        edge = cv2.morphologyEx(m, cv2.MORPH_GRADIENT, np.ones((5, 5), np.uint8))
        w = ((lines > 0) & (m > 0)) | (edge > 0); img[w] = (255, 230, 90); a = np.zeros_like(a)
    elif mode == "xray":
        img = np.clip(img * 0.4 + np.array((60, 40, 20)), 0, 255); ghost = cv2.GaussianBlur(m, (0, 0), 9)[..., None] / 255.0
        img = img * (1 - ghost * 0.8) + np.array((255, 225, 200)) * ghost * 0.8
        for k in range(6): cv2.line(img, (int(cx - 160 * u), int(hy + (330 + 70 * k) * u)), (int(cx + 160 * u), int(hy + (330 + 70 * k) * u)), (255, 255, 255), int(10 * u))
        a = np.zeros_like(a)
    img = np.where(a, body, img)
    if mode == "photo":                                                    # skin head + hair so the face reads
        hm = np.zeros((H, W), np.uint8); cv2.ellipse(hm, (int(cx), int(hy)), (int(116 * u), int(146 * u)), 0, 0, 360, 255, -1)
        img[hm > 0] = (110, 140, 190) if kind != "scale" else (60, 120, 70)
        cv2.ellipse(img, (int(cx), int(hy - 95 * u)), (int(125 * u), int(70 * u)), 0, 180, 360, (25, 25, 30), -1)
        for ex in (-45, 45): cv2.circle(img, (int(cx + ex * u), int(hy - 10 * u)), int(9 * u), (30, 30, 30), -1)
    img = np.clip(img + np.random.default_rng(len(name)).normal(0, 4, img.shape), 0, 255).astype(np.uint8)
    cv2.putText(img, f"PLACEHOLDER {label}", (40, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 200, 255), 2, cv2.LINE_AA)
    os.makedirs("plates", exist_ok=True); cv2.imwrite(f"plates/{name}.jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 90]); return img

def transition(name, a, b, sec=5.0, fps=30, hold=1.2, morph=1.6):
    """Start+end-frame transition stand-in: hold A, a wipe-melt A->B between hold and hold+morph, hold B. Half-res to stay cheap."""
    os.makedirs("clips", exist_ok=True); w, h = W // 2, H // 2; A, B = cv2.resize(a, (w, h)), cv2.resize(b, (w, h))
    vw = cv2.VideoWriter(f"clips/{name}.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h)); yy = np.linspace(0, 1, h)[:, None, None]
    for f in range(int(sec * fps)):
        u = np.clip((f / fps - hold) / morph, 0, 1); u = u * u * (3 - 2 * u)
        mix = np.clip((u * 1.4 - (1 - yy) * 0.4) / 0.6 * 1.0, 0, 1)
        fr = (A * (1 - mix) + B * mix).astype(np.uint8)
        cv2.putText(fr, f"PLACEHOLDER {name} {f / fps:.1f}s", (20, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 1, cv2.LINE_AA); vw.write(fr)
    vw.release()

def logo():
    """stand-in mark: a yellow wordmark whose O is an eye (ring, white, pupil), dark outline, transparent background."""
    im = Image.new("RGBA", (900, 260), (0, 0, 0, 0)); d = ImageDraw.Draw(im); f = font(190); x = 30; y = 20
    for ch in ["M", "EYE", "RPH"]:
        if ch == "EYE":
            cx, cy, r = x + 92, y + 120, 86
            d.ellipse([cx - r - 10, cy - r - 10, cx + r + 10, cy + r + 10], fill=(17, 17, 17, 255))
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(246, 201, 69, 255)); d.ellipse([cx - 60, cy - 60, cx + 60, cy + 60], fill=(17, 17, 17, 255))
            d.ellipse([cx - 50, cy - 50, cx + 50, cy + 50], fill=(255, 255, 255, 255)); d.ellipse([cx - 4, cy - 26, cx + 40, cy + 18], fill=(17, 17, 17, 255))
            x += 200; continue
        d.text((x, y), ch, font=f, fill=(246, 201, 69, 255), stroke_width=9, stroke_fill=(17, 17, 17, 255)); x += d.textlength(ch, font=f) + 10
    os.makedirs("refs", exist_ok=True); im.crop(im.getbbox()).save("refs/logo.png")

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "chain"; logo()
    if mode == "chain":
        k = {}
        k[0] = still("k0", "k0 HERO", (176, 203, 217))                                   # cream jacket (BGR)
        k[1] = still("k1", "k1 WIREFRAME", (0, 0, 0), mode="wire", bg=((12, 12, 12), (4, 4, 4)))
        k[2] = still("k2", "k2 REPTILE", (60, 130, 70), kind="scale")
        k[3] = still("k3", "k3 X-RAY", (0, 0, 0), mode="xray", bg=((40, 30, 20), (10, 8, 6)))
        k[4] = still("k4", "k4 RED LEATHER", (30, 30, 170))
        k[5] = still("k5", "k5 CREAM KNIT", (200, 225, 238), kind="knit", dx=60, sc=0.92)  # off-centre on purpose
        k[6] = still("k6", "k6 NAVY KNIT", (90, 45, 25), kind="knit", dy=-50, sc=1.06)    # off-centre on purpose
        k[7] = still("k7", "k7 DENIM", (150, 100, 60), kind="denim")
        transition("t1", k[0], k[1]); transition("t2", k[1], k[2]); transition("t3", k[7], k[0])
    print("placeholders ->", "refs/logo.png" + (", plates/k0..k7.jpg, clips/t1..t3.mp4" if mode == "chain" else ""))
