import React, { useMemo } from "react";
import { AbsoluteFill } from "remotion";
import { clamp01, hash } from "../lib/anim";

let fxId = 0;

/**
 * Brief RGB channel displacement for selected match cuts (≤ 2 frames,
 * per the production guide). `amount` is in pixels; 0 renders children as-is.
 */
export const ChromaSplit: React.FC<{ amount: number; children: React.ReactNode; angle?: number }> = ({
  amount,
  children,
  angle = 0,
}) => {
  const id = useMemo(() => `rgb${fxId++}`, []);
  if (Math.abs(amount) < 0.25) return <AbsoluteFill>{children}</AbsoluteFill>;
  const dx = Math.cos(angle) * amount;
  const dy = Math.sin(angle) * amount;
  return (
    <AbsoluteFill>
      <svg width="0" height="0" style={{ position: "absolute" }}>
        <filter id={id} x="-5%" y="-5%" width="110%" height="110%" colorInterpolationFilters="sRGB">
          <feColorMatrix in="SourceGraphic" type="matrix" values="1 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0" result="r" />
          <feOffset in="r" dx={dx} dy={dy} result="ro" />
          <feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0  0 1 0 0 0  0 0 0 0 0  0 0 0 1 0" result="g" />
          <feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 1 0 0  0 0 0 1 0" result="b" />
          <feOffset in="b" dx={-dx} dy={-dy} result="bo" />
          <feBlend in="ro" in2="g" mode="screen" result="rg" />
          <feBlend in="rg" in2="bo" mode="screen" />
        </filter>
      </svg>
      <AbsoluteFill style={{ filter: `url(#${id})` }}>{children}</AbsoluteFill>
    </AbsoluteFill>
  );
};

/**
 * Stepped pixel-block wipe (the block-mosaic transition from the reference),
 * rendered as an overlay of squares. `mode="cover"` fills towards `color`,
 * `mode="reveal"` starts filled and opens up.
 */
export const PixelWipe: React.FC<{
  p: number;
  color: string;
  cell?: number;
  mode?: "cover" | "reveal";
  dir?: { x: number; y: number };
  seed?: number;
  softness?: number;
  accent?: string;
  accentRatio?: number;
}> = ({ p, color, cell = 60, mode = "cover", dir = { x: 1, y: 0.25 }, seed = 1, softness = 0.55, accent, accentRatio = 0.12 }) => {
  const cols = Math.ceil(1920 / cell);
  const rows = Math.ceil(1080 / cell);
  const pp = clamp01(p);
  if (mode === "cover" && pp <= 0) return null;
  if (mode === "reveal" && pp >= 1) return null;
  const len = Math.hypot(dir.x, dir.y) || 1;
  const nx = dir.x / len;
  const ny = dir.y / len;
  const cells: React.ReactNode[] = [];
  for (let j = 0; j < rows; j++) {
    for (let i = 0; i < cols; i++) {
      // directional ramp + per-cell noise -> blocky stepped front
      const u = (i / cols) * nx + (j / rows) * ny;
      const base = (u - Math.min(0, nx) - Math.min(0, ny)) / (Math.abs(nx) + Math.abs(ny));
      const th = base * (1 - softness) + hash(i * 31.7 + j * 7.3 + seed * 13.1) * softness;
      const on = mode === "cover" ? pp > th : pp < th;
      if (!on) continue;
      const isAccent = accent && pp < 0.82 ? hash(i * 3.1 + j * 17.9 + seed) < accentRatio : false;
      cells.push(
        <div
          key={`${i}-${j}`}
          style={{
            position: "absolute",
            left: i * cell,
            top: j * cell,
            width: cell + 1,
            height: cell + 1,
            background: isAccent ? accent : color,
          }}
        />,
      );
    }
  }
  return <AbsoluteFill style={{ pointerEvents: "none" }}>{cells}</AbsoluteFill>;
};

/** Soft depth-of-field bands (tilt-shift) for 3D flyovers. */
export const TiltShift: React.FC<{ top?: number; bottom?: number; blur?: number }> = ({
  top = 0.34,
  bottom = 0.22,
  blur = 10,
}) => (
  <AbsoluteFill style={{ pointerEvents: "none" }}>
    {top > 0 ? (
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: 0,
          height: `${top * 100}%`,
          backdropFilter: `blur(${blur}px)`,
          WebkitMaskImage: "linear-gradient(to bottom, black 0%, black 25%, transparent 100%)",
          maskImage: "linear-gradient(to bottom, black 0%, black 25%, transparent 100%)",
        }}
      />
    ) : null}
    {bottom > 0 ? (
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          bottom: 0,
          height: `${bottom * 100}%`,
          backdropFilter: `blur(${blur}px)`,
          WebkitMaskImage: "linear-gradient(to top, black 0%, black 20%, transparent 100%)",
          maskImage: "linear-gradient(to top, black 0%, black 20%, transparent 100%)",
        }}
      />
    ) : null}
  </AbsoluteFill>
);
