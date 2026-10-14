// Shared "crop camera" for the cake sequence. The source (I10) and result (I17)
// photos are aligned so the cake body occupies the same screen rectangle:
//   I10 shown at scale 1.2306, offset (-58, -61)
//   I17 shown at scale 1.1483, offset (0, 0)
// A view rectangle (in I10 logical pixels) therefore maps to an I17 rectangle.

export type Rect = { x: number; y: number; w: number; h: number };

const S10 = 1.2306;
const O10 = { x: -58, y: -61 };
const S17 = 1.1483;

/** The full-frame view of I10 at the aligned transform. */
export const FULL10: Rect = { x: -O10.x / S10, y: -O10.y / S10, w: 1920 / S10, h: 1080 / S10 };

/** View rect for a camera zoom k around screen point (cx, cy) (aligned frame space). */
export const viewForZoom = (k: number, cx: number, cy: number): Rect => {
  const X0 = cx + (0 - cx) / k;
  const Y0 = cy + (0 - cy) / k;
  return {
    x: (X0 - O10.x) / S10,
    y: (Y0 - O10.y) / S10,
    w: 1920 / k / S10,
    h: 1080 / k / S10,
  };
};

export const to17 = (r: Rect): Rect => ({
  x: (r.x * S10 + O10.x) / S17,
  y: (r.y * S10 + O10.y) / S17,
  w: (r.w * S10) / S17,
  h: (r.h * S10) / S17,
});

/** I10 point -> screen, for a given view rect. */
export const toScreen = (r: Rect, px: number, py: number) => ({
  x: ((px - r.x) / r.w) * 1920,
  y: ((py - r.y) / r.h) * 1080,
  s: 1920 / r.w,
});

export const lerpRect = (a: Rect, b: Rect, p: number): Rect => ({
  x: a.x + (b.x - a.x) * p,
  y: a.y + (b.y - a.y) * p,
  w: a.w + (b.w - a.w) * p,
  h: a.h + (b.h - a.h) * p,
});

// Cake centre in aligned frame space (I17 at 1.1483).
export const CAKE_SCREEN = { x: 1169 * 1.1483, y: 665 * 1.1483 };
