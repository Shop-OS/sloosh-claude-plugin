#!/usr/bin/env python3
"""logo_to_path.py: vectorise the REAL logo file (the end-card mark). Never redraw a logo.

The method: upscale the raster 8x, split it into colour masks (k-means on the logo's own colours), trace each
mask with OpenCV contours, and write a crisp layered SVG that stays sharp at any size, plus a JSON the HTML pages read.

Run it inside the film folder (setup_film.sh copies it to lib/):
  python3 lib/logo_to_path.py refs/logo.png --out ui/logo            -> ui/logo.svg, ui/logo.json, ui/logo_check.png
  python3 lib/logo_to_path.py refs/logo.png --colors 3 --icon 0,0,120,96 --out ui/logo
  python3 lib/logo_to_path.py refs/logo.svg --icon x,y,w,h --out ui/logo
      -> an SVG is kept as it is: its <path d> are listed, each part gets a box from its points, and no check
         image is made. Pass --icon in the SVG's own units for the send morph; without it the icon is the whole mark.

logo.json: {"viewBox":[w,h], "layers":[{"color":"#rrggbb","parts":[{"d", "ring", "bbox":[x,y,w,h], "area"}]}],
            "icon":[x,y,w,h], "bbox":[x,y,w,h]}
  d     the part with its own holes (render with fill-rule evenodd)      ring  the outer contour only (for morphing)
  icon  the box the send morph shows inside the tile (eyes, symbol). --icon x,y,w,h in source pixels; auto = the cluster
        of overlapping parts with the most colours (an icon is usually multi-colour), else the left cluster split by the
        widest gap, else the whole mark. LOOK at logo_check.png: traced fill on the left, source on the right, icon box.
Needs opencv-python, numpy, Pillow.
"""
import argparse, json, os, re, sys
import numpy as np, cv2
from PIL import Image

UP = 8

def load(path):
    im = np.array(Image.open(path).convert("RGBA")).astype(np.float32)
    h, w = im.shape[:2]; s = min(UP, 4000 / max(h, w))              # 8x, capped at 4000 px on the long side
    big = cv2.resize(im, (round(w * s), round(h * s)), interpolation=cv2.INTER_CUBIC)
    return im, np.clip(big, 0, 255), s

def palette(big, k):
    """colour clusters of the logo's opaque pixels (alpha) or of non-background pixels (opaque files)."""
    rgb, a = big[..., :3], big[..., 3]
    if a.min() < 250: fg = a > 127
    else:
        corners = np.concatenate([rgb[:6, :6].reshape(-1, 3), rgb[-6:, -6:].reshape(-1, 3), rgb[:6, -6:].reshape(-1, 3), rgb[-6:, :6].reshape(-1, 3)])
        bg = np.median(corners, 0); fg = np.linalg.norm(rgb - bg, axis=2) > 40
    px = rgb[fg].reshape(-1, 3)
    if len(px) < 16: sys.exit("logo_to_path: no logo pixels found. Use a file with a plain or transparent background.")
    sub = px[np.random.default_rng(0).choice(len(px), min(len(px), 60000), replace=False)]
    best = None
    for kk in ([k] if k else range(1, 7)):                            # auto: the smallest k that explains the colours well
        crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 40, 0.5)
        comp, lab, cen = cv2.kmeans(sub.astype(np.float32), kk, None, crit, 3, cv2.KMEANS_PP_CENTERS)
        err = comp / len(sub)
        if best is None or k or err < best[0] * 0.55: best = (err, cen)
        else: break
    cen = best[1]; d = np.linalg.norm(rgb[..., None, :] - cen[None, None], axis=3); lab = np.argmin(d, 2)
    share = np.array([(lab[fg] == i).mean() for i in range(len(cen))]); keep = []
    for i in range(len(cen)):                                   # drop anti-alias clusters: small AND a blend of two others
        o = [j for j in range(len(cen)) if j != i]
        blend = any(np.linalg.norm(np.cross(cen[b] - cen[a], cen[a] - cen[i])) / (np.linalg.norm(cen[b] - cen[a]) + 1e-6) < 30
                    and np.dot(cen[i] - cen[a], cen[b] - cen[a]) > 0 and np.dot(cen[i] - cen[b], cen[a] - cen[b]) > 0 for a in o for b in o if a < b)
        if not (blend and share[i] < 0.12): keep.append(i)
    cen = cen[keep]; d = np.linalg.norm(rgb[..., None, :] - cen[None, None], axis=3); lab = np.argmin(d, 2)
    return fg, cen, lab

def trace(path, k, eps):
    src, big, s = load(path); fg, cen, lab = palette(big, k); H, W = src.shape[:2]; layers = []
    order = np.argsort([-(lab[fg] == i).sum() for i in range(len(cen))])  # biggest colour first (painted first)
    for i in order:
        m = ((lab == i) & fg).astype(np.uint8) * 255
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)); m = cv2.dilate(m, np.ones((2, 2), np.uint8))  # no hairline gaps
        cs, hi = cv2.findContours(m, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
        if not cs: continue
        hi = hi[0]; parts = []
        def poly(c): c = cv2.approxPolyDP(c, eps * s / UP, True).reshape(-1, 2) / s; return "M" + "L".join(f"{x:.2f} {y:.2f}" for x, y in c) + "Z"
        for j, c in enumerate(cs):
            if hi[j][3] >= 0: continue                                 # holes are attached to their parent below
            a = cv2.contourArea(c) / s / s
            if a < W * H * 0.00015: continue                           # specks
            holes = [poly(cs[h]) for h in range(len(cs)) if hi[h][3] == j and cv2.contourArea(cs[h]) / s / s > W * H * 0.00005]
            x, y, w, h = cv2.boundingRect(c); ring = poly(c)
            parts.append({"d": ring + "".join(holes), "ring": ring, "bbox": [round(x / s, 2), round(y / s, 2), round(w / s, 2), round(h / s, 2)], "area": round(a, 1)})
        if parts:
            c = cen[i]; layers.append({"color": "#%02x%02x%02x" % tuple(int(v) for v in c[:3]), "parts": sorted(parts, key=lambda p: -p["area"])})
    return [W, H], layers, src

ARGS = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "T": 2, "A": 7, "Z": 0}

def path_bbox(d):
    """box of a path's end and control points (absolute and relative commands; arcs by their end points)."""
    toks = re.findall(r"[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?", d)
    x = y = sx = sy = 0.0; pts = []; cmd = None; i = 0
    while i < len(toks):
        if toks[i].isalpha(): cmd = toks[i]; i += 1
        if cmd is None: break
        C = cmd.upper(); rel = cmd != C; n = ARGS[C]
        if C == "Z": x, y = sx, sy; cmd = None; continue
        if i + n > len(toks) or any(t.isalpha() for t in toks[i:i + n]): break
        v = [float(t) for t in toks[i:i + n]]; i += n
        if C == "H": x = v[0] + (x if rel else 0)
        elif C == "V": y = v[0] + (y if rel else 0)
        elif C == "A": x, y = v[5] + (x if rel else 0), v[6] + (y if rel else 0)
        else:
            for k in range(0, n, 2):
                px, py = v[k] + (x if rel else 0), v[k + 1] + (y if rel else 0)
                if k < n - 2: pts.append((px, py))
            x, y = px, py
        pts.append((x, y))
        if C == "M": sx, sy = x, y; cmd = "l" if rel else "L"
    if not pts: return None
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return [round(min(xs), 2), round(min(ys), 2), round(max(xs) - min(xs), 2), round(max(ys) - min(ys), 2)]

def from_svg(path):
    with open(path, encoding="utf-8") as f: s = f.read()
    vb = re.search(r'viewBox="([-\d.\se,]+)"', s)
    v = [float(x) for x in re.split(r"[\s,]+", vb.group(1).strip())] if vb else [0, 0, 0, 0]
    if re.search(r"<(circle|rect|ellipse|polygon|polyline|line|text|use)\b", s):
        print("!! the SVG has shapes or text that are not paths. Flatten the shapes and convert text to outlines in your vector editor, then export again.")
    def own_fill(attrs):                                                  # fill="#rgb" or style="fill:#rgb"
        f = re.search(r'(?:\bfill\s*=\s*"|fill\s*:\s*)(#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3})\b', attrs)
        if not f: return None
        c = f.group(1); return c if len(c) == 7 else "#" + "".join(ch * 2 for ch in c[1:])
    parts = []; stack = ["#000000"]                                       # a path takes its own fill, else its group's
    for m in re.finditer(r"<(/?)([A-Za-z][\w:-]*)([^>]*?)(/?)>", s):
        close, tag, attrs, selfclose = m.groups()
        if tag == "g":
            if close: stack = stack[:-1] or ["#000000"]
            elif not selfclose: stack.append(own_fill(attrs) or stack[-1])
        elif tag == "path" and not close:
            d = re.search(r'\sd\s*=\s*"([^"]+)"', " " + attrs)
            if d: parts.append((own_fill(attrs) or stack[-1], d.group(1)))
    layers = {}
    for col, d in parts:
        ring = re.split(r"[Zz]", d)[0] + "Z"; b = path_bbox(d)
        layers.setdefault(col, []).append({"d": d, "ring": ring, "bbox": b, "area": round(b[2] * b[3], 1) if b else None})
    allb = [p["bbox"] for ly in layers.values() for p in ly if p["bbox"]]
    if not v[2] and allb: u = boxes_union(allb); v = [u[0], u[1], u[2], u[3]]
    return v, [{"color": c, "parts": p} for c, p in layers.items()], None

def boxes_union(bs):
    x0 = min(b[0] for b in bs); y0 = min(b[1] for b in bs); x1 = max(b[0] + b[2] for b in bs); y1 = max(b[1] + b[3] for b in bs); return [x0, y0, x1 - x0, y1 - y0]

def auto_icon(layers, W):
    P = [(k, p["bbox"]) for k, ly in enumerate(layers) for p in ly["parts"] if p["bbox"]]
    if not P: return None
    cl = []                                                               # clusters of overlapping parts
    for k, b in P:
        hit = [c for c in cl if any(not (b[0] > o[0] + o[2] or o[0] > b[0] + b[2] or b[1] > o[1] + o[3] or o[1] > b[1] + b[3]) for _, o in c)]
        new = [(k, b)] + [x for c in hit for x in c]; cl = [c for c in cl if c not in hit] + [new]
    colours = lambda c: len({k for k, _ in c})
    rich = max(cl, key=lambda c: (colours(c), sum(b[2] * b[3] for _, b in c)))
    if colours(rich) >= 3: return boxes_union([b for _, b in rich])
    xs = sorted(boxes_union([b for _, b in c]) for c in cl); gaps = [(xs[i + 1][0] - (xs[i][0] + xs[i][2]), i) for i in range(len(xs) - 1)]
    if gaps and max(gaps)[0] > 0.04 * W: g, i = max(gaps); return boxes_union(xs[:i + 1])
    return boxes_union([b for _, b in P])

def check(layers, src, vb, icon, out):
    W, H = int(vb[0]), int(vb[1]); s = 600 / max(W, H); cw, ch = int(W * s), int(H * s)
    board = np.full((ch, cw, 3), 128, np.uint8)
    for ly in layers:
        col = tuple(int(ly["color"][i:i + 2], 16) for i in (5, 3, 1))
        for p in ly["parts"]:                                    # evenodd, like the SVG: holes show what is beneath
            m = np.zeros((ch, cw), np.uint8)
            for n, sub in enumerate(re.split(r"[Zz]", p["d"])):
                pts = re.findall(r"(-?[\d.]+) (-?[\d.]+)", sub)
                if len(pts) > 2: cv2.fillPoly(m, [(np.array(pts, float) * s).astype(np.int32)], 255 if n == 0 else 0)
            board[m > 0] = col
    if icon: x, y, w, h = [int(v * s) for v in icon]; cv2.rectangle(board, (x, y), (x + w, y + h), (0, 255, 255), 2)
    right = np.full((ch, cw, 3), 128, np.uint8)
    if src is not None:
        r = cv2.resize(src, (cw, ch)); a = r[..., 3:4] / 255.0; right = (r[..., [2, 1, 0]] * a + 128 * (1 - a)).astype(np.uint8)
    cv2.imwrite(out, np.hstack([board, right]))

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("logo"); ap.add_argument("--out", default="ui/logo")
    ap.add_argument("--colors", type=int, default=0, help="colour layers (0 = auto)"); ap.add_argument("--eps", type=float, default=1.0, help="simplify, px at 8x")
    ap.add_argument("--icon", help="x,y,w,h in source pixels")
    a = ap.parse_args(); os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    if not os.path.isfile(a.logo): sys.exit(f"logo_to_path: {a.logo} not found. Save the real logo there first.")
    if os.path.abspath(a.out + ".svg") == os.path.abspath(a.logo): sys.exit("logo_to_path: --out would overwrite the source SVG. Choose another --out, for example ui/logo.")
    is_svg = a.logo.lower().endswith(".svg")
    if is_svg: vb4, layers, src = from_svg(a.logo)
    else:
        wh, layers, src = trace(a.logo, a.colors, a.eps)
        vb4 = [0, 0] + wh
    if not layers: sys.exit("logo_to_path: no shapes found. Check the file has a plain or transparent background, or that the SVG has <path> elements.")
    vb = [vb4[2], vb4[3]]
    allb = [p["bbox"] for ly in layers for p in ly["parts"] if p["bbox"]]
    whole = boxes_union(allb) if allb else list(vb4)
    if a.icon:
        icon = [float(v) for v in a.icon.split(",")]
        if len(icon) != 4: sys.exit("logo_to_path: --icon needs four numbers: x,y,w,h")
    else:
        icon = auto_icon(layers, vb[0]) if not is_svg else None
        if icon is None:
            icon = whole
            print("!! icon box = the whole mark. For the send morph, pass --icon x,y,w,h around the symbol (in the logo's own units).")
    J = {"viewBox": vb, "origin": vb4[:2], "layers": layers, "icon": icon, "bbox": whole}
    with open(a.out + ".json", "w", encoding="utf-8") as f: json.dump(J, f)
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb4[0]} {vb4[1]} {vb[0]} {vb[1]}">' + "".join(
        f'<g fill="{ly["color"]}">' + "".join(f'<path fill-rule="evenodd" d="{p["d"]}"/>' for p in ly["parts"]) + "</g>" for ly in layers) + "</svg>"
    with open(a.out + ".svg", "w", encoding="utf-8") as f: f.write(svg)
    if src is not None: check(layers, src, vb, icon, a.out + "_check.png")
    else: print("note: no check image for an SVG. Open " + a.out + ".svg next to the source and compare them by eye.")
    print(f"{sum(len(l['parts']) for l in layers)} parts in {len(layers)} colour layers {[l['color'] for l in layers]} -> {a.out}.svg/.json"
          + (f", check: {a.out}_check.png" if src is not None else "") + f"; icon box {icon}")
