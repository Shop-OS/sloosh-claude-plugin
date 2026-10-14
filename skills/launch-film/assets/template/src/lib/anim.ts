import { Easing, interpolate } from "remotion";

export type EasingFn = (t: number) => number;

// Curves used across the film. Camera moves use the quint/expo families so
// they read as deliberate "designed" moves; UI pops use a gentle back-out.
export const E = {
  linear: (t: number) => t,
  outExpo: Easing.bezier(0.16, 1, 0.3, 1),
  outQuart: Easing.bezier(0.25, 1, 0.5, 1),
  outCubic: Easing.bezier(0.33, 1, 0.68, 1),
  inOutCubic: Easing.bezier(0.65, 0, 0.35, 1),
  inOutQuart: Easing.bezier(0.76, 0, 0.24, 1),
  inOutQuint: Easing.bezier(0.83, 0, 0.17, 1),
  inOutExpo: Easing.bezier(0.87, 0, 0.13, 1),
  inExpo: Easing.bezier(0.7, 0, 0.84, 0),
  inCubic: Easing.bezier(0.32, 0, 0.67, 0),
  outBack: Easing.bezier(0.34, 1.36, 0.64, 1),
  outBackSoft: Easing.bezier(0.3, 1.18, 0.55, 1),
};

/** Clamped 0..1 progress between t0 and t1 (seconds or frames), eased. */
export const prog = (t: number, t0: number, t1: number, ease: EasingFn = E.linear) =>
  interpolate(t, [t0, t1], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: ease,
  });

/** Clamped multi-keyframe interpolation with a single easing per segment. */
export const kf = (t: number, times: number[], values: number[], ease: EasingFn = E.inOutCubic) =>
  interpolate(t, times, values, {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: ease,
  });

export const mix = (a: number, b: number, p: number) => a + (b - a) * p;

export const clamp01 = (v: number) => Math.max(0, Math.min(1, v));

/** Deterministic hash noise in [0,1). */
export const hash = (n: number) => {
  const s = Math.sin(n * 127.1 + 311.7) * 43758.5453123;
  return s - Math.floor(s);
};

/**
 * Piecewise camera path: an array of keys {t, ...values}. Each segment uses its
 * own easing so we can chain designed moves (push, hold, whip) seamlessly.
 */
export type Key<T extends string> = { t: number; e?: EasingFn } & Record<T, number>;

export const path = <T extends string>(t: number, keys: Key<T>[], field: T): number => {
  if (t <= keys[0].t) return keys[0][field];
  for (let i = 0; i < keys.length - 1; i++) {
    const a = keys[i];
    const b = keys[i + 1];
    if (t <= b.t) {
      const p = (t - a.t) / Math.max(1e-6, b.t - a.t);
      const ease = b.e ?? E.inOutCubic;
      return a[field] + (b[field] - a[field]) * ease(Math.max(0, Math.min(1, p)));
    }
  }
  return keys[keys.length - 1][field];
};

/** Speed of a path value (units per second), sampled numerically. */
export const pathSpeed = <T extends string>(t: number, keys: Key<T>[], fields: T[]) => {
  const dt = 1 / 120;
  let s = 0;
  for (const f of fields) {
    const v = (path(t + dt, keys, f) - path(t - dt, keys, f)) / (2 * dt);
    s = Math.max(s, Math.abs(v));
  }
  return s;
};
