import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { MotionBlur } from "../components/MotionBlur";
import { Cam, Plane3D, Stage3D } from "../components/Stage3D";
import { Cursor } from "../components/Cursor";
import { Photo } from "../components/Media";
import { MonoLabel } from "../components/Tech";
import { PAGE_W, WF, WorkflowPage } from "../ui/Pages";
import { NodeLabel } from "../ui/Kit";
import { IMG } from "../assets";
import { C } from "../theme";
import { E, Key, kf, path, pathSpeed, prog } from "../lib/anim";
import { project } from "../lib/project";

const PERSP = 1500;
const PC = { x: WF.product.x + WF.product.w / 2, y: WF.product.y + WF.product.h / 2 };
const GC = { x: WF.generate.x + WF.generate.w / 2, y: WF.generate.y + WF.generate.h / 2 };

type F = "tx" | "ty" | "z" | "rx" | "rz";
const KEYS: Key<F>[] = [
  { t: 0, tx: 222, ty: 173, z: 820, rx: 4, rz: -1 },
  { t: 0.32, tx: 330, ty: 505, z: 400, rx: 12, rz: -3.5, e: E.outExpo },
  { t: 0.95, tx: 338, ty: 530, z: 430, rx: 11, rz: -3, e: E.inOutCubic },
  { t: 1.1, tx: PC.x, ty: PC.y, z: 1010, rx: 0, rz: 0, e: E.inCubic },
];
const camAt = (t: number): Cam => ({
  tx: path(t, KEYS, "tx"),
  ty: path(t, KEYS, "ty"),
  z: path(t, KEYS, "z"),
  rx: path(t, KEYS, "rx"),
  rz: path(t, KEYS, "rz"),
});

/** Illustrative graph inside the overview canvas. */
const MiniCanvas: React.FC<{ t: number }> = ({ t }) => {
  const a = prog(t, 0.2, 0.6, E.outCubic);
  return (
    <div style={{ position: "absolute", inset: 0, opacity: 0.35 + 0.65 * a }}>
      <svg width="100%" height="100%" style={{ position: "absolute", inset: 0 }}>
        <path d="M250 150 C 380 150, 380 235, 500 235" stroke="rgba(255,255,255,0.35)" strokeWidth={2.5} fill="none" />
        <path d="M250 320 C 380 320, 380 245, 500 245" stroke="rgba(255,255,255,0.35)" strokeWidth={2.5} fill="none" />
        <path d="M680 240 C 740 240, 740 240, 790 240" stroke="rgba(254,204,21,0.8)" strokeWidth={2.5} fill="none" />
      </svg>
      <div style={{ position: "absolute", left: 40, top: 90 }}>
        <NodeLabel kind="image" text="Product photo" />
        <div style={{ marginTop: 8, width: 210, height: 110, borderRadius: 10, border: "1.5px solid rgba(96,165,250,0.45)", background: "#111" }} />
      </div>
      <div style={{ position: "absolute", left: 40, top: 262 }}>
        <NodeLabel kind="image" text="Scene photo" />
        <div style={{ marginTop: 8, width: 210, height: 110, borderRadius: 10, border: "1.5px solid rgba(96,165,250,0.45)", background: "#111" }} />
      </div>
      <div style={{ position: "absolute", left: 500, top: 196 }}>
        <NodeLabel kind="model" text="Relight" />
        <div style={{ marginTop: 8, width: 180, height: 64, borderRadius: 10, border: "1.5px solid rgba(254,204,21,0.5)", background: "#111", color: C.textSubtle, fontSize: 13, display: "flex", alignItems: "center", justifyContent: "center" }}>
          Nano Banana Pro
        </div>
      </div>
      <div style={{ position: "absolute", left: 790, top: 160 }}>
        <NodeLabel kind="image" text="Output" />
        <div style={{ marginTop: 8, width: 130, height: 150, borderRadius: 10, border: "1.5px dashed rgba(255,255,255,0.25)", background: "#0d0d0d" }} />
      </div>
    </div>
  );
};

const Inner: React.FC = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = f / fps;
  const cam = camAt(t);

  const dropT = 0.53; // "photo"
  const productFill = prog(t, dropT, dropT + 0.14, E.outCubic);
  const productHover = prog(t, 0.36, 0.46) * (1 - prog(t, dropT, dropT + 0.06));
  const sceneFill = prog(t, 0.66, 0.78, E.outCubic);
  const ready = prog(t, 0.74, 0.8);
  const pressT = 0.93;
  const genPress = prog(t, pressT - 0.03, pressT) * (1 - prog(t, pressT + 0.05, pressT + 0.1));

  // dragged print: flies in from the right, lands in the slot on "photo"
  const slot = project(cam, PC.x, PC.y, 0, PERSP);
  const fly = prog(t, 0.06, dropT, E.outCubic);
  const land = prog(t, dropT - 0.04, dropT + 0.08, E.inOutCubic);
  const px = kf(fly, [0, 1], [2250, slot.x + 30]) * (1 - land) + slot.x * land;
  const py = kf(fly, [0, 1], [760, slot.y - 10]) * (1 - land) + slot.y * land;
  const pScale = (1 - land) * 1 + land * ((WF.product.w * slot.scale) / 460);
  const pRot = kf(fly, [0, 1], [14, -5]) * (1 - land);
  const printOpacity = 1 - prog(t, dropT + 0.02, dropT + 0.1);

  // cursor: drags the print, then hits Generate
  const gen = project(cam, GC.x + 60, GC.y + 6, 0, PERSP);
  const toGen = prog(t, 0.6, 0.88, E.inOutCubic);
  const grabX = px + 160 * pScale;
  const grabY = py - 120 * pScale;
  const cx = grabX * (1 - toGen) + gen.x * toGen;
  const cy = grabY * (1 - toGen) + gen.y * toGen;
  const ripple = t >= pressT ? prog(t, pressT, pressT + 0.3) : -1;

  return (
    <AbsoluteFill style={{ background: "radial-gradient(120% 90% at 40% 40%, #1a1a1a 0%, #0a0a0a 70%)" }}>
      <Stage3D perspective={PERSP}>
        <Plane3D cam={cam} width={PAGE_W} height={900}>
          <WorkflowPage
            productFill={productFill}
            sceneFill={sceneFill}
            productHover={productHover}
            generateP={ready}
            generatePress={genPress}
            canvas={<MiniCanvas t={t} />}
            logoLook={{ x: kf(t, [0, 0.5, 0.9], [1, -1, 0.4]), y: 0.2 }}
          />
        </Plane3D>
      </Stage3D>
      {printOpacity > 0 ? (
        <div
          style={{
            position: "absolute",
            left: px,
            top: py,
            width: 0,
            height: 0,
            opacity: printOpacity,
          }}
        >
          <div
            style={{
              position: "absolute",
              left: -240,
              top: -150,
              padding: 12,
              background: "#FFFFFF",
              borderRadius: 6,
              transform: `scale(${pScale}) rotate(${pRot}deg)`,
              boxShadow: `0 ${40 * (1 - land)}px ${80 * (1 - land) + 10}px rgba(0,0,0,0.6)`,
            }}
          >
            <Photo img={IMG.cakeSrc} crop={{ x: 780, y: 410, w: 700, h: 420 }} width={456} height={274} />
          </div>
        </div>
      ) : null}
      <MonoLabel
        text="SOURCE · cake.jpg"
        p={prog(t, 0.16, 0.4)}
        color={C.yellow}
        style={{ position: "absolute", left: px - 240, top: py + 150, opacity: printOpacity }}
      />
      <Cursor x={cx} y={cy} size={42} press={genPress} ripple={ripple} opacity={prog(t, 0.06, 0.14) * (1 - prog(t, 1.02, 1.08))} />
    </AbsoluteFill>
  );
};

export const SceneBringPhoto: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <MotionBlur
      shutterAngle={180}
      samplesAt={(fr) => {
        const t = fr / fps;
        const sp = pathSpeed(t, KEYS, ["tx", "ty"]) + pathSpeed(t, KEYS, ["z"]) * 0.5;
        const fly = t > 0.05 && t < 0.4;
        return sp > 2500 ? 10 : sp > 800 || fly ? 6 : sp > 300 ? 3 : 1;
      }}
    >
      <Inner />
    </MotionBlur>
  );
};
