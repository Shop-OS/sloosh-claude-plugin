// Crop camera: drive photo shots with a "view rectangle" in image pixels so that
// overlays pinned to image features stay put, and so two aligned images can share one
// camera across an object-locked match cut.

export type Rect = { x: number; y: number; w: number; h: number };
/** Image placement in frame space: screen = x + s * imagePx */
export type Placement = { s: number; x: number; y: number };

export const SW = 1920;
export const SH = 1080;

/** View rect (image px) for a zoom k around a screen point (cx, cy) under a placement. */
export const viewOf = (pl: Placement, k: number, cx: number, cy: number, w = SW, h = SH): Rect => {
  const X0 = cx + (0 - cx) / k;
  const Y0 = cy + (0 - cy) / k;
  return { x: (X0 - pl.x) / pl.s, y: (Y0 - pl.y) / pl.s, w: w / k / pl.s, h: h / k / pl.s };
};

/** The same screen region expressed in another image's pixels. */
export const mapView = (view: Rect, from: Placement, to: Placement): Rect => ({
  x: (view.x * from.s + from.x - to.x) / to.s,
  y: (view.y * from.s + from.y - to.y) / to.s,
  w: (view.w * from.s) / to.s,
  h: (view.h * from.s) / to.s,
});

/** Image point → screen point for a view rect rendered full-frame. */
export const toScreen = (view: Rect, px: number, py: number, w = SW, h = SH) => ({
  x: ((px - view.x) / view.w) * w,
  y: ((py - view.y) / view.h) * h,
  s: w / view.w,
});

/** Image rect → screen rect for a view rect rendered full-frame. */
export const rectToScreen = (view: Rect, r: Rect, w = SW, h = SH): Rect => {
  const a = toScreen(view, r.x, r.y, w, h);
  const b = toScreen(view, r.x + r.w, r.y + r.h, w, h);
  return { x: a.x, y: a.y, w: b.x - a.x, h: b.y - a.y };
};

export const lerpRect = (a: Rect, b: Rect, p: number): Rect => ({
  x: a.x + (b.x - a.x) * p,
  y: a.y + (b.y - a.y) * p,
  w: a.w + (b.w - a.w) * p,
  h: a.h + (b.h - a.h) * p,
});

/** Full-frame view of an image under a placement. */
export const fullView = (pl: Placement, w = SW, h = SH): Rect => ({ x: -pl.x / pl.s, y: -pl.y / pl.s, w: w / pl.s, h: h / pl.s });

/**
 * Two images aligned on a shared object (values from scripts/align_pair.py).
 * Use `pair.view(k)` for image A and `pair.viewB(k)` for image B with the same k.
 */
export const makePair = (a: Placement, b: Placement, focus: { x: number; y: number }) => ({
  a,
  b,
  focus,
  view: (k: number) => viewOf(a, k, focus.x, focus.y),
  viewB: (k: number) => mapView(viewOf(a, k, focus.x, focus.y), a, b),
});
