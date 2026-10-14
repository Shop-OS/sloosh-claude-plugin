import React, { useMemo } from "react";
import { C } from "../theme";
import { LOGO_PATHS, LOGO_VIEWBOX, PUPIL_L, PUPIL_R } from "./logoPaths";

export type LogoVariant = "gradient" | "ink" | "white";

const LOOK_RANGE_X = 72;
const LOOK_RANGE_Y = 118;
// Eye centres chosen so that look = {x: 1, y: 0} reproduces the supplied logo exactly.
const EYE_L_C = { x: PUPIL_L.cx - LOOK_RANGE_X, y: PUPIL_L.cy };
const EYE_R_C = { x: PUPIL_R.cx - LOOK_RANGE_X, y: PUPIL_R.cy };

const LETTERS = [
  { key: "S1", box: { x: 0, y: 0, w: 270, h: 714 } },
  { key: "L", box: { x: 280, y: 0, w: 206, h: 714 } },
  { key: "OO", box: { x: 458, y: 0, w: 612, h: 714 } },
  { key: "S2", box: { x: 1060, y: 0, w: 258, h: 714 } },
  { key: "H", box: { x: 1328, y: 0, w: 276, h: 714 } },
] as const;

let uid = 0;

export const Logo: React.FC<{
  width: number;
  variant?: LogoVariant;
  /** Per-letter reveal 0..1 (S, L, OO, S, H). Letters rise out of their own masks. */
  reveal?: number[];
  /** 0 = closed, 1 = open */
  eyeOpen?: number;
  /** x: -1 (left) .. 1 (right, as in the supplied logo); y: -1 (up) .. 1 (down) */
  look?: { x: number; y: number };
  /** Fill of the eye sockets (ring around the eye whites). */
  socket?: string;
  /** Pupil colour. */
  pupil?: string;
  style?: React.CSSProperties;
}> = ({
  width,
  variant = "gradient",
  reveal = [1, 1, 1, 1, 1],
  eyeOpen = 1,
  look = { x: 1, y: 0 },
  socket = C.ink,
  pupil = C.ink,
  style,
}) => {
  const id = useMemo(() => `logo${uid++}`, []);
  const height = (width * LOGO_VIEWBOX.h) / LOGO_VIEWBOX.w;
  const fill =
    variant === "gradient" ? `url(#${id}-g)` : variant === "ink" ? C.ink : C.white;
  const eyeFill = variant === "white" ? C.white : C.white;
  const pupilFill = pupil;
  const lx = look.x * LOOK_RANGE_X;
  const ly = look.y * LOOK_RANGE_Y;
  const open = Math.max(0.001, eyeOpen);

  const eye = (side: "L" | "R") => {
    const c = side === "L" ? EYE_L_C : EYE_R_C;
    const p = side === "L" ? PUPIL_L : PUPIL_R;
    const d = side === "L" ? LOGO_PATHS.EYE_L : LOGO_PATHS.EYE_R;
    const hole = side === "L" ? LOGO_PATHS.OO_INNER_L : LOGO_PATHS.OO_INNER_R;
    return (
      <g transform={`translate(0 ${c.y}) scale(1 ${open}) translate(0 ${-c.y})`}>
        <path d={hole} fill={socket} />
        <path d={d} fill={eyeFill} />
        <g clipPath={`url(#${id}-clip${side})`}>
          <circle cx={c.x + lx} cy={c.y + ly} r={p.r} fill={pupilFill} />
        </g>
      </g>
    );
  };

  return (
    <svg
      width={width}
      height={height}
      viewBox={`0 0 ${LOGO_VIEWBOX.w} ${LOGO_VIEWBOX.h}`}
      style={{ overflow: "visible", display: "block", ...style }}
    >
      <defs>
        <linearGradient id={`${id}-g`} x1="0" y1="0" x2="0" y2="714" gradientUnits="userSpaceOnUse">
          <stop stopColor={C.yellowTop} />
          <stop offset="1" stopColor={C.yellowBottom} />
        </linearGradient>
        <clipPath id={`${id}-clipL`}>
          <path d={LOGO_PATHS.EYE_L} />
        </clipPath>
        <clipPath id={`${id}-clipR`}>
          <path d={LOGO_PATHS.EYE_R} />
        </clipPath>
        {LETTERS.map((l) => (
          <clipPath id={`${id}-m-${l.key}`} key={l.key}>
            <rect x={l.box.x - 4} y={-40} width={l.box.w + 8} height={l.box.h + 80} />
          </clipPath>
        ))}
      </defs>
      {LETTERS.map((l, i) => {
        const r = reveal[i] ?? 1;
        const dy = (1 - r) * (l.box.h + 60);
        return (
          <g key={l.key} clipPath={`url(#${id}-m-${l.key})`}>
            <g transform={`translate(0 ${dy})`}>
              {l.key === "OO" ? (
                <>
                  <path d={LOGO_PATHS.OO} fill={fill} />
                  {eye("L")}
                  {eye("R")}
                </>
              ) : (
                <path d={LOGO_PATHS[l.key]} fill={fill} />
              )}
            </g>
          </g>
        );
      })}
    </svg>
  );
};

/** The two eyes alone (Spacelab mascot), cropped from the wordmark geometry. */
export const Eyes: React.FC<{
  width: number;
  eyeOpen?: number;
  look?: { x: number; y: number };
  white?: string;
  pupil?: string;
  style?: React.CSSProperties;
}> = ({ width, eyeOpen = 1, look = { x: 1, y: 0 }, white = C.white, pupil = C.ink, style }) => {
  const id = useMemo(() => `eyes${uid++}`, []);
  const vb = { x: 476, y: 18, w: 572, h: 436 };
  const height = (width * vb.h) / vb.w;
  const lx = look.x * LOOK_RANGE_X;
  const ly = look.y * LOOK_RANGE_Y;
  const open = Math.max(0.04, eyeOpen);
  const one = (side: "L" | "R") => {
    const c = side === "L" ? EYE_L_C : EYE_R_C;
    const p = side === "L" ? PUPIL_L : PUPIL_R;
    const d = side === "L" ? LOGO_PATHS.EYE_L : LOGO_PATHS.EYE_R;
    return (
      <g transform={`translate(0 ${c.y}) scale(1 ${open}) translate(0 ${-c.y})`}>
        <path d={d} fill={white} />
        <g clipPath={`url(#${id}-c${side})`}>
          <circle cx={c.x + lx} cy={c.y + ly} r={p.r * 1.12} fill={pupil} />
        </g>
      </g>
    );
  };
  return (
    <svg
      width={width}
      height={height}
      viewBox={`${vb.x} ${vb.y} ${vb.w} ${vb.h}`}
      style={{ overflow: "visible", display: "block", ...style }}
    >
      <defs>
        <clipPath id={`${id}-cL`}>
          <path d={LOGO_PATHS.EYE_L} />
        </clipPath>
        <clipPath id={`${id}-cR`}>
          <path d={LOGO_PATHS.EYE_R} />
        </clipPath>
      </defs>
      {one("L")}
      {one("R")}
    </svg>
  );
};

/** Pupil centre of the left eye in logo units (used to zoom through it). */
export const LEFT_PUPIL_NATURAL = { x: PUPIL_L.cx, y: PUPIL_L.cy, r: PUPIL_L.r };
export const LOGO_SIZE = LOGO_VIEWBOX;
