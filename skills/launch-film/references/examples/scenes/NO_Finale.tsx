import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { MotionBlur } from "../components/MotionBlur";
import { Photo, Placed } from "../components/Media";
import { ChromaSplit } from "../components/FX";
import { MonoLabel, Tag } from "../components/Tech";
import { Cursor } from "../components/Cursor";
import { Logo } from "../brand/Logo";
import { BetaPill, OutlineBtn, YellowBtn } from "../ui/Kit";
import { IArrowRight } from "../ui/Icons";
import { IMG, ImgAsset } from "../assets";
import { C, FONT } from "../theme";
import { clamp01, E, kf, mix, prog } from "../lib/anim";
import { CHAIR_C, POSTER } from "../lib/chairView";

// Sequence-relative frames (starts at film frame 582)
const T = {
  shrink0: 3,
  shrink1: 26,
  feels: 58,
  spread1: 86,
  logo0: 64,
  you: 77,
  head0: 84,
  cta0: 100,
  cursor0: 112,
  click: 133,
};

type Box = { cx: number; cy: number; w: number; rot: number; z: number };
type Card = {
  key: string;
  img: ImgAsset;
  crop?: { x: number; y: number; w: number; h: number };
  aspect: number; // w/h
  label?: string;
  overlay?: "top" | "right";
  board?: Box;
  frame: Box;
  enter: number;
};

const CARDS: Card[] = [
  {
    key: "p169",
    img: IMG.chairPoster,
    aspect: 1672 / 941,
    label: "16:9 · BILLBOARD",
    board: { cx: 720, cy: 520, w: 900, rot: 0, z: 0 },
    frame: { cx: 315, cy: 845, w: 450, rot: 5, z: 0 },
    enter: 0,
  },
  {
    key: "p11",
    img: IMG.alt03Clean,
    crop: { x: 160, y: 60, w: 840, h: 840 },
    aspect: 1,
    label: "1:1 · FEED",
    overlay: "right",
    board: { cx: 1350, cy: 330, w: 340, rot: 0, z: 0 },
    frame: { cx: 1760, cy: 120, w: 230, rot: -7, z: 0 },
    enter: 8,
  },
  {
    key: "p45",
    img: IMG.chairPosterClean,
    crop: { x: 160, y: 0, w: 752, h: 940 },
    aspect: 0.8,
    label: "4:5 · PRINT",
    overlay: "top",
    board: { cx: 1350, cy: 790, w: 300, rot: 0, z: 0 },
    frame: { cx: 1640, cy: 860, w: 250, rot: -4, z: 0 },
    enter: 12,
  },
  {
    key: "p916",
    img: IMG.chairPosterClean,
    crop: { x: 300, y: 0, w: 529, h: 941 },
    aspect: 9 / 16,
    label: "9:16 · STORY",
    overlay: "top",
    board: { cx: 1720, cy: 560, w: 280, rot: 0, z: 0 },
    frame: { cx: 1915, cy: 560, w: 210, rot: 8, z: 0 },
    enter: 16,
  },
  { key: "cake", img: IMG.cakeMoon, aspect: 16 / 9, frame: { cx: 330, cy: 235, w: 480, rot: -6, z: 0 }, enter: 60 },
  { key: "cup", img: IMG.cupCafe, crop: { x: 560, y: 110, w: 760, h: 820 }, aspect: 760 / 820, frame: { cx: 1610, cy: 330, w: 300, rot: 6, z: 0 }, enter: 63 },
  { key: "gold", img: IMG.rGolden, aspect: 16 / 9, frame: { cx: 10, cy: 560, w: 300, rot: 7, z: 0 }, enter: 68 },
  { key: "alt01", img: IMG.alt01, aspect: 16 / 9, frame: { cx: 980, cy: 1075, w: 360, rot: -3, z: 0 }, enter: 70 },
];

const LOGO_W = 820;
const LOGO_H = (LOGO_W * 714) / 1603;
const LOGO_X = 960 - LOGO_W / 2;
const LOGO_Y = 228;
const EYES_C = { x: LOGO_X + 760 * (LOGO_W / 1603), y: LOGO_Y + 233 * (LOGO_W / 1603) };
const CTA_Y = 812;
const START_BTN = { x: 812, y: CTA_Y + 32 };

const Overlay: React.FC<{ w: number; h: number; mode: "top" | "right" }> = ({ w, h, mode }) =>
  mode === "top" ? (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        top: w * 0.09,
        textAlign: "center",
        fontFamily: FONT.ui,
        fontWeight: 300,
        fontSize: Math.max(10, w * 0.075),
        letterSpacing: "0.16em",
        color: "#2B2E24",
      }}
    >
      TAKE A MOMENT
    </div>
  ) : (
    <div
      style={{
        position: "absolute",
        right: w * 0.06,
        top: h * 0.27,
        textAlign: "right",
        fontFamily: FONT.ui,
        fontWeight: 300,
        fontSize: Math.max(10, w * 0.068),
        lineHeight: 1.25,
        letterSpacing: "0.16em",
        color: "#2B2E24",
      }}
    >
      TAKE A
      <br />
      MOMENT
    </div>
  );

const Inner: React.FC = () => {
  const f = useCurrentFrame();
  const shrink = prog(f, T.shrink0, T.shrink1, E.inOutQuart);
  const spread = prog(f, T.feels, T.spread1, E.inOutCubic);
  const chroma = kf(f, [0, 2], [12, 0], E.outCubic);
  const drift = (i: number) => Math.sin(f / 30 + i * 1.7) * 6;

  // full-frame poster that becomes the billboard card
  const P = CARDS[0];
  const fullW = 1672 * POSTER.s * 1.03;
  const fullH = 941 * POSTER.s * 1.03;
  const fullCx = CHAIR_C.x + (POSTER.x + (1672 * POSTER.s) / 2 - CHAIR_C.x) * 1.03;
  const fullCy = CHAIR_C.y + (POSTER.y + (941 * POSTER.s) / 2 - CHAIR_C.y) * 1.03;

  const boxAt = (c: Card, i: number) => {
    const b = c.board ?? c.frame;
    const cx = mix(b.cx, c.frame.cx, spread) + drift(i) * spread;
    const cy = mix(b.cy, c.frame.cy, spread) + drift(i + 3) * spread;
    const w = mix(b.w, c.frame.w, spread);
    const rot = mix(b.rot, c.frame.rot, spread);
    return { cx, cy, w, h: w / c.aspect, rot };
  };

  // logo + copy
  const reveal = [0, 1, 2, 3, 4].map((i) => prog(f, T.logo0 + i * 2, T.logo0 + 9 + i * 2, E.outExpo));
  const eyeOpen = f < T.you - 2 ? 0 : kf(f, [T.you - 2, T.you, T.you + 2, 148, 150, 152], [0, 1.12, 1, 1, 0.08, 1], E.outCubic);
  // cursor
  const cur = prog(f, T.cursor0, T.click - 3, E.inOutCubic);
  const cx = mix(1780, START_BTN.x + 40, cur);
  const cy = mix(1160, START_BTN.y + 8, cur);
  const press = prog(f, T.click - 2, T.click) * (1 - prog(f, T.click + 3, T.click + 7));
  const ripple = f >= T.click ? prog(f, T.click, T.click + 12) : -1;
  // gaze: viewer on "you", then follows the cursor, then back to the viewer
  const follow = prog(f, T.cursor0 + 4, T.cursor0 + 12) * (1 - prog(f, T.click + 6, T.click + 14));
  const lookX = mix(0, clamp01((cx - EYES_C.x) / 900 + 0.5) * 2 - 1, follow);
  const lookY = mix(0.05, Math.max(-1, Math.min(1, (cy - EYES_C.y) / 520)), follow);
  const words = ["Got", "an", "idea?", "Sloosh", "it."];
  const ctaIn = prog(f, T.cta0, T.cta0 + 10, E.outExpo);
  const push = kf(f, [T.feels, 168], [1, 1.035], E.linear);
  const bg = prog(f, T.shrink0, T.shrink1);

  return (
    <AbsoluteFill style={{ background: C.ink, overflow: "hidden" }}>
      <AbsoluteFill style={{ transform: `scale(${push})`, transformOrigin: "960px 540px" }}>
        {/* environment */}
        <AbsoluteFill
          style={{
            opacity: bg,
            backgroundImage: "radial-gradient(rgba(255,255,255,0.07) 1.2px, transparent 1.2px)",
            backgroundSize: "30px 30px",
          }}
        />
        <AbsoluteFill
          style={{
            opacity: prog(f, T.feels, T.spread1) * 0.9,
            background: "radial-gradient(60% 45% at 50% 100%, rgba(254,204,21,0.16) 0%, rgba(254,204,21,0) 70%)",
          }}
        />
        <ChromaSplit amount={chroma}>
          {CARDS.map((c, i) => {
            if (i === 0) return null;
            const a = prog(f, c.enter, c.enter + 12, E.outExpo);
            if (a <= 0) return null;
            const b = boxAt(c, i);
            const fromX = c.board ? 2300 : b.cx < 960 ? -500 : 2400;
            const x = mix(fromX, b.cx, a);
            const isExtra = !c.board;
            const blur = isExtra ? 1.6 * spread : 0;
            return (
              <div
                key={c.key}
                style={{
                  position: "absolute",
                  left: x - b.w / 2,
                  top: b.cy - b.h / 2,
                  width: b.w,
                  height: b.h,
                  transform: `rotate(${b.rot}deg)`,
                  filter: blur > 0.1 ? `blur(${blur}px)` : undefined,
                  opacity: isExtra ? 0.9 : 1,
                }}
              >
                <div style={{ position: "relative", width: b.w, height: b.h, borderRadius: 10, overflow: "hidden", boxShadow: "0 30px 70px rgba(0,0,0,0.6)" }}>
                  <Photo img={c.img} crop={c.crop} width={b.w} height={b.h} />
                  {c.overlay ? <Overlay w={b.w} h={b.h} mode={c.overlay} /> : null}
                </div>
                {c.label ? (
                  <MonoLabel text={c.label} color="rgba(255,255,255,0.7)" size={14} p={prog(f, c.enter + 6, c.enter + 16)} style={{ position: "absolute", left: 0, top: -26, opacity: 1 - spread }} />
                ) : null}
              </div>
            );
          })}
          {/* billboard: starts as the full-frame poster */}
          {(() => {
            const b = boxAt(P, 0);
            const w = mix(fullW, b.w, shrink);
            const h = mix(fullH, b.h, shrink);
            const ccx = mix(fullCx, b.cx, shrink);
            const ccy = mix(fullCy, b.cy, shrink);
            const radius = 10 * shrink;
            return (
              <div
                style={{
                  position: "absolute",
                  left: ccx - w / 2,
                  top: ccy - h / 2,
                  width: w,
                  height: h,
                  transform: `rotate(${b.rot}deg)`,
                }}
              >
                <div style={{ position: "relative", width: w, height: h, borderRadius: radius, overflow: "hidden", boxShadow: `0 30px 70px rgba(0,0,0,${0.6 * shrink})` }}>
                  <Placed img={IMG.chairPoster} scale={w / 1672} x={0} y={0} />
                </div>
                <MonoLabel text={P.label!} color="rgba(255,255,255,0.7)" size={14} p={prog(f, 18, 28)} style={{ position: "absolute", left: 0, top: -26, opacity: 1 - spread }} />
              </div>
            );
          })()}
        </ChromaSplit>
        {/* campaign tag */}
        <div style={{ position: "absolute", left: 270, top: 196, opacity: 1 - spread }}>
          <Tag text="A CAMPAIGN · 4 FORMATS" p={prog(f, 14, 24)} size={16} />
        </div>
        {/* soft scrim behind the lockup */}
        <AbsoluteFill
          style={{
            opacity: prog(f, T.logo0 - 4, T.logo0 + 10),
            background: "radial-gradient(42% 46% at 50% 50%, rgba(10,10,10,0.92) 0%, rgba(10,10,10,0.75) 55%, rgba(10,10,10,0) 100%)",
          }}
        />
        {/* lockup */}
        <div style={{ position: "absolute", left: LOGO_X, top: LOGO_Y }}>
          <Logo width={LOGO_W} reveal={reveal} eyeOpen={eyeOpen} look={{ x: lookX, y: lookY }} />
        </div>
        <div style={{ position: "absolute", left: LOGO_X + LOGO_W + 16, top: LOGO_Y + 18, opacity: prog(f, T.logo0 + 10, T.logo0 + 16) }}>
          <BetaPill scale={1.6} />
        </div>
        <div
          style={{
            position: "absolute",
            left: 0,
            right: 0,
            top: LOGO_Y + LOGO_H + 50,
            display: "flex",
            justifyContent: "center",
            gap: 22,
            fontFamily: FONT.display,
            fontSize: 84,
            lineHeight: 1,
          }}
        >
          {words.map((w, i) => {
            const p = prog(f, T.head0 + i * 3, T.head0 + 10 + i * 3, E.outExpo);
            return (
              <div key={w} style={{ overflow: "hidden", padding: "6px 0" }}>
                <div style={{ transform: `translateY(${(1 - p) * 110}%)`, color: i >= 3 ? C.yellowText : C.white }}>{w}</div>
              </div>
            );
          })}
        </div>
        <div
          style={{
            position: "absolute",
            left: 0,
            right: 0,
            top: CTA_Y,
            display: "flex",
            justifyContent: "center",
            gap: 20,
            opacity: ctaIn,
            transform: `translateY(${(1 - ctaIn) * 30}px) scale(1.12)`,
          }}
        >
          <YellowBtn
            label="Start creating"
            size="lg"
            icon={<IArrowRight size={24} color={C.ink} stroke={2.4} />}
            press={press}
            glow={prog(f, T.click, T.click + 4) * (1 - prog(f, T.click + 10, T.click + 30))}
          />
          <OutlineBtn label="Browse spaces" size="lg" />
        </div>
        <MonoLabel
          text="BETA.SLOOSH.AI"
          p={prog(f, T.cta0 + 6, T.cta0 + 18)}
          color="rgba(255,255,255,0.62)"
          size={22}
          style={{ position: "absolute", left: 0, right: 0, top: CTA_Y + 104, textAlign: "center", letterSpacing: "0.18em" }}
        />
      </AbsoluteFill>
      <Cursor x={cx} y={cy} size={44} press={press} ripple={ripple} opacity={prog(f, T.cursor0, T.cursor0 + 4)} />
    </AbsoluteFill>
  );
};

export const SceneFinale: React.FC = () => (
  <MotionBlur
    shutterAngle={180}
    samplesAt={(fr) => {
      if (fr < 1) return 1;
      if (fr >= T.shrink0 && fr < T.shrink1) return 6;
      if (fr >= T.feels && fr < T.spread1) return 5;
      return 1;
    }}
  >
    <Inner />
  </MotionBlur>
);
