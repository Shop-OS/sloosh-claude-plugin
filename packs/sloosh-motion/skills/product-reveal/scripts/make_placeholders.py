#!/usr/bin/env python3
"""make_placeholders.py: zero-credit stand-ins for every product-reveal source, so tl.py / edit.py / the HTML pages can be
built and checked while the real shots are generating (build the skeleton first).

  python3 <skill>/scripts/make_placeholders.py [film_folder] [--w 1080 --h 1920] [--force]
The frame size and the product box (tl.PACK) come from tl.json in the film folder (run tl.py first), else from --w and
--h, else 1080x1920. The stand-in product stands in the PACK box, so the plates line up with ui/packshot.html.

Writes the exact filenames examples/dark_luxury/edit.py expects:
  plates/product_cut.png    transparent cutout (stand-in for scripts/cutout.py on the real photo)
  plates/hero.jpg           the product on the dark set (stand-in for the approved generated hero still)
  plates/set_empty.jpg      the same set without the product (the packshot background)
  refs/front.jpg            the product on a plain light background (stand-in for the user's front photo; an existing file is kept)
  plates/hook.jpg anchor.jpg label.jpg material.jpg action.jpg   the other approved stills (start frames)
  clips/hook.mp4 anchor.mp4 label.mp4 material.mp4 action.mp4 hero.mp4   5 s, 30 fps stand-ins for generated clips
  clips/label_macro.mp4     a slow push across the label (stand-in for scripts/label_macro.py)
The stand-in product is a perfume bottle labelled MAISON ÉCLAT / EAU DE PARFUM / 50 ML. Each clip carries a small grey
"PH <name>" tag bottom-right so you can tell the shots apart on a QA sheet. It never overwrites a file that already exists (a real still, clip or cutout stays), unless you pass --force.
Replace every placeholder before delivery.
Deterministic. Writes only inside the film folder. Needs Python 3.9+, Pillow, numpy, OpenCV and ffmpeg.
"""
import json, os, shutil, subprocess, sys
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

FONT_DIR = "fonts"


def font(sz):
    """the film's vendored serif (fonts/ from new_film.sh), else Pillow's built-in font"""
    p = os.path.join(FONT_DIR, "bodoni-moda-latin-500-normal.woff2")
    if os.path.exists(p):
        try:
            return ImageFont.truetype(p, sz)
        except (OSError, ValueError):
            pass
    try:
        return ImageFont.load_default(size=sz)
    except TypeError:
        return ImageFont.load_default()

def vgrad(w, h, top, bot):
    t = np.linspace(0, 1, h)[:, None, None]; a = np.array(top)[None, None]; b = np.array(bot)[None, None]
    return Image.fromarray(np.repeat((a + (b - a) * t).astype(np.uint8), w, axis=1))

def hgrad_alpha(w, h, stops):
    xs = np.linspace(0, 1, w); row = np.interp(xs, [s[0] for s in stops], [s[1] for s in stops]).astype(np.uint8)
    return Image.fromarray(np.repeat(row[None, :], h, axis=0), "L")

def bottle(S=3, cap_dy=0):
    """a perfume bottle at scale S (S=1 -> 600x1000), cap lifted by cap_dy base px. RGBA."""
    W, H = 600 * S, 1000 * S; img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    body = (60 * S, 330 * S, 540 * S, 980 * S)
    liquid = vgrad(W, H, (150, 88, 30), (62, 30, 10)).convert("RGBA")
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).rounded_rectangle(body, 46 * S, fill=255); img.paste(liquid, (0, 0), m)
    shade = hgrad_alpha(W, H, [(0, 0), (.12, 150), (.22, 30), (.5, 0), (.78, 40), (.88, 170), (1, 0)])
    img.paste(Image.new("RGBA", (W, H), (20, 10, 4, 255)), (0, 0), ImageChops.multiply(shade, m))
    spec = Image.new("L", (W, H), 0); d = ImageDraw.Draw(spec)
    d.rounded_rectangle((110 * S, 360 * S, 135 * S, 950 * S), 12 * S, fill=210); d.rounded_rectangle((470 * S, 380 * S, 480 * S, 940 * S), 5 * S, fill=110)
    img.paste(Image.new("RGBA", (W, H), (255, 236, 205, 255)), (0, 0), ImageChops.multiply(spec.filter(ImageFilter.GaussianBlur(5 * S)), m))
    d2 = ImageDraw.Draw(img); d2.rectangle((250 * S, 285 * S, 350 * S, 335 * S), fill=(120, 95, 60, 255))     # neck
    cy = -cap_dy * S; cap = (170 * S, 60 * S + cy, 430 * S, 290 * S + cy)
    cm = Image.new("L", (W, H), 0); ImageDraw.Draw(cm).rounded_rectangle(cap, 18 * S, fill=255)
    gold = np.repeat(np.interp(np.linspace(0, 1, W), [0, .3, .42, .5, .7, 1], [60, 120, 250, 170, 210, 70])[None, :, None].astype(np.uint8), H, 0).repeat(3, 2)
    gold = ImageChops.multiply(Image.fromarray(gold).convert("RGBA"), Image.new("RGBA", (W, H), (214, 170, 92, 255)))
    img.paste(gold, (0, 0), cm)
    for x in range(178 * S, 428 * S, 9 * S): d2.line((x, 70 * S + cy, x, 280 * S + cy), fill=(90, 66, 30, 120), width=max(1, S))
    d2.rectangle((150 * S, 560 * S, 450 * S, 790 * S), fill=(232, 222, 204, 255))
    d2.rectangle((158 * S, 568 * S, 442 * S, 782 * S), outline=(150, 120, 70, 255), width=2 * S)
    for txt, sz, y in [("MAISON", 17, 596), ("ÉCLAT", 44, 632), ("EAU DE PARFUM", 17, 704), ("50 ML", 17, 740)]:
        f = font(sz * S); tw = d2.textlength(txt, font=f); d2.text(((W - tw) / 2, y * S), txt, font=f, fill=(46, 34, 20, 255))
    return img

def set_plate(W, H, floor_y):
    """dark set: black backdrop with a warm glow, black lacquer floor from floor_y down"""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    g = np.exp(-(((xx - W / 2) / (0.45 * W)) ** 2 + ((yy - floor_y * 0.8) / (0.35 * H)) ** 2))
    bg = np.stack([6 + 26 * g, 6 + 30 * g, 7 + 38 * g], -1)                          # BGR-ish warm glow (RGB order below)
    fl = yy >= floor_y; k = np.clip((yy - floor_y) / (H - floor_y), 0, 1)
    bg[fl] = (np.stack([12 + 20 * g, 12 + 22 * g, 13 + 26 * g], -1) * (1 - 0.6 * k[..., None]))[fl]
    line = np.exp(-((yy - floor_y) / 3) ** 2) * np.exp(-((xx - W / 2) / (0.3 * W)) ** 2) * 40
    return Image.fromarray(np.clip(bg + line[..., None], 0, 255).astype(np.uint8)[..., ::-1].copy())

def tag(arr, name):
    h, w = arr.shape[:2]; cv2.putText(arr, f"PH {name}", (w - 150, h - 18), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (90, 90, 90), 1, cv2.LINE_AA)
    return arr

FORCE = False

def fresh(path):
    """True when the placeholder should be written: the file is missing, or --force was given"""
    if FORCE or not os.path.exists(path):
        return True
    print("keep", path, "(exists; pass --force to replace it)")
    return False

def write_clip(path, frames_fn, n, w, h):
    if not fresh(path):
        return False
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{w}x{h}", "-r", "30", "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    for i in range(n): p.stdin.write(np.ascontiguousarray(frames_fn(i / 30.0)).tobytes())
    p.stdin.close()
    if p.wait() != 0:
        sys.exit("make_placeholders: ffmpeg failed to write " + path)
    return True

def main():
    global FONT_DIR, FORCE
    a = sys.argv[1:]; root = a[0] if a and not a[0].startswith("--") else "."
    if not os.path.isdir(root): sys.exit("make_placeholders: no film folder " + root)
    if shutil.which("ffmpeg") is None: sys.exit("make_placeholders: ffmpeg is missing. Ask the user to install it.")
    FONT_DIR = os.path.join(root, "fonts"); FORCE = "--force" in a
    tlj = {}
    if os.path.exists(os.path.join(root, "tl.json")):
        with open(os.path.join(root, "tl.json"), encoding="utf-8") as f:
            tlj = json.load(f)
    W = int(a[a.index("--w") + 1]) if "--w" in a else int(tlj.get("W", 1080))
    H = int(a[a.index("--h") + 1]) if "--h" in a else int(tlj.get("H", 1920))
    P, CL, RF = os.path.join(root, "plates"), os.path.join(root, "clips"), os.path.join(root, "refs")
    for d in (P, CL, RF): os.makedirs(d, exist_ok=True)
    big = bottle(S=4); bb = big.getbbox(); cut = big.crop(bb)
    if fresh(os.path.join(P, "product_cut.png")):
        cut.resize((cut.width * 1000 // cut.height, 1000), Image.LANCZOS).save(os.path.join(P, "product_cut.png"))
    front = Image.new("RGB", (1080, 1440), (238, 236, 232)); fc = cut.resize((cut.width * 1100 // cut.height, 1100), Image.LANCZOS)
    front.paste(fc, ((1080 - fc.width) // 2, 170), fc)
    if not os.path.exists(os.path.join(RF, "front.jpg")):          # never overwrite the user's own photo
        front.save(os.path.join(RF, "front.jpg"), quality=92)
    # hero still: the cutout standing on the set's floor line, in the tl.PACK box (units: px of a 1080 short side)
    pk = tlj.get("PACK") if (tlj.get("W"), tlj.get("H")) == (W, H) else None    # a PACK made for another size does not fit
    if not pk:                                      # the per-format defaults of examples/dark_luxury/tl.py
        if W / H > 1.2:    pk = {"cx": 960, "bottom": 900, "height": 680}     # 16:9
        elif W / H > 0.85: pk = {"cx": 540, "bottom": 900, "height": 680}     # 1:1
        elif H / W < 1.6:  pk = {"cx": 540, "bottom": 1120, "height": 800}    # 4:5
        else:              pk = {"cx": 540, "bottom": 1330, "height": 940}    # 9:16
    sc = min(W, H) / 1080.0
    floor = int(pk["bottom"] * sc); ph = int(pk["height"] * sc); pw = int(ph * cut.width / cut.height); px = int(pk["cx"] * sc - pw / 2)
    empty = set_plate(W, H, floor)
    if fresh(os.path.join(P, "set_empty.jpg")): empty.save(os.path.join(P, "set_empty.jpg"), quality=92)
    pcx = px + pw / 2
    def hero_img(cap_dy=0, S=4):
        b = bottle(S=S, cap_dy=cap_dy); b = b.crop(b.getbbox()); f = ph / (cut.height / 4 * S)   # px per bottle px
        prod = b.resize((round(b.width * f), round(b.height * f)), Image.LANCZOS); hh = prod.height
        im = empty.convert("RGBA"); sh = Image.new("L", (W, H), 0)
        ImageDraw.Draw(sh).ellipse((px + pw * .05, floor - 22 * sc, px + pw * .95, floor + 22 * sc), fill=200)
        im.paste(Image.new("RGBA", (W, H), (0, 0, 0, 255)), (0, 0), sh.filter(ImageFilter.GaussianBlur(14 * sc)))
        r = np.array(prod.transpose(Image.FLIP_TOP_BOTTOM)); r[..., 3] = (r[..., 3] * np.linspace(.22, 0, r.shape[0])[:, None]).astype(np.uint8)
        im.alpha_composite(Image.fromarray(r), (px, floor)); im.alpha_composite(prod, (px, floor - hh))
        return np.array(im.convert("RGB"))[..., ::-1].copy()
    hero = hero_img()
    if fresh(os.path.join(P, "hero.jpg")): cv2.imwrite(os.path.join(P, "hero.jpg"), hero, [cv2.IMWRITE_JPEG_QUALITY, 92])
    # macro crops of the hero (what image-model edits of the hero still would give), as BGR arrays
    def crop(img, cx, cy, z):
        M = cv2.getRotationMatrix2D((cx, cy), 0, z); M[0, 2] += W / 2 - cx; M[1, 2] += H / 2 - cy
        return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT)
    top = floor - ph; capc = (pcx, top + ph * 0.13); labc = (pcx, top + ph * 0.60); glsc = (px + pw * 0.2, top + ph * 0.85)
    gray = cv2.cvtColor(hero, cv2.COLOR_BGR2GRAY)
    rim = (cv2.Canny(gray, 40, 120) > 0).astype(np.float32); rim = cv2.GaussianBlur(cv2.dilate(rim, np.ones((5, 5))), (0, 0), 2)
    rimimg = np.clip(hero * 0.05 + rim[..., None] * np.array([200, 230, 242]), 0, 255).astype(np.uint8)
    stills = {"hook": crop(rimimg, pcx, top + ph * 0.25, 1.8), "anchor": crop(hero, *capc, 3.2), "label": crop(hero, *labc, 2.6),
              "material": crop(hero, *glsc, 3.0), "action": crop(hero_img(0), pcx, top + ph * 0.25, 1.6)}
    for k, v in stills.items():
        if fresh(os.path.join(P, k + ".jpg")): cv2.imwrite(os.path.join(P, k + ".jpg"), v, [cv2.IMWRITE_JPEG_QUALITY, 90])
    cw, ch = W // 4 * 2, H // 4 * 2                  # half size, rounded to even numbers (the encoder needs them)
    small = lambda im: cv2.resize(im, (cw, ch), interpolation=cv2.INTER_AREA)
    xs = np.linspace(0, 1, cw)[None, :, None]
    def band(img, u, width=0.12, amt=90):
        g = np.exp(-((xs - u) / width) ** 2); return np.clip(img + g * amt * (img.mean(2, keepdims=True) > 12), 0, 255).astype(np.uint8)
    lit_hook = small(crop(hero, pcx, top + ph * 0.25, 1.8)); rim_hook = small(stills["hook"])
    def f_hook(t):                                   # the key light crawls left -> right across the rim silhouette
        u = np.clip((t - 0.3) / 3.5, 0, 1); m = np.clip((u * 1.4 - xs) / 0.25 + 0.5, 0, 1)
        img = (rim_hook * (1 - m) + lit_hook * m).astype(np.uint8); z = 1 + 0.04 * t / 5
        return tag(cv2.warpAffine(img, cv2.getRotationMatrix2D((cw / 2, ch * .3), 0, z), (cw, ch)), "hook")
    def slide(name, src, dx, z0, z1):
        s = small(src)
        def f(t):
            u = t / 5; M = cv2.getRotationMatrix2D((cw / 2, ch / 2), 0, z0 + (z1 - z0) * u); M[0, 2] += dx * (u - .5)
            return tag(band(cv2.warpAffine(s, M, (cw, ch)), -0.2 + 1.4 * u), name)
        return f
    def f_action(t):                                  # the cap lifts off between 1.0 and 3.4 s, then hangs
        dy = 55 * float(np.clip((t - 1.0) / 2.4, 0, 1)) ** 0.8
        return tag(small(crop(hero_img(dy, S=2), pcx, top + ph * 0.25, 1.6)), "action")
    hs = small(hero)
    def f_hero(t):
        M = cv2.getRotationMatrix2D((cw / 2, ch * .55), 0, 1.0 + 0.05 * t / 5); return tag(band(cv2.warpAffine(hs, M, (cw, ch)), (t - .5) / 3.5, .08, 70), "hero")
    jobs = {"hook": f_hook, "anchor": slide("anchor", stills["anchor"], 60, 1.0, 1.06), "label": slide("label", stills["label"], -50, 1.02, 1.08),
            "material": slide("material", stills["material"], 40, 1.0, 1.1), "action": f_action, "hero": f_hero}
    lab = small(stills["label"])
    def f_label_macro(t):                             # a slow push and drift across the label (the code macro move)
        u = t / 5; M = cv2.getRotationMatrix2D((cw / 2, ch / 2), 0, 1.0 + 0.12 * u); M[0, 2] += 40 * (0.5 - u)
        return tag(band(cv2.warpAffine(lab, M, (cw, ch)), -0.1 + 1.2 * u, .1, 60), "label_macro")
    jobs["label_macro"] = f_label_macro
    for k, fn in jobs.items():
        if write_clip(os.path.join(CL, k + ".mp4"), fn, 150, cw, ch):
            print("clip", k)
    print("placeholders ->", root, sorted(os.listdir(P)), sorted(os.listdir(CL)))
    print("tl.PACK for these plates: cx {:.0f}, bottom {:.0f}, height {:.0f}".format(pcx / sc, floor / sc, ph / sc))

if __name__ == "__main__":
    main()
