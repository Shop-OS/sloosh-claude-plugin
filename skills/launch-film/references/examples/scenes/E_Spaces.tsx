import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { MotionBlur } from "../components/MotionBlur";
import { Cam, Plane3D, Stage3D } from "../components/Stage3D";
import { TiltShift } from "../components/FX";
import { Cursor } from "../components/Cursor";
import { PAGE_W, SPACE_CARDS, SPACES_LAYOUT, SpacesPage, spaceCardPos } from "../ui/Pages";
import { MonoLabel, Tag } from "../components/Tech";
import { E, Key, path, pathSpeed, prog } from "../lib/anim";
import { project } from "../lib/project";

const PERSP = 1500;
const TARGET = 3; // Product in Scene + Relight
const tp = spaceCardPos(TARGET);
const BADGE = { x: tp.x + 24, y: tp.y + 24 };
const CARD_C = { x: tp.x + SPACES_LAYOUT.cardW / 2, y: tp.y + 130 };

type F = "tx" | "ty" | "z" | "rx" | "rz";
const KEYS: Key<F>[] = [
  { t: 0, tx: BADGE.x, ty: BADGE.y, z: 1260, rx: 0, rz: 0 },
  { t: 0.55, tx: 600, ty: 600, z: 80, rx: 38, rz: -11, e: E.outExpo },
  { t: 1.22, tx: 760, ty: 700, z: 40, rx: 40, rz: -9, e: E.inOutCubic },
  { t: 1.62, tx: CARD_C.x + 50, ty: CARD_C.y + 10, z: 420, rx: 30, rz: -6, e: E.inOutCubic },
  { t: 2.14, tx: CARD_C.x, ty: CARD_C.y - 20, z: 940, rx: 10, rz: -2, e: E.inCubic },
];

const camAt = (t: number): Cam => ({
  tx: path(t, KEYS, "tx"),
  ty: path(t, KEYS, "ty"),
  z: path(t, KEYS, "z"),
  rx: path(t, KEYS, "rx"),
  rz: path(t, KEYS, "rz"),
});

const Inner: React.FC = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = f / fps;
  const cam = camAt(t);

  // staggered card entrances radiating out from the target card
  const appear = SPACE_CARDS.map((_, i) => {
    if (i === TARGET) return 1;
    const p = spaceCardPos(i);
    const d = Math.hypot(p.x - tp.x, p.y - tp.y) / 1400;
    return prog(t, 0.08 + d * 0.5, 0.5 + d * 0.5, E.outCubic);
  });
  const hover = prog(t, 1.32, 1.46, E.outCubic);
  const clickT = 1.52;
  const highlight = SPACE_CARDS.map((_, i) => (i === TARGET ? hover : 0));
  const lift = SPACE_CARDS.map((_, i) => (i === TARGET ? 10 * hover : 0));

  const target = project(cam, CARD_C.x + 70, CARD_C.y + 40, 0, PERSP);
  const enter = prog(t, 0.9, 1.42, E.outCubic);
  const cx = 1750 + (target.x - 1750) * enter;
  const cy = 1180 + (target.y - 1180) * enter;
  const press = prog(t, clickT - 0.04, clickT) * (1 - prog(t, clickT + 0.04, clickT + 0.1));
  const ripple = t >= clickT ? prog(t, clickT, clickT + 0.32) : -1;

  // annotation tag pinned to the target card
  const tagPos = project(cam, tp.x, tp.y - 18, 0, PERSP);
  const tagP = prog(t, 1.0, 1.2, E.outExpo) * (1 - prog(t, 1.9, 2.0));

  return (
    <AbsoluteFill style={{ background: "radial-gradient(120% 90% at 50% 35%, #191919 0%, #0a0a0a 70%)" }}>
      <Stage3D perspective={PERSP}>
        <Plane3D cam={cam} width={PAGE_W} height={SPACES_LAYOUT.height}>
          <SpacesPage appear={appear} highlight={highlight} lift={lift} logoLook={{ x: Math.sin(t * 5) * 0.9, y: 0 }} />
        </Plane3D>
      </Stage3D>
      <TiltShift top={0.24 * prog(t, 0.2, 0.6)} bottom={0.1 * prog(t, 0.2, 0.6)} blur={7} />
      {tagP > 0.01 ? (
        <div style={{ position: "absolute", left: tagPos.x, top: tagPos.y - 40 }}>
          <Tag text="WORKFLOW · PREPARED" p={tagP} size={20} />
        </div>
      ) : null}
      <MonoLabel
        text="SPACES / RECOMMENDED"
        p={prog(t, 0.35, 0.7)}
        color="rgba(255,255,255,0.6)"
        style={{ position: "absolute", left: 72, top: 64, opacity: 1 - prog(t, 1.8, 2.0) }}
      />
      <Cursor x={cx} y={cy} size={50} press={press} ripple={ripple} opacity={prog(t, 0.9, 1.0)} />
    </AbsoluteFill>
  );
};

export const SceneSpaces: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <MotionBlur
      shutterAngle={180}
      samplesAt={(fr) => {
        const t = fr / fps;
        const sp = pathSpeed(t, KEYS, ["tx", "ty"]) + pathSpeed(t, KEYS, ["z"]) * 0.5;
        return sp > 2500 ? 10 : sp > 900 ? 6 : sp > 350 ? 3 : 1;
      }}
    >
      <Inner />
    </MotionBlur>
  );
};
