import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { MotionBlur } from "../components/MotionBlur";
import { Cam, Plane3D, Stage3D } from "../components/Stage3D";
import { PixelWipe, TiltShift } from "../components/FX";
import { Cursor } from "../components/Cursor";
import { ExplorePage, EXPLORE_LAYOUT, PAGE_W } from "../ui/Pages";
import { C, FONT } from "../theme";
import { E, Key, path, pathSpeed, prog } from "../lib/anim";
import { project } from "../lib/project";
import { ICheck } from "../ui/Icons";

const PERSP = 1500;

type F = "tx" | "ty" | "z" | "rx" | "rz" | "sx";
const KEYS: Key<F>[] = [
  { t: 0, tx: 760, ty: 430, z: 60, rx: 40, rz: -14, sx: 1900 },
  { t: 0.24, tx: 760, ty: 470, z: 110, rx: 40, rz: -13, sx: 0, e: E.outExpo },
  { t: 0.72, tx: 640, ty: 1560, z: 40, rx: 40, rz: -10, sx: 0, e: E.inOutCubic },
  { t: 1.0, tx: 330, ty: 1795, z: 520, rx: 30, rz: -6, sx: 0, e: E.outCubic },
  { t: 1.47, tx: 215, ty: 1812, z: 930, rx: 16, rz: -3, sx: 0, e: E.inCubic },
];

const camAt = (t: number): Cam => ({
  tx: path(t, KEYS, "tx"),
  ty: path(t, KEYS, "ty"),
  z: path(t, KEYS, "z"),
  rx: path(t, KEYS, "rx"),
  rz: path(t, KEYS, "rz"),
  sx: path(t, KEYS, "sx"),
});

// Floating "what do you want to make" chips above the page.
const CHIPS: { label: string; x: number; y: number; h: number; style: "yellow" | "white" | "glass" }[] = [
  { label: "Product shot", x: 1010, y: 300, h: 150, style: "glass" },
  { label: "Campaign", x: 90, y: 640, h: 140, style: "yellow" },
  { label: "Poster", x: 1110, y: 880, h: 170, style: "white" },
  { label: "Visual story", x: 40, y: 1180, h: 130, style: "glass" },
  { label: "Lookbook", x: 1060, y: 1380, h: 150, style: "glass" },
  { label: "Video ad", x: 520, y: 1040, h: 190, style: "white" },
];

const Chip: React.FC<{ label: string; kind: "yellow" | "white" | "glass" }> = ({ label, kind }) => {
  const bg = kind === "yellow" ? C.yellow : kind === "white" ? "#FAFAFA" : "rgba(28,28,28,0.92)";
  const fg = kind === "glass" ? C.text : C.ink;
  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 14,
        height: 104,
        padding: "0 44px 0 30px",
        borderRadius: 999,
        background: bg,
        color: fg,
        fontFamily: FONT.ui,
        fontWeight: 600,
        fontSize: 44,
        whiteSpace: "nowrap",
        border: kind === "glass" ? "1.5px solid rgba(255,255,255,0.16)" : "none",
        boxShadow:
          kind === "yellow"
            ? `0 6px 0 ${C.yellowEdge}, 0 30px 60px rgba(0,0,0,0.55)`
            : "0 30px 60px rgba(0,0,0,0.55)",
      }}
    >
      <div
        style={{
          width: 44,
          height: 44,
          borderRadius: 999,
          background: kind === "glass" ? C.yellow : C.ink,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <ICheck size={22} color={kind === "glass" ? C.ink : kind === "yellow" ? C.yellow : C.white} stroke={3} />
      </div>
      {label}
    </div>
  );
};

const FOOD = { x: 26 + 335 / 2, y: EXPLORE_LAYOUT.tools.y + 62 + 58 };

const Inner: React.FC = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = f / fps;
  const cam = camAt(t);

  // tool card focus: Food Styling
  const hover = prog(t, 0.76, 0.88, E.outCubic);
  const toolHighlight = [hover, 0, 0, 0, 0, 0, 0, 0];
  const pulse = [0.36, 0.42, 0.48, 0.54, 0.4, 0.46, 0.52, 0.58].map((s) => prog(t, s, s + 0.08) * (1 - prog(t, s + 0.12, s + 0.24)) * 0.6);
  toolHighlight.forEach((_, i) => {
    if (i > 0) toolHighlight[i] = pulse[i];
  });

  // cursor follows the projected card
  const target = project(cam, FOOD.x + 40, FOOD.y + 10, 0, PERSP);
  const enter = prog(t, 0.55, 0.86, E.outCubic);
  const cx = 1600 + (target.x - 1600) * enter;
  const cy = 1150 + (target.y - 1150) * enter;
  const press = prog(t, 0.86, 0.9) * (1 - prog(t, 0.93, 0.98));
  const ripple = t >= 0.88 ? prog(t, 0.88, 1.18) : -1;

  return (
    <AbsoluteFill style={{ background: "radial-gradient(120% 90% at 50% 40%, #1a1a1a 0%, #0a0a0a 70%)" }}>
      <Stage3D perspective={PERSP}>
        <Plane3D cam={cam} width={PAGE_W} height={EXPLORE_LAYOUT.height}>
          <ExplorePage state={{ toolHighlight, heroProgress: 0.25 + t * 0.2 }} logoLook={{ x: Math.sin(t * 6) * 0.8, y: 0 }} />
          {/* floating chips */}
          {CHIPS.map((c, i) => {
            const bob = Math.sin(t * 2.2 + i * 1.3) * 10;
            const appear = prog(t, 0.05 + i * 0.07, 0.35 + i * 0.07, E.outBack);
            return (
              <React.Fragment key={c.label}>
                <div
                  style={{
                    position: "absolute",
                    left: c.x + 30,
                    top: c.y + 40,
                    width: c.label.length * 22 + 110,
                    height: 60,
                    borderRadius: 999,
                    background: "rgba(0,0,0,0.6)",
                    filter: `blur(${14 + c.h * 0.08}px)`,
                    opacity: appear,
                  }}
                />
                <div
                  style={{
                    position: "absolute",
                    left: c.x,
                    top: c.y,
                    transformStyle: "preserve-3d",
                    transformOrigin: "0% 100%",
                    transform: `translateZ(${(c.h + bob) * appear}px) rotateZ(${-cam.rz}deg) rotateX(${-cam.rx * 0.85}deg) rotateY(${Math.sin(i * 2.1) * 8}deg) scale(${appear})`,
                  }}
                >
                  <Chip label={c.label} kind={c.style} />
                </div>
              </React.Fragment>
            );
          })}
        </Plane3D>
      </Stage3D>
      <TiltShift top={0.26} bottom={0.12} blur={7} />
      <Cursor x={cx} y={cy} size={48} press={press} ripple={ripple} opacity={prog(t, 0.55, 0.62)} />
      <PixelWipe p={prog(t, 1.16, 1.45)} color={C.yellow} cell={96} dir={{ x: 1, y: -0.35 }} seed={3} accent={C.ink} accentRatio={0.06} />
    </AbsoluteFill>
  );
};

export const SceneChoose: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <MotionBlur
      shutterAngle={180}
      samplesAt={(fr) => {
        const t = fr / fps;
        const sp = pathSpeed(t, KEYS, ["tx", "ty", "sx"]) + pathSpeed(t, KEYS, ["z"]) * 0.6;
        return sp > 2400 ? 12 : sp > 900 ? 8 : sp > 300 ? 4 : 1;
      }}
      smearAt={(fr) => {
        const sx = Math.abs(pathSpeed(fr / fps, KEYS, ["sx"]));
        return { x: Math.min(40, sx / 260), y: 0 };
      }}
    >
      <Inner />
    </MotionBlur>
  );
};
