import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { Logo, LOGO_SIZE } from "../brand/Logo";
import { MotionBlur } from "../components/MotionBlur";
import { Zoom } from "../components/Media";
import { Crosshair, Guides, MonoLabel } from "../components/Tech";
import { C } from "../theme";
import { E, kf, prog } from "../lib/anim";

// Wordmark placement (frame space)
const LW = 1100;
const LS = LW / LOGO_SIZE.w;
const LX = 960 - LW / 2;
const LH = LOGO_SIZE.h * LS;
const LY = 540 - LH / 2;
// left eye centre (pupil when looking at camera)
const PX = LX + 613.17 * LS;
const PY = LY + 232.59 * LS;

const Inner: React.FC = () => {
  const f = useCurrentFrame();
  // background punctuation: paper -> yellow -> black
  const mode = f < 38 ? "paper" : f < 41 ? "yellow" : "black";
  const bg = mode === "paper" ? C.paper : mode === "yellow" ? C.yellow : C.ink;
  const lineColor = mode === "paper" ? "rgba(10,10,10,0.2)" : mode === "yellow" ? "rgba(10,10,10,0.35)" : "rgba(255,255,255,0.12)";
  const labelColor = mode === "paper" ? "rgba(10,10,10,0.62)" : mode === "yellow" ? C.ink : "rgba(255,255,255,0.45)";

  const guideP = prog(f, 0, 14, E.inOutCubic);
  const squareP = prog(f, 9, 17);
  const reveal = [0, 1, 2, 3, 4].map((i) => prog(f, 18 + i * 2, 27 + i * 2, E.outExpo));
  const eyeOpen = f < 31 ? 0 : kf(f, [31, 33, 35], [0, 1.12, 1], E.outCubic);
  const lookX = kf(f, [31, 34, 38, 43, 46], [0, 0, 1, 1, 0], E.inOutCubic);
  const lookY = kf(f, [31, 34, 38, 43, 46], [0.15, 0.15, 0, 0, 0], E.inOutCubic);
  const dot = prog(f, 1, 5, E.outBack) * (1 - prog(f, 18, 22));

  // push through the left pupil (log-space zoom so the move accelerates evenly)
  const push = prog(f, 44, 51.5, E.inCubic);
  const k = Math.pow(52, push);

  const variant = mode === "yellow" ? "ink" : "gradient";
  const xs = [LX, 960, LX + LW];
  const ys = [LY, 540, LY + LH];

  return (
    <AbsoluteFill style={{ background: bg }}>
      <Zoom k={k} cx={PX} cy={PY} dx={(960 - PX) * push} dy={(540 - PY) * push}>
        <Guides
          xs={xs}
          ys={ys}
          p={guideP}
          color={lineColor}
          thickness={1.5}
          squares
          squareP={squareP}
          squareColor={mode === "yellow" ? C.ink : C.yellow}
          squareSize={12}
        />
        {/* construction circle */}
        <div
          style={{
            position: "absolute",
            left: 960 - 330,
            top: 540 - 330,
            width: 660,
            height: 660,
            borderRadius: "50%",
            border: `1px solid ${lineColor}`,
            clipPath: `inset(0 ${(1 - prog(f, 4, 18, E.inOutCubic)) * 100}% 0 0)`,
          }}
        />
        <Crosshair x={960} y={540} size={26} color={mode === "yellow" ? C.ink : C.yellow} p={prog(f, 2, 8)} />
        {dot > 0 ? (
          <div
            style={{
              position: "absolute",
              left: 960 - 8 * dot,
              top: 540 - 8 * dot,
              width: 16 * dot,
              height: 16 * dot,
              background: C.yellow,
            }}
          />
        ) : null}
        <div style={{ position: "absolute", left: LX, top: LY }}>
          <Logo
            width={LW}
            variant={variant}
            reveal={reveal}
            eyeOpen={eyeOpen}
            look={{ x: lookX, y: lookY }}
            socket={C.ink}
            pupil={C.ink}
          />
        </div>
        <MonoLabel text={"SLOOSH_BETA\nIDEA → IMAGE"} p={prog(f, 3, 16)} color={labelColor} style={{ position: "absolute", left: 72, top: 64 }} />
        <MonoLabel text={"FIG. 01 — WORDMARK"} p={prog(f, 6, 18)} color={labelColor} style={{ position: "absolute", right: 72, top: 64, textAlign: "right" }} />
        <MonoLabel text={"X 960   Y 540"} p={prog(f, 8, 20)} color={labelColor} style={{ position: "absolute", left: 72, bottom: 64 }} />
        <MonoLabel text={"BETA.SLOOSH.AI"} p={prog(f, 10, 22)} color={labelColor} style={{ position: "absolute", right: 72, bottom: 64, textAlign: "right" }} />
        <MonoLabel
          text={"SPECIMEN_01"}
          p={prog(f, 12, 22)}
          color={mode === "yellow" ? C.yellow : C.ink}
          size={12}
          style={{
            position: "absolute",
            left: LX,
            top: LY + LH + 26,
            background: mode === "yellow" ? C.ink : C.yellow,
            padding: "3px 7px",
            opacity: f >= 12 ? 1 : 0,
          }}
        />
      </Zoom>
    </AbsoluteFill>
  );
};

export const SceneLogo: React.FC = () => (
  <MotionBlur samplesAt={(fr) => (fr >= 52 ? 1 : fr >= 46 ? 28 : fr >= 44 ? 10 : 1)} shutterAngle={200}>
    <Inner />
  </MotionBlur>
);
