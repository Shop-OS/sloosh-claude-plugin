import React from "react";
import { C, FONT } from "../theme";
import { clamp01 } from "../lib/anim";

/** An SVG path drawn on with pathLength=1 dash offsets (p: 0..1). Put inside an <svg>. */
export const Stroke: React.FC<{ d: string; p: number; w?: number; color?: string; opacity?: number }> = ({
  d,
  p,
  w = 7,
  color = C.accent,
  opacity = 1,
}) => (
  <path
    d={d}
    pathLength={1}
    fill="none"
    stroke={color}
    strokeWidth={w}
    strokeLinecap="round"
    strokeLinejoin="round"
    strokeDasharray="1 1"
    strokeDashoffset={1 - clamp01(p)}
    opacity={opacity}
  />
);

/** Four-point sparkle; scale s (0 hides it). Put inside an <svg>. */
export const Sparkle: React.FC<{ x: number; y: number; s: number; color?: string }> = ({ x, y, s, color = C.white }) =>
  s <= 0.001 ? null : (
    <path
      transform={`translate(${x} ${y}) scale(${s})`}
      d="M0 -20 C 3 -5 5 -3 20 0 C 5 3 3 5 0 20 C -3 5 -5 3 -20 0 C -5 -3 -3 -5 0 -20 Z"
      fill={color}
    />
  );

/** Handwritten line revealed left-to-right (p: 0..1). */
export const Handwriting: React.FC<{
  children: React.ReactNode;
  p: number;
  size?: number;
  color?: string;
  rotate?: number;
  style?: React.CSSProperties;
}> = ({ children, p, size = 92, color = C.white, rotate = -2, style }) => (
  <div
    style={{
      fontFamily: FONT.script,
      fontWeight: 700,
      fontSize: size,
      color,
      clipPath: `inset(-20% ${(1 - clamp01(p)) * 100}% -20% 0)`,
      transform: `rotate(${rotate}deg)`,
      whiteSpace: "nowrap",
      ...style,
    }}
  >
    {children}
  </div>
);

/**
 * Doodle of a cake on a crescent moon (the "idea" sketch). Local coordinates ~700×480;
 * position it with a <g transform>. Each part has its own progress so it draws in order.
 * Cake body spans x 112–486, y 190–432 in local units — use that box to fit the sketch
 * over a real photo for a sketch-to-photo reveal.
 */
export const CAKE_SKETCH_BOX = { x: 112, y: 190, w: 374, h: 242 };
export const CakeMoonSketch: React.FC<{
  moon: number;
  top: number;
  body: number;
  plate: number;
  piping: number;
  berries: number[];
  stars: number[];
  color?: string;
  stroke?: number;
}> = ({ moon, top, body, plate, piping, berries, stars, color = C.accent, stroke = 7 }) => (
  <>
    <Stroke d="M560 30 C 500 40 470 100 488 156 C 506 210 566 236 618 220 C 572 206 540 168 538 120 C 536 78 552 48 560 30 Z" p={moon} color={color} w={stroke} />
    <Stroke d="M112 238 C 112 206 210 190 300 190 C 392 190 486 206 486 236 C 486 266 392 282 300 282 C 208 282 112 268 112 238 Z" p={top} color={color} w={stroke} />
    <Stroke d="M112 240 L 116 380 C 120 414 214 432 300 432 C 390 432 480 416 484 382 L 486 238" p={body} color={color} w={stroke} />
    <Stroke d="M70 392 C 60 440 200 470 300 470 C 410 470 548 444 530 394" p={plate} color={color} w={stroke - 1} />
    <Stroke
      d="M120 250 q 12 16 24 0 q 12 16 24 0 q 12 16 24 0 q 12 16 24 0 q 12 16 24 0 q 12 16 24 0 q 12 16 24 0 q 12 16 24 0 q 12 16 24 0 q 12 16 24 0 q 12 16 24 0 q 12 16 24 0 q 12 16 24 0 q 12 16 24 0 q 12 16 24 0"
      p={piping}
      color={color}
      w={stroke - 2}
    />
    {[
      { x: 232, y: 208, r: -12, k: 1 },
      { x: 300, y: 196, r: 4, k: 1.1 },
      { x: 370, y: 210, r: 14, k: 1 },
    ].map((b, i) => (
      <g key={i} transform={`translate(${b.x} ${b.y}) rotate(${b.r}) scale(${(berries[i] ?? 0) * b.k})`}>
        <path d="M0 -26 C 20 -26 26 -6 14 12 C 8 22 2 28 0 30 C -2 28 -8 22 -14 12 C -26 -6 -20 -26 0 -26 Z" fill={color} />
        <path d="M-10 -26 L0 -36 L10 -26 M0 -36 L0 -28" stroke={C.ink} strokeWidth={3} fill="none" strokeLinecap="round" />
      </g>
    ))}
    <Sparkle x={640} y={120} s={(stars[0] ?? 0) * 0.9} />
    <Sparkle x={430} y={20} s={(stars[1] ?? 0) * 0.6} />
    <Sparkle x={36} y={120} s={(stars[2] ?? 0) * 0.75} />
  </>
);
