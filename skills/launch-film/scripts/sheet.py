#!/usr/bin/env python3
"""Contact sheet from a rendered JPEG sequence (Remotion --sequence output).

usage: python3 sheet.py <seq_dir> <out.jpg> "f1,f2,f3,…" [cols=4] [tile_width=480]
Frames are film frame numbers; files are element-NNN.jpeg (3 or 4 digit padding).
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

d, out, frames = sys.argv[1], sys.argv[2], [int(x) for x in sys.argv[3].split(",") if x.strip()]
cols = int(sys.argv[4]) if len(sys.argv) > 4 else 4
w = int(sys.argv[5]) if len(sys.argv) > 5 else 480
h = int(w * 9 / 16)
rows = (len(frames) + cols - 1) // cols
sheet = Image.new("RGB", (cols * (w + 4), rows * (h + 4)), (255, 255, 255))
try:
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 18)
except Exception:
    font = ImageFont.load_default()
for i, fr in enumerate(frames):
    p = None
    for pad in (3, 4, 5):
        cand = os.path.join(d, f"element-{fr:0{pad}d}.jpeg")
        if os.path.exists(cand):
            p = cand
            break
    if p is None:
        continue
    im = Image.open(p).convert("RGB").resize((w, h), Image.LANCZOS)
    dr = ImageDraw.Draw(im)
    dr.rectangle([0, 0, 64, 24], fill=(0, 0, 0))
    dr.text((4, 2), f"f{fr}", fill=(255, 255, 0), font=font)
    sheet.paste(im, ((i % cols) * (w + 4), (i // cols) * (h + 4)))
sheet.save(out, quality=88)
print(out)
