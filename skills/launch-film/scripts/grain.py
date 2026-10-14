#!/usr/bin/env python3
"""Generate 8 film-grain plates (960x540 mid-grey noise) for <Grain>.
usage: python3 grain.py <out_dir>"""
import numpy as np
from PIL import Image, ImageFilter
import sys
out = sys.argv[1]
rng = np.random.default_rng(7)
for i in range(8):
    n = rng.normal(0, 1, (540, 960)).astype(np.float32)
    img = Image.fromarray(np.clip(128 + n * 38, 0, 255).astype(np.uint8), "L")
    img = img.filter(ImageFilter.GaussianBlur(0.55))
    img.save(f"{out}/grain_{i}.png", optimize=True)
print("ok")
