import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { MotionBlur } from "../components/MotionBlur";
import { Photo } from "../components/Media";
import { BBox, Crosshair, MonoLabel } from "../components/Tech";
import { EyeBadge } from "../ui/Kit";
import { IMG, ImgAsset } from "../assets";
import { C, FONT } from "../theme";
import { E, kf, prog } from "../lib/anim";

const FLASH: { img: ImgAsset; crop?: { x: number; y: number; w: number; h: number } }[] = [
  { img: IMG.cakeMoon, crop: { x: 820, y: 330, w: 700, h: 600 } },
  { img: IMG.cupCafe, crop: { x: 560, y: 180, w: 700, h: 700 } },
  { img: IMG.chairPoster, crop: { x: 120, y: 150, w: 900, h: 790 } },
  { img: IMG.rGolden, crop: { x: 560, y: 220, w: 520, h: 480 } },
  { img: IMG.alt01, crop: { x: 300, y: 80, w: 800, h: 800 } },
  { img: IMG.alt02, crop: { x: 520, y: 140, w: 720, h: 720 } },
  { img: IMG.rDusk, crop: { x: 560, y: 220, w: 520, h: 480 } },
  { img: IMG.alt03, crop: { x: 520, y: 100, w: 760, h: 760 } },
];

const LETTERS = "WORKFLOWS".split("");

const Creative: React.FC<{ f: number }> = ({ f }) => {
  const inP = prog(f, 0, 7, E.outExpo);
  const drift = kf(f, [0, 17], [0, -30], E.linear);
  const gap = 250 + 40 * inP;
  const idx = Math.min(FLASH.length - 1, Math.floor(Math.max(0, f - 1) / 2));
  const win = prog(f, 0, 6, E.outBack);
  const fs = 300;
  return (
    <AbsoluteFill style={{ background: C.yellow, overflow: "hidden" }}>
      <div
        style={{
          position: "absolute",
          right: 960 + gap + drift - (1 - inP) * 600,
          top: 540 - fs * 0.62,
          fontFamily: FONT.display,
          fontSize: fs,
          lineHeight: 1,
          color: C.ink,
          whiteSpace: "nowrap",
          letterSpacing: "-0.01em",
        }}
      >
        CREA
      </div>
      <div
        style={{
          position: "absolute",
          left: 960 + gap - drift - (1 - inP) * 600,
          top: 540 - fs * 0.62,
          fontFamily: FONT.display,
          fontSize: fs,
          lineHeight: 1,
          color: C.ink,
          whiteSpace: "nowrap",
          letterSpacing: "-0.01em",
        }}
      >
        TIVE
      </div>
      <div
        style={{
          position: "absolute",
          left: 960 - 220,
          top: 540 - 220,
          width: 440,
          height: 440,
          transform: `scale(${0.4 + 0.6 * win})`,
          boxShadow: "0 30px 60px rgba(90,60,0,0.35)",
        }}
      >
        <Photo img={FLASH[idx].img} crop={FLASH[idx].crop} width={440} height={440} />
      </div>
      <BBox x={960 - 220} y={540 - 220} w={440} h={440} p={prog(f, 2, 9)} color={C.ink} handleFill={C.yellow} label={`OUTPUT_0${idx + 1}`} tagBg={C.ink} tagColor={C.yellow} labelSize={14} />
      <Crosshair x={960} y={540} color={C.white} size={24} p={prog(f, 3, 8)} />
      <MonoLabel text="SECTION 02 / CREATIVE" p={prog(f, 1, 9)} color={C.ink} style={{ position: "absolute", left: 72, top: 64 }} />
      <MonoLabel text="SPACES · PREPARED" p={prog(f, 3, 11)} color={C.ink} style={{ position: "absolute", right: 72, top: 64, textAlign: "right" }} />
      <MonoLabel text="IDEA → WORKFLOW → IMAGE" p={prog(f, 5, 13)} color={C.ink} style={{ position: "absolute", left: 72, bottom: 64 }} />
    </AbsoluteFill>
  );
};

const Workflows: React.FC<{ f: number }> = ({ f }) => {
  // f is local to this beat (0 at the cut). Natural kerning; a node rail runs under the word
  // and a yellow signal travels through it like a workflow executing.
  const fs = 228;
  const run = prog(f, 1, 14, E.inOutCubic);
  const collapse = prog(f, 15, 23, E.inOutQuart);
  const badge = prog(f, 16, 23, E.outBack);
  const enter = prog(f, 0, 5, E.outExpo);
  const n = LETTERS.length;
  return (
    <AbsoluteFill style={{ background: C.ink, overflow: "hidden" }}>
      <AbsoluteFill
        style={{
          backgroundImage: "radial-gradient(rgba(255,255,255,0.08) 1.2px, transparent 1.2px)",
          backgroundSize: "30px 30px",
          opacity: 0.8,
        }}
      />
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
        <div
          style={{
            position: "relative",
            display: "flex",
            alignItems: "flex-end",
            transform: `scale(${1 - 0.8 * collapse})`,
            opacity: 1 - collapse,
            filter: collapse > 0.05 ? `blur(${collapse * 8}px)` : undefined,
            marginTop: -40,
          }}
        >
          {/* rail */}
          <div style={{ position: "absolute", left: 40, right: 40, bottom: -46, height: 4, borderRadius: 2, background: "rgba(255,255,255,0.18)" }} />
          <div
            style={{
              position: "absolute",
              left: 40,
              bottom: -46,
              height: 4,
              borderRadius: 2,
              width: `calc((100% - 80px) * ${run})`,
              background: C.yellow,
              boxShadow: "0 0 18px rgba(254,204,21,0.7)",
            }}
          />
          {LETTERS.map((ch, i) => {
            const at = i / (n - 1);
            const lit = run >= at - 0.001;
            const pop = prog(run, at - 0.05, at + 0.03, E.outBack) * (1 - prog(run, at + 0.06, at + 0.16));
            return (
              <div
                key={i}
                style={{
                  position: "relative",
                  fontFamily: FONT.display,
                  fontSize: fs,
                  lineHeight: 1,
                  color: lit ? C.yellow : C.white,
                  transform: `translateY(${(1 - enter) * (i % 2 ? 160 : -160)}px) scale(${1 + 0.07 * pop})`,
                  transformOrigin: "50% 100%",
                }}
              >
                {ch}
                <div
                  style={{
                    position: "absolute",
                    left: "50%",
                    bottom: -55,
                    width: 22,
                    height: 22,
                    marginLeft: -11,
                    borderRadius: 999,
                    background: lit ? C.yellow : C.ink,
                    border: `3px solid ${lit ? C.yellow : "rgba(255,255,255,0.45)"}`,
                    boxSizing: "border-box",
                    boxShadow: lit ? "0 0 14px rgba(254,204,21,0.8)" : undefined,
                  }}
                />
              </div>
            );
          })}
        </div>
      </AbsoluteFill>
      <MonoLabel text={`STEP ${String(Math.min(9, 1 + Math.floor(run * 8.99))).padStart(2, "0")} / 09`} p={prog(f, 1, 6)} color="rgba(255,255,255,0.6)" style={{ position: "absolute", left: 72, top: 64 }} />
      <MonoLabel text="RUNNING ·  ·  ·" p={prog(f, 2, 8)} color={C.yellow} style={{ position: "absolute", right: 72, top: 64, textAlign: "right" }} />
      {badge > 0 ? (
        <div style={{ position: "absolute", left: 960 - 75, top: 540 - 75, transform: `scale(${badge})` }}>
          <EyeBadge size={150} look={{ x: kf(f, [16, 20, 23], [0, -0.8, 0]), y: 0 }} />
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

const Inner: React.FC = () => {
  const f = useCurrentFrame();
  return f < 17 ? <Creative f={f} /> : <Workflows f={f - 17} />;
};

export const SceneCreative: React.FC = () => (
  <MotionBlur samplesAt={(fr) => (fr < 6 || (fr >= 18 && fr < 22) || fr >= 31 ? 8 : 1)} shutterAngle={180}>
    <Inner />
  </MotionBlur>
);
