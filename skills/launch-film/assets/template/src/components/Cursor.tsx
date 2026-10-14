import React from "react";
import { clamp01, E, prog } from "../lib/anim";

/** macOS-style pointer. `press` 0..1 shrinks it; `ripple` 0..1 draws a click ring. */
export const Cursor: React.FC<{
  x: number;
  y: number;
  size?: number;
  press?: number;
  ripple?: number;
  rippleColor?: string;
  opacity?: number;
}> = ({ x, y, size = 34, press = 0, ripple = -1, rippleColor = "#FECC15", opacity = 1 }) => {
  const s = 1 - 0.16 * clamp01(press);
  const r = ripple >= 0 && ripple <= 1 ? ripple : -1;
  return (
    <div style={{ position: "absolute", left: x, top: y, width: 0, height: 0, opacity, pointerEvents: "none" }}>
      {r >= 0 ? (
        <div
          style={{
            position: "absolute",
            left: -size * 1.3 * E.outCubic(r),
            top: -size * 1.3 * E.outCubic(r),
            width: size * 2.6 * E.outCubic(r),
            height: size * 2.6 * E.outCubic(r),
            borderRadius: "50%",
            border: `3px solid ${rippleColor}`,
            opacity: 1 - prog(r, 0.2, 1),
          }}
        />
      ) : null}
      <svg
        width={size}
        height={size * 1.32}
        viewBox="0 0 24 32"
        style={{
          position: "absolute",
          left: -size * 0.12,
          top: -size * 0.06,
          transform: `scale(${s})`,
          transformOrigin: "10% 6%",
          filter: "drop-shadow(0 6px 10px rgba(0,0,0,0.45))",
          overflow: "visible",
        }}
      >
        <path
          d="M2.2 1.6 L2.2 25.4 L8.1 19.8 L11.9 28.6 L15.6 27.0 L11.9 18.4 L19.9 18.4 Z"
          fill="#FFFFFF"
          stroke="#0A0A0A"
          strokeWidth="1.7"
          strokeLinejoin="round"
        />
      </svg>
    </div>
  );
};

/** Cubic bezier point (for curved cursor paths). */
export const bez = (
  t: number,
  p0: [number, number],
  p1: [number, number],
  p2: [number, number],
  p3: [number, number],
): [number, number] => {
  const u = 1 - t;
  const a = u * u * u;
  const b = 3 * u * u * t;
  const c = 3 * u * t * t;
  const d = t * t * t;
  return [a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]];
};
