import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { MotionBlur } from "../components/MotionBlur";
import { Flash, Photo, Vignette } from "../components/Media";
import { ChromaSplit } from "../components/FX";
import { BBox, MonoLabel, Tag } from "../components/Tech";
import { EyeBadge } from "../ui/Kit";
import { IMG, ImgAsset } from "../assets";
import { C, FONT } from "../theme";
import { clamp01, E, kf, prog } from "../lib/anim";
import { ICheck } from "../ui/Icons";

// Sequence-relative frames (sequence starts at film frame 462)
const CUT = 38; // "A new visual story" -> café result inside the same print
const WHIP = 82;
const END = 88;

// Inner print area and the shared cup anchor (cup body centre + width in px)
const IW = 1208;
const IH = 688;
// Mirrored source crop and café crop solved so the cup body lands on the same spot.
const CROP_SRC = { x: 692.9, y: 465.6, w: 644.3, h: 366.9 };
const CROP_CAFE = { x: 340.1, y: 148.8, w: 1139.6, h: 649.1 };
const CUP = { x: 664, y: 358, w: 300 };

const FRAMES: { img: ImgAsset; crop: { x: number; y: number; w: number; h: number } }[] = [
  { img: IMG.cupCafe, crop: { x: 340.1, y: 148.8, w: 1139.6, h: 641 } },
  { img: IMG.cupCafe, crop: { x: 600, y: 250, w: 680, h: 382 } },
  { img: IMG.alt02, crop: { x: 300, y: 80, w: 1100, h: 619 } },
  { img: IMG.cupCafe, crop: { x: 1080, y: 520, w: 590, h: 332 } },
  { img: IMG.commission, crop: { x: 0, y: 180, w: 1150, h: 647 } },
  { img: IMG.alt02, crop: { x: 560, y: 220, w: 700, h: 394 } },
];
const FW = 480;
const FH = 270;
const GAPX = 28;
const GAPY = 64;
const GS = 1.06; // final grid scale

const Inner: React.FC = () => {
  const f = useCurrentFrame();
  const cafe = f >= CUT;

  // print placement
  const drop = prog(f, 0, 10, E.outExpo);
  const push = kf(f, [0, CUT], [1.0, 1.045], E.linear);
  // storyboard: the print (frame 01) shrinks into the top-left cell of a 3×2 grid
  const toStrip = prog(f, CUT + 4, CUT + 22, E.inOutQuart);
  const whip = prog(f, WHIP, END, E.inExpo);
  const s0 = IW / FW;
  const s = s0 + (GS - s0) * toStrip;
  const gridW = (3 * FW + 2 * GAPX) * GS;
  const gridH = (2 * FH + GAPY) * GS;
  const gx0 = 960 - (FW * s0) / 2;
  const gy0 = 540 - (FH * s0) / 2 + (1 - drop) * -120;
  const gx1 = 960 - gridW / 2;
  const gy1 = 540 - gridH / 2 + 26;
  const ox = gx0 + (gx1 - gx0) * toStrip - whip * 2600;
  const oy = gy0 + (gy1 - gy0) * toStrip;

  const chroma = cafe ? kf(f, [CUT, CUT + 2], [12, 0], E.outCubic) : 0;
  const focus = prog(f, 9, 14, E.outBack);
  const sweep = prog(f, 60, 84, E.linear);
  const active = sweep > 0 && sweep < 1 ? Math.min(5, Math.floor(sweep * 6)) : -1;

  const frameRect = (i: number) => ({
    x: ox + (i % 3) * (FW + GAPX) * s,
    y: oy + Math.floor(i / 3) * (FH + GAPY) * s,
    w: FW * s,
    h: FH * s,
  });

  // print geometry (frame 01 drawn as the print itself, with a white border)
  const r0 = frameRect(0);
  const border = 16 * (1 - toStrip) + 4 * toStrip;
  const rot = (1 - drop) * -6 + -1.5 * (1 - toStrip);

  return (
    <AbsoluteFill style={{ background: C.ink, overflow: "hidden" }}>
      <AbsoluteFill
        style={{
          backgroundImage: "radial-gradient(rgba(255,255,255,0.07) 1.2px, transparent 1.2px)",
          backgroundSize: "28px 28px",
          transform: `translateX(${-whip * 1400}px)`,
        }}
      />
      <ChromaSplit amount={chroma}>
        <AbsoluteFill style={{ transform: `scale(${push})`, transformOrigin: "960px 540px" }}>
          {/* other storyboard frames */}
          {FRAMES.map((fr, i) => {
            if (i === 0) return null;
            const r = frameRect(i);
            const a = prog(f, CUT + 10 + i * 2.5, CUT + 18 + i * 2.5, E.outExpo);
            const on = active === i;
            return (
              <div key={i} style={{ position: "absolute", left: r.x + (1 - a) * 260, top: r.y + (1 - a) * 40, opacity: clamp01(a * 2) }}>
                <div
                  style={{
                    background: on ? C.yellow : "#fff",
                    padding: on ? 6 : 4,
                    margin: on ? -2 : 0,
                    borderRadius: 4,
                    boxShadow: "0 24px 50px rgba(0,0,0,0.55)",
                  }}
                >
                  <Photo img={fr.img} crop={fr.crop} width={r.w} height={r.h} />
                </div>
                <MonoLabel text={`FRAME 0${i + 1}`} color={on ? C.yellow : "rgba(255,255,255,0.7)"} size={16} style={{ position: "absolute", left: 0, top: -30 }} />
              </div>
            );
          })}
          {/* the print / frame 01 */}
          <div
            style={{
              position: "absolute",
              left: r0.x - border,
              top: r0.y - border,
              padding: active === 0 ? border + 2 : border,
              background: active === 0 ? C.yellow : "#FFFFFF",
              borderRadius: 6,
              transform: `rotate(${rot}deg)`,
              boxShadow: `0 ${50 * (1 - toStrip) + 10}px ${100 * (1 - toStrip) + 20}px rgba(0,0,0,0.6)`,
            }}
          >
            <div style={{ position: "relative", width: r0.w, height: r0.h, overflow: "hidden" }}>
              <Photo
                img={cafe ? IMG.cupCafe : IMG.cupSrc}
                crop={cafe ? CROP_CAFE : CROP_SRC}
                flip={!cafe}
                width={r0.w}
                height={r0.h}
              />
              {/* viewfinder focus on the cup (shared anchor) */}
              {focus > 0 ? (
                <div
                  style={{
                    position: "absolute",
                    left: ((CUP.x - CUP.w * 0.75) / IW) * r0.w,
                    top: ((CUP.y - CUP.w * 0.72) / IH) * r0.h,
                    width: ((CUP.w * 1.5) / IW) * r0.w,
                    height: ((CUP.w * 1.44) / IH) * r0.h,
                    opacity: 1 - toStrip,
                  }}
                >
                  <BBox x={0} y={0} w={((CUP.w * 1.5) / IW) * r0.w} h={((CUP.w * 1.44) / IH) * r0.h} p={focus} label={cafe ? "SAME CUP ✓" : "CUP · TEAL HANDLE"} labelSize={16} />
                </div>
              ) : null}
            </div>
          </div>
          <MonoLabel
            text={cafe ? "FRAME 01" : "PHOTO_02 · cup.jpg"}
            color={active === 0 ? C.yellow : "rgba(255,255,255,0.75)"}
            size={16}
            p={prog(f, 4, 14)}
            style={{ position: "absolute", left: r0.x - border, top: r0.y - border - 30 }}
          />
          {!cafe ? (
            <MonoLabel
              text="RAW · 1672×940"
              color="rgba(255,255,255,0.5)"
              size={14}
              p={prog(f, 8, 18)}
              style={{ position: "absolute", left: r0.x + r0.w - 200, top: r0.y + r0.h + border + 14, width: 200, textAlign: "right" }}
            />
          ) : null}
        </AbsoluteFill>
      </ChromaSplit>
      <Vignette strength={0.4} />
      {/* workflow chip */}
      <div
        style={{
          position: "absolute",
          left: 72,
          bottom: 64,
          display: "flex",
          alignItems: "center",
          gap: 12,
          padding: "10px 16px 10px 10px",
          borderRadius: 14,
          background: "rgba(10,10,10,0.8)",
          border: `1px solid ${C.lineStrong}`,
          fontFamily: FONT.ui,
          fontWeight: 600,
          fontSize: 20,
          color: C.text,
          opacity: prog(f, CUT + 14, CUT + 20) * (1 - whip),
          transform: `translateY(${(1 - prog(f, CUT + 14, CUT + 22, E.outExpo)) * 20}px)`,
        }}
      >
        <EyeBadge size={34} />
        Cinematic Ad Sequence
        <span style={{ color: C.textMuted, fontWeight: 500, fontSize: 16 }}>· 6 frames</span>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", width: 26, height: 26, borderRadius: 8, background: C.yellow }}>
          <ICheck size={16} color={C.ink} stroke={3} />
        </div>
      </div>
      {cafe ? (
        <div style={{ position: "absolute", right: 72, top: 64, opacity: 1 - whip }}>
          <Tag text="A NEW VISUAL STORY" p={prog(f, CUT + 8, CUT + 16)} size={16} />
        </div>
      ) : null}
      <Flash o={kf(f, [0, 6], [1, 0], E.outCubic)} />
    </AbsoluteFill>
  );
};

export const SceneCup: React.FC = () => (
  <MotionBlur
    shutterAngle={200}
    samplesAt={(fr) => {
      if (fr >= CUT && fr < CUT + 1) return 1;
      if (fr >= WHIP) return 16;
      if (fr >= CUT + 5 && fr < CUT + 22) return 6;
      return 1;
    }}
    smearAt={(fr) => ({ x: fr >= WHIP + 1 ? Math.min(70, (fr - WHIP) * 12) : 0, y: 0 })}
  >
    <Inner />
  </MotionBlur>
);
