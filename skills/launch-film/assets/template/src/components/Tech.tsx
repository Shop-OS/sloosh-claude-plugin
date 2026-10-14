import React from "react";
import { C, FONT } from "../theme";
import { clamp01, E, prog } from "../lib/anim";

/**
 * Editorial "construction" language from the botanical reference: hairline
 * guides, crosshairs, corner handles, tiny monospaced annotations and solid
 * accent squares at intersections. Re-coloured to the Sloosh palette.
 */

export const MonoLabel: React.FC<{
  text: string;
  /** 0..1 typewriter progress */
  p?: number;
  size?: number;
  color?: string;
  style?: React.CSSProperties;
  weight?: number;
  caret?: boolean;
}> = ({ text, p = 1, size = 13, color = C.text, style, weight = 500, caret = false }) => {
  const n = Math.round(text.length * clamp01(p));
  return (
    <div
      style={{
        fontFamily: FONT.mono,
        fontSize: size,
        fontWeight: weight,
        letterSpacing: "0.06em",
        color,
        whiteSpace: "pre",
        lineHeight: 1.25,
        textTransform: "uppercase",
        ...style,
      }}
    >
      {text.slice(0, n)}
      {caret && p < 1 ? <span style={{ opacity: 0.8 }}>▍</span> : null}
    </div>
  );
};

export const Tag: React.FC<{
  text: string;
  p?: number;
  bg?: string;
  color?: string;
  size?: number;
  style?: React.CSSProperties;
}> = ({ text, p = 1, bg = C.accent, color = C.ink, size = 13, style }) => {
  const s = E.outExpo(clamp01(p));
  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        background: bg,
        color,
        fontFamily: FONT.mono,
        fontWeight: 700,
        fontSize: size,
        letterSpacing: "0.06em",
        padding: `${size * 0.32}px ${size * 0.62}px`,
        textTransform: "uppercase",
        whiteSpace: "nowrap",
        clipPath: `inset(0 ${(1 - s) * 100}% 0 0)`,
        ...style,
      }}
    >
      {text}
    </div>
  );
};

export const Crosshair: React.FC<{
  x: number;
  y: number;
  size?: number;
  color?: string;
  p?: number;
  ring?: number;
  thickness?: number;
}> = ({ x, y, size = 22, color = C.accent, p = 1, ring = 0, thickness = 1.5 }) => {
  const s = E.outExpo(clamp01(p));
  return (
    <div style={{ position: "absolute", left: x, top: y, width: 0, height: 0, opacity: s > 0 ? 1 : 0 }}>
      <div
        style={{
          position: "absolute",
          left: (-size / 2) * s,
          top: -thickness / 2,
          width: size * s,
          height: thickness,
          background: color,
        }}
      />
      <div
        style={{
          position: "absolute",
          top: (-size / 2) * s,
          left: -thickness / 2,
          height: size * s,
          width: thickness,
          background: color,
        }}
      />
      {ring > 0 ? (
        <div
          style={{
            position: "absolute",
            left: -ring * s,
            top: -ring * s,
            width: ring * 2 * s,
            height: ring * 2 * s,
            borderRadius: "50%",
            border: `${thickness}px solid ${color}`,
          }}
        />
      ) : null}
    </div>
  );
};

/** Bounding box with square corner handles, drawn in from its corners. */
export const BBox: React.FC<{
  x: number;
  y: number;
  w: number;
  h: number;
  p?: number;
  color?: string;
  handle?: number;
  handleFill?: string;
  thickness?: number;
  label?: string;
  labelP?: number;
  labelPos?: "top" | "bottom";
  tagBg?: string;
  tagColor?: string;
  labelSize?: number;
  dashed?: boolean;
  style?: React.CSSProperties;
}> = ({
  x,
  y,
  w,
  h,
  p = 1,
  color = C.accent,
  handle = 9,
  handleFill = C.white,
  thickness = 1.5,
  label,
  labelP,
  labelPos = "top",
  tagBg,
  tagColor,
  labelSize = 13,
  dashed = false,
  style,
}) => {
  const lp = E.outExpo(clamp01(p));
  const hp = prog(p, 0.45, 1, E.outBack);
  const border = dashed ? "dashed" : "solid";
  const corners = [
    [0, 0],
    [1, 0],
    [0, 1],
    [1, 1],
  ];
  return (
    <div style={{ position: "absolute", left: x, top: y, width: w, height: h, ...style }}>
      {/* top / bottom edges grow from the left corners, sides from the top */}
      <div style={{ position: "absolute", left: 0, top: 0, width: w * lp, borderTop: `${thickness}px ${border} ${color}` }} />
      <div
        style={{
          position: "absolute",
          right: 0,
          bottom: 0,
          width: w * lp,
          borderTop: `${thickness}px ${border} ${color}`,
          transform: `translateY(${thickness / 2}px)`,
        }}
      />
      <div style={{ position: "absolute", left: 0, top: 0, height: h * lp, borderLeft: `${thickness}px ${border} ${color}` }} />
      <div
        style={{
          position: "absolute",
          right: 0,
          bottom: 0,
          height: h * lp,
          borderLeft: `${thickness}px ${border} ${color}`,
          transform: `translateX(${thickness / 2}px)`,
        }}
      />
      {corners.map(([cx, cy], i) => (
        <div
          key={i}
          style={{
            position: "absolute",
            left: cx * w - handle / 2,
            top: cy * h - handle / 2,
            width: handle,
            height: handle,
            background: handleFill,
            border: `${thickness}px solid ${color}`,
            boxSizing: "border-box",
            transform: `scale(${hp})`,
          }}
        />
      ))}
      {label ? (
        <div
          style={{
            position: "absolute",
            left: -thickness / 2,
            ...(labelPos === "top" ? { bottom: h + handle * 0.9 } : { top: h + handle * 0.9 }),
          }}
        >
          <Tag
            text={label}
            p={labelP ?? prog(p, 0.3, 1)}
            bg={tagBg ?? color}
            color={tagColor ?? C.ink}
            size={labelSize}
          />
        </div>
      ) : null}
    </div>
  );
};

/** Full-bleed hairline guides that draw outward from an origin. */
export const Guides: React.FC<{
  xs?: number[];
  ys?: number[];
  p?: number;
  origin?: { x: number; y: number };
  color?: string;
  width?: number;
  height?: number;
  thickness?: number;
  squares?: boolean;
  squareColor?: string;
  squareSize?: number;
  squareP?: number;
}> = ({
  xs = [],
  ys = [],
  p = 1,
  origin = { x: 960, y: 540 },
  color = C.paperLine,
  width = 1920,
  height = 1080,
  thickness = 1,
  squares = false,
  squareColor = C.accent,
  squareSize = 10,
  squareP = 1,
}) => {
  const s = E.inOutCubic(clamp01(p));
  const sq = E.outBack(clamp01(squareP));
  return (
    <div style={{ position: "absolute", inset: 0, pointerEvents: "none" }}>
      {xs.map((x) => {
        const top = origin.y - origin.y * s;
        const bottom = origin.y + (height - origin.y) * s;
        return (
          <div
            key={`x${x}`}
            style={{ position: "absolute", left: x - thickness / 2, top, height: bottom - top, width: thickness, background: color }}
          />
        );
      })}
      {ys.map((y) => {
        const left = origin.x - origin.x * s;
        const right = origin.x + (width - origin.x) * s;
        return (
          <div
            key={`y${y}`}
            style={{ position: "absolute", top: y - thickness / 2, left, width: right - left, height: thickness, background: color }}
          />
        );
      })}
      {squares
        ? xs.flatMap((x) =>
            ys.map((y) => (
              <div
                key={`s${x}-${y}`}
                style={{
                  position: "absolute",
                  left: x - squareSize / 2,
                  top: y - squareSize / 2,
                  width: squareSize,
                  height: squareSize,
                  background: squareColor,
                  transform: `scale(${sq})`,
                }}
              />
            )),
          )
        : null}
    </div>
  );
};

/** Dotted connector (curved) drawn with stroke-dashoffset. */
export const Connector: React.FC<{
  d: string;
  p?: number;
  color?: string;
  width?: number;
  dashed?: boolean;
  length?: number;
  style?: React.CSSProperties;
  w?: number;
  h?: number;
}> = ({ d, p = 1, color = C.accent, width = 1.5, dashed = false, length = 2400, style, w = 1920, h = 1080 }) => {
  const s = clamp01(p);
  return (
    <svg width={w} height={h} style={{ position: "absolute", left: 0, top: 0, overflow: "visible", ...style }}>
      <path
        d={d}
        fill="none"
        stroke={color}
        strokeWidth={width}
        strokeLinecap="round"
        strokeDasharray={dashed ? "2 7" : `${length} ${length}`}
        strokeDashoffset={dashed ? 0 : length * (1 - s)}
        style={dashed ? { clipPath: `inset(0 ${(1 - s) * 100}% 0 0)` } : undefined}
      />
    </svg>
  );
};

/** Measurement ruler ticks along a line. */
export const Ruler: React.FC<{
  x: number;
  y: number;
  length: number;
  vertical?: boolean;
  p?: number;
  color?: string;
  step?: number;
}> = ({ x, y, length, vertical = false, p = 1, color = C.paperLine, step = 12 }) => {
  const n = Math.floor(length / step);
  const s = clamp01(p);
  return (
    <div style={{ position: "absolute", left: x, top: y }}>
      {new Array(n + 1).fill(0).map((_, i) => {
        if (i / n > s) return null;
        const big = i % 5 === 0;
        const len = big ? 10 : 5;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              background: color,
              ...(vertical
                ? { top: i * step, left: 0, width: len, height: 1 }
                : { left: i * step, top: 0, width: 1, height: len }),
            }}
          />
        );
      })}
    </div>
  );
};
