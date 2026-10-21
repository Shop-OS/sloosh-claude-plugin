#!/usr/bin/env python3
"""palette_from_photo.py: derive the film's world palette from the REAL product photo (so the world matches the product).

Usage:  python3 <skill>/scripts/palette_from_photo.py product.jpg [--cutout plates/product_cut.png]
Prints JSON + CSS tokens:
  product_hex   dominant colour of the product (alpha-weighted if a cutout is given)
  accent_hex    most saturated frequent colour (logo / cap / LED) -> the ONE accent
  hue_dark / hue_mid / hue_lit   a monochrome world built from the dominant hue (Splash/Levitation brand-colour world)
  base / lit    Dark Luxury base (near-black tinted 3% toward the product) and end-card glow
Deterministic (Pillow median-cut quantize). Needs Python 3.9+, Pillow and numpy.
"""
import colorsys, json, sys
import numpy as np
from PIL import Image

def hx(rgb): return "#%02X%02X%02X" % tuple(int(max(0, min(255, round(c)))) for c in rgb)
def hls(h, l, s): return [c * 255 for c in colorsys.hls_to_rgb(h, l, s)]

def main():
    if len(sys.argv) < 2 or sys.argv[1].startswith("--"):
        sys.exit(__doc__)
    src = sys.argv[1]
    if "--cutout" in sys.argv and sys.argv.index("--cutout") + 1 >= len(sys.argv):
        sys.exit("palette_from_photo.py: --cutout needs a PNG path")
    cut = sys.argv[sys.argv.index("--cutout") + 1] if "--cutout" in sys.argv else None
    im = Image.open(cut or src).convert("RGBA"); im.thumbnail((400, 400))
    a = np.array(im); rgb = a[..., :3].reshape(-1, 3); al = a[..., 3].reshape(-1)
    keep = rgb[al > 200] if cut else rgb
    if not cut:  # drop near-white / near-black studio background pixels
        lum = keep.mean(1); keep = keep[(lum > 18) & (lum < 240)]
    if len(keep) < 16:
        sys.exit("palette_from_photo.py: too few product pixels to sample (an empty cutout, or a photo that is all white "
                 "or all black). Check the cutout, or pass the photo without --cutout.")
    mc = getattr(getattr(Image, "Quantize", Image), "MEDIANCUT", 0)          # Pillow < 9.1 has Image.MEDIANCUT only
    q = Image.fromarray(keep.reshape(-1, 1, 3).astype(np.uint8)).quantize(colors=8, method=mc)
    raw = list(q.getpalette() or [])[:24]; raw += [0] * (24 - len(raw))      # a short palette is padded to 8 colours
    pal = np.array(raw, np.float64).reshape(8, 3); counts = np.bincount(np.array(q).reshape(-1), minlength=8)[:8]
    # group the 8 clusters into hue families (30 deg buckets; low-saturation = one neutral family), so several shades of
    # one body colour beat a single flat label colour; dominant = count-weighted mean of the largest family
    H = [colorsys.rgb_to_hls(*(c / 255)) for c in pal]
    fam = [("n" if (hh[2] < 0.15 or hh[1] < 0.08 or hh[1] > 0.92) else int(hh[0] * 12) % 12) for hh in H]
    tot = {}
    for i, f in enumerate(fam):
        tot[f] = tot.get(f, 0) + counts[i]
    best = max(tot, key=tot.get); idx = [i for i, f in enumerate(fam) if f == best]
    dom = (pal[idx] * counts[idx, None]).sum(0) / max(1, counts[idx].sum())
    def sat(c): return colorsys.rgb_to_hls(*(c / 255))[2]
    cand = [pal[i] for i in range(8) if counts[i] > 0.02 * counts.sum() and fam[i] != best and fam[i] != "n"]
    acc = max(cand, key=lambda c: sat(c) * (0.4 + colorsys.rgb_to_hls(*(c / 255))[1])) if cand else \
          max([pal[i] for i in range(8) if counts[i] > 0], key=lambda c: sat(c))
    h, l, s = colorsys.rgb_to_hls(*(dom / 255)); s2 = max(s, 0.45)
    out = {"product_hex": hx(dom), "accent_hex": hx(acc),
           "hue_dark": hx(hls(h, 0.07, s2)), "hue_mid": hx(hls(h, 0.24, s2)), "hue_lit": hx(hls(h, 0.42, min(1, s2 + 0.1))),
           "base": hx(np.array([5, 5, 5]) * 0.97 + dom * 0.03), "lit": hx(hls(h, 0.14, min(s, 0.25)))}
    print(json.dumps(out, indent=1))
    print("# paste into tl.py (ACCENT = the ONE accent, taken from the product itself):")
    acc_hex, base_hex, lit_hex = out["accent_hex"], out["base"], out["lit"]
    print('ACCENT, RULE = "{0}", "{0}"'.format(acc_hex))
    print('BASE, LIT = "{}", "{}"'.format(base_hex, lit_hex))
    print(f"# Splash / Levitation world: hue_dark {out['hue_dark']}, hue_mid {out['hue_mid']}, hue_lit {out['hue_lit']}")

if __name__ == "__main__":
    main()
