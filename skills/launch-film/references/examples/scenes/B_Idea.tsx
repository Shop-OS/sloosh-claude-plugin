import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { MotionBlur } from "../components/MotionBlur";
import { BBox, Crosshair, MonoLabel } from "../components/Tech";
import { C, FONT } from "../theme";
import { E, kf, prog } from "../lib/anim";

// Hand-drawn idea sketch: a cake on the moon. Paths are drawn on with pathLength.
const STROKE = C.yellow;

const Stroke: React.FC<{ d: string; p: number; w?: number; color?: string }> = ({ d, p, w = 7, color = STROKE }) => (
  <path
    d={d}
    pathLength={1}
    fill="none"
    stroke={color}
    strokeWidth={w}
    strokeLinecap="round"
    strokeLinejoin="round"
    strokeDasharray="1 1"
    strokeDashoffset={1 - Math.max(0, Math.min(1, p))}
  />
);

const Berry: React.FC<{ x: number; y: number; s: number; r?: number }> = ({ x, y, s, r = 0 }) => (
  <g transform={`translate(${x} ${y}) rotate(${r}) scale(${s})`}>
    <path d="M0 -26 C 20 -26 26 -6 14 12 C 8 22 2 28 0 30 C -2 28 -8 22 -14 12 C -26 -6 -20 -26 0 -26 Z" fill={C.yellow} />
    <path d="M-10 -26 L0 -36 L10 -26 M0 -36 L0 -28" stroke={C.ink} strokeWidth={3} fill="none" strokeLinecap="round" />
    <circle cx={-6} cy={-6} r={2.4} fill={C.ink} />
    <circle cx={6} cy={2} r={2.4} fill={C.ink} />
    <circle cx={-2} cy={12} r={2.4} fill={C.ink} />
  </g>
);

const Sparkle: React.FC<{ x: number; y: number; s: number }> = ({ x, y, s }) => (
  <path
    transform={`translate(${x} ${y}) scale(${s})`}
    d="M0 -20 C 3 -5 5 -3 20 0 C 5 3 3 5 0 20 C -3 5 -5 3 -20 0 C -5 -3 -3 -5 0 -20 Z"
    fill={C.white}
  />
);

const Inner: React.FC = () => {
  const f = useCurrentFrame();
  const moon = prog(f, 2, 12, E.inOutCubic);
  const cakeTop = prog(f, 5, 13, E.inOutCubic);
  const cakeBody = prog(f, 9, 17, E.inOutCubic);
  const plate = prog(f, 13, 19, E.inOutCubic);
  const piping = prog(f, 14, 21, E.inOutCubic);
  const berries = [0, 1, 2].map((i) => prog(f, 15 + i * 1.5, 21 + i * 1.5, E.outBack));
  const stars = [0, 1, 2].map((i) => prog(f, 17 + i * 2, 23 + i * 2, E.outBack));
  const arrow = prog(f, 19, 26, E.inOutCubic);
  const write = prog(f, 9, 27, E.inOutCubic);
  const box = prog(f, 22, 29, E.outExpo);
  const whip = prog(f, 30, 38, E.inExpo);
  const push = kf(f, [0, 30], [1.08, 1.14], E.outCubic);
  const tx = -whip * 2600;

  // doodle placement
  const ox = 960 - 330;
  const oy = 205;

  return (
    <AbsoluteFill style={{ background: C.ink, overflow: "hidden" }}>
      <AbsoluteFill
        style={{
          backgroundImage: "radial-gradient(rgba(255,255,255,0.07) 1.2px, transparent 1.2px)",
          backgroundSize: "28px 28px",
          transform: `translateX(${tx * 0.6}px)`,
        }}
      />
      <AbsoluteFill style={{ transform: `translateX(${tx}px) scale(${push})`, transformOrigin: "960px 540px" }}>
        <svg width={1920} height={1080} style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }}>
          <g transform={`translate(${ox} ${oy}) rotate(-3 330 220)`}>
            {/* crescent moon */}
            <Stroke d="M560 30 C 500 40 470 100 488 156 C 506 210 566 236 618 220 C 572 206 540 168 538 120 C 536 78 552 48 560 30 Z" p={moon} />
            {/* cake top ellipse */}
            <Stroke d="M112 238 C 112 206 210 190 300 190 C 392 190 486 206 486 236 C 486 266 392 282 300 282 C 208 282 112 268 112 238 Z" p={cakeTop} />
            {/* cake body */}
            <Stroke d="M112 240 L 116 380 C 120 414 214 432 300 432 C 390 432 480 416 484 382 L 486 238" p={cakeBody} />
            {/* plate */}
            <Stroke d="M70 392 C 60 440 200 470 300 470 C 410 470 548 444 530 394" p={plate} w={6} />
            {/* piped rim */}
            <Stroke
              d="M120 250 q 12 16 24 0 q 12 16 24 0 q 12 16 24 0 q 12 16 24 0 q 12 16 24 0 q 12 16 24 0 q 12 16 24 0 q 12 16 24 0 q 12 16 24 0 q 12 16 24 0 q 12 16 24 0 q 12 16 24 0 q 12 16 24 0 q 12 16 24 0 q 12 16 24 0"
              p={piping}
              w={5}
            />
            <Berry x={232} y={208} s={berries[0]} r={-12} />
            <Berry x={300} y={196} s={berries[1] * 1.1} r={4} />
            <Berry x={370} y={210} s={berries[2]} r={14} />
            <Sparkle x={640} y={120} s={stars[0] * 0.9} />
            <Sparkle x={430} y={20} s={stars[1] * 0.6} />
            <Sparkle x={36} y={120} s={stars[2] * 0.75} />
            {/* arrow from handwriting to the cake */}
            <Stroke d="M-40 560 C -90 520 -70 430 40 396" p={arrow} w={5} color={C.white} />
            <Stroke d="M14 380 L 44 394 L 22 420" p={prog(f, 24, 27)} w={5} color={C.white} />
          </g>
        </svg>
        {/* handwriting */}
        <div
          style={{
            position: "absolute",
            left: 0,
            right: 0,
            top: 760,
            textAlign: "center",
            fontFamily: FONT.script,
            fontWeight: 700,
            fontSize: 92,
            color: C.white,
            clipPath: `inset(0 ${(1 - write) * 100}% 0 0)`,
            transform: "rotate(-2deg)",
          }}
        >
          my cake… <span style={{ color: C.yellow }}>on the moon?</span>
        </div>
        <BBox
          x={ox - 40}
          y={oy - 30}
          w={720}
          h={540}
          p={box}
          color={C.white}
          handleFill={C.ink}
          label="YOUR IDEA"
          tagBg={C.yellow}
          labelSize={15}
        />
        <Crosshair x={ox + 300} y={oy + 330} p={box} color={C.white} size={20} />
        <MonoLabel text="IDEA_001 · SKETCH" p={prog(f, 23, 30)} color="rgba(255,255,255,0.55)" style={{ position: "absolute", left: ox - 40, top: oy + 528 }} />
        <MonoLabel text="V0.1 — ROUGH IS FINE" p={prog(f, 25, 31)} color="rgba(255,255,255,0.55)" style={{ position: "absolute", left: ox + 680 - 260, top: oy + 528, width: 300, textAlign: "right" }} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const SceneIdea: React.FC = () => (
  <MotionBlur
    samplesAt={(fr) => (fr >= 30 ? 16 : 1)}
    shutterAngle={240}
    smearAt={(fr) => ({ x: fr >= 31 ? Math.min(60, (fr - 30) * 9) : 0, y: 0 })}
  >
    <Inner />
  </MotionBlur>
);
