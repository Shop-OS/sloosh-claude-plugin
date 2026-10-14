#!/usr/bin/env python3
"""Solve placements for an object-locked match cut between two images.

usage:
  python3 align_pair.py --a W,H,cx,cy,objw --b W,H,cx,cy,objw
                        [--flipA] [--flipB] [--target X,Y] [--screen 1920x1080] [--minscale 1.0]

A = outgoing image (e.g. source photo), B = incoming image (e.g. AI result). cx,cy,objw are
the measured object centre and width in each image's logical pixels (gridify.py). With
--flipA the A image is mirrored (cx becomes W - cx) — render it with `flip`.

Prints JSON placements {s, x, y} (screen = x + s * px) so the objects coincide at the
target point with equal width, and both images cover the whole frame. Default target is
where B's object sits when B is shown full-frame (cover-fit, centred).
"""
import argparse
import json


def parse(v):
    return [float(x) for x in v.split(",")]


def min_cover(W, H, cx, cy, tx, ty, SW, SH, floor):
    return max(
        floor,
        tx / cx if cx > 0 else 0,
        (SW - tx) / (W - cx) if W - cx > 0 else 0,
        ty / cy if cy > 0 else 0,
        (SH - ty) / (H - cy) if H - cy > 0 else 0,
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--flipA", action="store_true")
    ap.add_argument("--flipB", action="store_true")
    ap.add_argument("--target")
    ap.add_argument("--screen", default="1920x1080")
    ap.add_argument("--minscale", type=float, default=0.0)
    o = ap.parse_args()
    SW, SH = [float(x) for x in o.screen.split("x")]
    WA, HA, cxA, cyA, wA = parse(o.a)
    WB, HB, cxB, cyB, wB = parse(o.b)
    if o.flipA:
        cxA = WA - cxA
    if o.flipB:
        cxB = WB - cxB
    if o.target:
        tx, ty = parse(o.target)
    else:
        s0 = max(SW / WB, SH / HB)
        tx = (SW - WB * s0) / 2 + s0 * cxB
        ty = (SH - HB * s0) / 2 + s0 * cyB
    r = wB / wA  # sA = sB * r keeps object widths equal on screen
    minA = min_cover(WA, HA, cxA, cyA, tx, ty, SW, SH, o.minscale)
    minB = min_cover(WB, HB, cxB, cyB, tx, ty, SW, SH, o.minscale)
    sB = max(minB, minA / r)
    sA = sB * r
    out = {
        "target": {"x": round(tx, 1), "y": round(ty, 1)},
        "objectScreenWidth": round(sB * wB, 1),
        "A": {"s": round(sA, 4), "x": round(tx - sA * cxA, 1), "y": round(ty - sA * cyA, 1), "flip": o.flipA},
        "B": {"s": round(sB, 4), "x": round(tx - sB * cxB, 1), "y": round(ty - sB * cyB, 1), "flip": o.flipB},
        "note": "s > ~1.15 → use the 2x HD file for that image",
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
