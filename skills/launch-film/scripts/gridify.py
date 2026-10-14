#!/usr/bin/env python3
"""Draw a labelled 50/100 px coordinate grid on an image to measure boxes.
usage: python3 gridify.py <image> <out.jpg>"""
import sys
from PIL import Image, ImageDraw, ImageFont
src, dst = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("RGB")
W, H = im.size
d = ImageDraw.Draw(im)
try:
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 18)
except Exception:
    font = ImageFont.load_default()
for x in range(0, W, 50):
    c = (255, 0, 0) if x % 100 == 0 else (255, 160, 160)
    d.line([(x, 0), (x, H)], fill=c, width=1 if x % 100 else 2)
    if x % 100 == 0:
        d.text((x + 2, 2), str(x), fill=(255, 255, 0), font=font)
for y in range(0, H, 50):
    c = (0, 120, 255) if y % 100 == 0 else (150, 190, 255)
    d.line([(0, y), (W, y)], fill=c, width=1 if y % 100 else 2)
    if y % 100 == 0:
        d.text((2, y + 2), str(y), fill=(0, 255, 255), font=font)
im.save(dst, quality=88)
print(W, H)
