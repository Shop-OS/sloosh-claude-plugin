import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { MotionBlur } from "../components/MotionBlur";
import { Cam, Plane3D, Stage3D } from "../components/Stage3D";
import { TiltShift } from "../components/FX";
import { Photo } from "../components/Media";
import { BBox, MonoLabel, Tag } from "../components/Tech";
import { NodeLabel, Port } from "../ui/Kit";
import { WF_PRODUCT_CROP } from "../ui/Pages";
import { IMG, ImgAsset } from "../assets";
import { C, FONT } from "../theme";
import { clamp01, E, Key, kf, path, pathSpeed, prog } from "../lib/anim";
import { lerpRect, viewForZoom, CAKE_SCREEN } from "../lib/cakeView";
import { IStar, ISparkle } from "../ui/Icons";

const PERSP = 1500;
const CW = 3500;
const CH = 1900;

type Node = { x: number; y: number; w: number; h: number };
const N_TEXT: Node = { x: 200, y: 360, w: 420, h: 190 };
const N_PROD: Node = { x: 200, y: 690, w: 420, h: 220 };
const N_SCENE: Node = { x: 200, y: 1010, w: 420, h: 220 };
const M: Node = { x: 920, y: 700, w: 380, h: 200 };
const OUT: { n: Node; img: ImgAsset; label: string; star?: boolean }[] = [
  { n: { x: 1580, y: 250, w: 480, h: 270 }, img: IMG.rWarm, label: "V1 · WARM" },
  { n: { x: 1580, y: 620, w: 480, h: 270 }, img: IMG.cakeMoon, label: "V2 · EARTHRISE", star: true },
  { n: { x: 1580, y: 990, w: 480, h: 270 }, img: IMG.rCool, label: "V3 · COOL" },
  { n: { x: 2160, y: 430, w: 480, h: 270 }, img: IMG.rGolden, label: "V4 · GOLDEN" },
  { n: { x: 2160, y: 800, w: 480, h: 270 }, img: IMG.rMono, label: "V5 · MONO" },
  { n: { x: 2160, y: 1170, w: 480, h: 270 }, img: IMG.rDusk, label: "V6 · DUSK" },
];
const FAR: { n: Node; img: ImgAsset; crop?: { x: number; y: number; w: number; h: number } }[] = [
  { n: { x: 2760, y: 260, w: 400, h: 225 }, img: IMG.cupCafe },
  { n: { x: 2760, y: 560, w: 400, h: 225 }, img: IMG.chairPoster },
  { n: { x: 2760, y: 860, w: 400, h: 225 }, img: IMG.alt01 },
  { n: { x: 2760, y: 1160, w: 400, h: 225 }, img: IMG.mGrid },
  { n: { x: 3200, y: 420, w: 260, h: 340 }, img: IMG.alt02, crop: { x: 560, y: 60, w: 620, h: 820 } },
  { n: { x: 3200, y: 840, w: 260, h: 340 }, img: IMG.alt03, crop: { x: 600, y: 60, w: 620, h: 820 } },
];

const NC = (n: Node) => ({ x: n.x + n.w / 2, y: n.y + n.h / 2 });

type F = "tx" | "ty" | "z" | "rx" | "rz";
const KEYS: Key<F>[] = [
  { t: 0, tx: NC(N_PROD).x, ty: NC(N_PROD).y, z: 915, rx: 0, rz: 0 },
  { t: 0.5, tx: 820, ty: 820, z: 60, rx: 28, rz: -7, e: E.outExpo },
  { t: 1.2, tx: 1860, ty: 820, z: -120, rx: 32, rz: -9, e: E.inOutCubic },
  { t: 1.47, tx: 2000, ty: 800, z: -170, rx: 33, rz: -10, e: E.outCubic },
];
const camAt = (t: number): Cam => ({
  tx: path(t, KEYS, "tx"),
  ty: path(t, KEYS, "ty"),
  z: path(t, KEYS, "z"),
  rx: path(t, KEYS, "rx"),
  rz: path(t, KEYS, "rz"),
});

const curve = (x0: number, y0: number, x1: number, y1: number) => {
  const dx = Math.max(80, (x1 - x0) * 0.5);
  return `M${x0} ${y0} C ${x0 + dx} ${y0}, ${x1 - dx} ${y1}, ${x1} ${y1}`;
};

const Canvas: React.FC<{ t: number }> = ({ t }) => {
  const mIn = prog(t, 0.12, 0.3, E.outBack);
  const run = prog(t, 0.3, 0.62, E.inOutCubic);
  const inLines = prog(t, 0.1, 0.34, E.inOutCubic);
  const outLines = OUT.map((_, i) => prog(t, 0.42 + i * 0.05, 0.62 + i * 0.05, E.inOutCubic));
  const outIn = OUT.map((_, i) => prog(t, 0.5 + i * 0.06, 0.74 + i * 0.06, E.outBack));
  const farIn = FAR.map((_, i) => prog(t, 0.8 + i * 0.05, 1.1 + i * 0.05, E.outCubic));
  const mOut = { x: M.x + M.w, y: M.y + M.h / 2 };
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        top: 0,
        width: CW,
        height: CH,
        background: C.ink,
        backgroundImage: "radial-gradient(rgba(255,255,255,0.10) 1.5px, transparent 1.5px)",
        backgroundSize: "26px 26px",
        transformStyle: "preserve-3d",
      }}
    >
      <svg width={CW} height={CH} style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }}>
        {[N_TEXT, N_PROD, N_SCENE].map((n, i) => (
          <path
            key={i}
            d={curve(n.x + n.w, n.y + n.h / 2, M.x, M.y + 60 + i * 40)}
            stroke="rgba(255,255,255,0.4)"
            strokeWidth={3}
            fill="none"
            pathLength={1}
            strokeDasharray="1 1"
            strokeDashoffset={1 - inLines}
          />
        ))}
        {OUT.map((o, i) => (
          <path
            key={i}
            d={curve(mOut.x, mOut.y, o.n.x, o.n.y + o.n.h / 2)}
            stroke={C.yellow}
            strokeOpacity={0.85}
            strokeWidth={3}
            fill="none"
            pathLength={1}
            strokeDasharray="1 1"
            strokeDashoffset={1 - outLines[i]}
          />
        ))}
      </svg>
      {/* prompt node */}
      <div style={{ position: "absolute", left: N_TEXT.x, top: N_TEXT.y - 40 }}>
        <NodeLabel kind="text" text="Text" scale={1.3} />
      </div>
      <div
        style={{
          position: "absolute",
          left: N_TEXT.x,
          top: N_TEXT.y,
          width: N_TEXT.w,
          height: N_TEXT.h,
          borderRadius: 16,
          border: "2px solid rgba(52,211,153,0.4)",
          background: "rgba(16,40,30,0.9)",
          color: C.text,
          fontFamily: FONT.ui,
          fontSize: 24,
          lineHeight: 1.4,
          padding: 22,
          boxSizing: "border-box",
        }}
      >
        Place my cake on the moon. Keep the icing, strawberries and rim exactly as they are.
      </div>
      {/* product + scene nodes */}
      {[
        { n: N_PROD, label: "Product photo", img: IMG.cakeSrc, crop: WF_PRODUCT_CROP },
        { n: N_SCENE, label: "Scene photo", img: IMG.cakeMoon, crop: { x: 60, y: 160, w: 760, h: 400 } },
      ].map((o) => (
        <React.Fragment key={o.label}>
          <div style={{ position: "absolute", left: o.n.x, top: o.n.y - 40 }}>
            <NodeLabel kind="image" text={o.label} scale={1.3} />
          </div>
          <div style={{ position: "absolute", left: o.n.x, top: o.n.y, borderRadius: 16, overflow: "hidden", border: "2px solid rgba(96,165,250,0.55)" }}>
            <Photo img={o.img} crop={o.crop} width={o.n.w} height={o.n.h} />
          </div>
          <div style={{ position: "absolute", left: o.n.x + o.n.w - 14, top: o.n.y + o.n.h / 2 - 14 }}>
            <Port kind="image" size={28} />
          </div>
        </React.Fragment>
      ))}
      {/* model node */}
      <div style={{ position: "absolute", left: M.x, top: M.y - 40, opacity: mIn }}>
        <NodeLabel kind="model" text="Relight" scale={1.3} />
      </div>
      <div
        style={{
          position: "absolute",
          left: M.x,
          top: M.y,
          width: M.w,
          height: M.h,
          borderRadius: 18,
          border: "2px solid rgba(254,204,21,0.6)",
          background: "#141209",
          transform: `translateZ(${30 * mIn}px) scale(${0.7 + 0.3 * mIn})`,
          opacity: clamp01(mIn * 1.5),
          fontFamily: FONT.ui,
          padding: 24,
          boxSizing: "border-box",
          boxShadow: "0 30px 60px rgba(0,0,0,0.5)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 10, color: C.yellowText, fontSize: 26, fontWeight: 600 }}>
          <ISparkle size={26} color={C.yellow} /> Nano Banana Pro
        </div>
        <div style={{ marginTop: 14, color: C.textMuted, fontSize: 18 }}>Product in Scene + Relight</div>
        <div style={{ marginTop: 22, height: 8, borderRadius: 4, background: C.layer3, overflow: "hidden" }}>
          <div style={{ width: `${run * 100}%`, height: "100%", background: C.yellow }} />
        </div>
      </div>
      {/* outputs, lifted for parallax */}
      {OUT.map((o, i) => {
        const a = outIn[i];
        const h = 40 + (i % 3) * 30;
        return (
          <React.Fragment key={o.label}>
            <div
              style={{
                position: "absolute",
                left: o.n.x + 20,
                top: o.n.y + 30,
                width: o.n.w - 40,
                height: o.n.h - 30,
                borderRadius: 20,
                background: "rgba(0,0,0,0.7)",
                filter: "blur(22px)",
                opacity: a,
              }}
            />
            <div
              style={{
                position: "absolute",
                left: o.n.x,
                top: o.n.y,
                transformStyle: "preserve-3d",
                transform: `translateZ(${h * a}px) scale(${0.6 + 0.4 * a})`,
                opacity: clamp01(a * 1.4),
              }}
            >
              <div style={{ position: "absolute", left: 0, top: -42 }}>
                <NodeLabel kind="image" text={o.label} scale={1.25} />
              </div>
              <div
                style={{
                  borderRadius: 16,
                  overflow: "hidden",
                  border: o.star ? `3px solid ${C.yellow}` : "2px solid rgba(255,255,255,0.18)",
                  boxShadow: o.star ? "0 0 0 6px rgba(254,204,21,0.18)" : undefined,
                }}
              >
                <Photo img={o.img} width={o.n.w} height={o.n.h} />
              </div>
              {o.star ? (
                <div style={{ position: "absolute", right: 14, top: 14, opacity: prog(t, 0.9, 1.0) }}>
                  <IStar size={40} />
                </div>
              ) : null}
            </div>
          </React.Fragment>
        );
      })}
      {FAR.map((o, i) => (
        <div
          key={i}
          style={{
            position: "absolute",
            left: o.n.x,
            top: o.n.y,
            borderRadius: 14,
            overflow: "hidden",
            border: "2px solid rgba(255,255,255,0.12)",
            opacity: farIn[i] * 0.85,
            transform: `translateZ(${60 * farIn[i]}px)`,
          }}
        >
          <Photo img={o.img} crop={o.crop} width={o.n.w} height={o.n.h} />
        </div>
      ))}
    </div>
  );
};

// ---------- editorial contact sheet beat
const SHEET = [
  { img: IMG.cakeSrc, label: "SOURCE", crop: { x: 925, y: 465, w: 430, h: 430 } },
  { img: IMG.rWarm, label: "WARM", crop: { x: 560, y: 220, w: 520, h: 520 } },
  { img: IMG.cakeMoon, label: "EARTHRISE", crop: { x: 900, y: 420, w: 540, h: 540 } },
  { img: IMG.rCool, label: "COOL", crop: { x: 560, y: 220, w: 520, h: 520 } },
  { img: IMG.rGolden, label: "GOLDEN", crop: { x: 560, y: 220, w: 520, h: 520 } },
  { img: IMG.rMono, label: "MONO", crop: { x: 560, y: 220, w: 520, h: 520 } },
];
const TILE = 262;
const TILE_GAP = 24;
const ROW_X = 960 - (SHEET.length * TILE + (SHEET.length - 1) * TILE_GAP) / 2;
const ROW_Y = 540 - TILE / 2 - 20;

const Sheet: React.FC<{ t: number }> = ({ t }) => {
  // t local to the beat
  const expand = prog(t, 0.24, 0.37, E.inOutQuart);
  // H's opening view (zoom 1.5 around the cake) — keeps the hand-off seamless
  const hView = viewForZoom(1.5, CAKE_SCREEN.x, CAKE_SCREEN.y);
  const srcCrop = SHEET[0].crop;
  const crop = lerpRect(srcCrop, hView, expand);
  const box = {
    x: ROW_X * (1 - expand),
    y: ROW_Y * (1 - expand),
    w: TILE + (1920 - TILE) * expand,
    h: TILE + (1080 - TILE) * expand,
  };
  return (
    <AbsoluteFill style={{ background: C.yellow, overflow: "hidden" }}>
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0, opacity: 1 - expand }}>
        {SHEET.slice(1).map((_, i) => {
          const x0 = ROW_X + TILE / 2;
          const x1 = ROW_X + (i + 1) * (TILE + TILE_GAP) + TILE / 2;
          const y = ROW_Y + TILE + 26;
          const p = prog(t, 0.05 + i * 0.03, 0.2 + i * 0.03, E.inOutCubic);
          return (
            <path
              key={i}
              d={`M${x0} ${y} C ${x0} ${y + 90 + i * 18}, ${x1} ${y + 90 + i * 18}, ${x1} ${y}`}
              stroke={C.ink}
              strokeOpacity={0.55}
              strokeWidth={1.6}
              fill="none"
              pathLength={1}
              strokeDasharray="1 1"
              strokeDashoffset={1 - p}
            />
          );
        })}
      </svg>
      {SHEET.map((s, i) => {
        if (i === 0) return null;
        const x = ROW_X + i * (TILE + TILE_GAP);
        const a = prog(t, i * 0.025, 0.12 + i * 0.025, E.outExpo);
        return (
          <div key={s.label} style={{ position: "absolute", left: x + (1 - a) * 260, top: ROW_Y, opacity: (1 - expand) * clamp01(a * 2) }}>
            <Photo img={s.img} crop={s.crop} width={TILE} height={TILE} />
            <MonoLabel text={s.label} color={C.ink} size={15} weight={700} style={{ position: "absolute", left: 0, top: -30 }} />
            <BBox x={0} y={0} w={TILE} h={TILE} p={a} color={C.ink} handleFill={C.white} handle={11} />
          </div>
        );
      })}
      <div style={{ position: "absolute", left: box.x, top: box.y, width: box.w, height: box.h }}>
        <Photo img={SHEET[0].img} crop={crop} width={box.w} height={box.h} />
      </div>
      <div style={{ position: "absolute", left: ROW_X, top: ROW_Y, opacity: 1 - expand }}>
        <MonoLabel text="SOURCE" color={C.ink} size={15} weight={700} style={{ position: "absolute", left: 0, top: -30 }} />
        <BBox x={0} y={0} w={TILE} h={TILE} p={prog(t, 0, 0.1)} color={C.ink} handleFill={C.yellow} handle={11} />
      </div>
      <div style={{ position: "absolute", left: 72, top: 64, opacity: 1 - expand }}>
        <Tag text="6 DIRECTIONS · 1 SOURCE" bg={C.ink} color={C.yellow} size={15} p={prog(t, 0, 0.12)} />
      </div>
      <MonoLabel text="SAME CAKE / NEW LIGHT" color={C.ink} size={14} p={prog(t, 0.04, 0.2)} style={{ position: "absolute", right: 72, top: 70, textAlign: "right", opacity: 1 - expand }} />
    </AbsoluteFill>
  );
};

const SHEET_T = 44 / 30;

const Inner: React.FC = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = f / fps;
  if (t >= SHEET_T) return <Sheet t={t - SHEET_T} />;
  const cam = camAt(t);
  return (
    <AbsoluteFill style={{ background: C.ink }}>
      <Stage3D perspective={PERSP}>
        <Plane3D cam={cam} width={CW} height={CH}>
          <Canvas t={t} />
        </Plane3D>
      </Stage3D>
      <TiltShift top={0.24 * prog(t, 0.2, 0.6)} bottom={0.12 * prog(t, 0.2, 0.6)} blur={7} />
      <MonoLabel text="SPACELAB · CANVAS" p={prog(t, 0.3, 0.6)} color="rgba(255,255,255,0.6)" style={{ position: "absolute", left: 72, top: 64 }} />
      <MonoLabel
        text={`${Math.round(kf(t, [0.45, 1.1], [0, 6]))} DIRECTIONS EXPLORED`}
        p={prog(t, 0.45, 0.7)}
        color={C.yellow}
        style={{ position: "absolute", right: 72, top: 64, textAlign: "right" }}
      />
    </AbsoluteFill>
  );
};

export const SceneExplore: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <MotionBlur
      shutterAngle={180}
      samplesAt={(fr) => {
        const t = fr / fps;
        if (t >= SHEET_T && t < SHEET_T + 1 / fps) return 1; // never blend across the cut
        if (t >= SHEET_T) return t > SHEET_T + 0.23 ? 6 : 1;
        const sp = pathSpeed(t, KEYS, ["tx", "ty"]) + pathSpeed(t, KEYS, ["z"]) * 0.5;
        return sp > 2500 ? 10 : sp > 900 ? 6 : sp > 350 ? 3 : 1;
      }}
    >
      <Inner />
    </MotionBlur>
  );
};
