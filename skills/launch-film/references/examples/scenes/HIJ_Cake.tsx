import React, { useMemo } from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { MotionBlur } from "../components/MotionBlur";
import { Flash, Photo, Vignette } from "../components/Media";
import { ChromaSplit } from "../components/FX";
import { BBox, Crosshair, MonoLabel } from "../components/Tech";
import { EyeBadge } from "../ui/Kit";
import { IMG } from "../assets";
import { C, FONT } from "../theme";
import { clamp01, E, kf, prog } from "../lib/anim";
import { CAKE_SCREEN, Rect, toScreen, to17, viewForZoom } from "../lib/cakeView";
import { ICheck, ILock } from "../ui/Icons";

// Sequence-relative frame markers (sequence starts at film frame 330)
const M = {
  details: 10,
  yoursCut: 46,
  yoursBack: 51,
  moonCut: 99,
  end: 132,
};

// Detail windows in I10 logical pixels
const WINDOWS = [
  { r: { x: 1052, y: 526, w: 176, h: 80 }, label: "STRAWBERRIES ×3", at: 10 },
  { r: { x: 964, y: 572, w: 150, h: 60 }, label: "PIPED RIM", at: 15 },
  { r: { x: 1166, y: 640, w: 140, h: 112 }, label: "BUTTERCREAM", at: 20 },
];
const SHAPE = { x: 958, y: 520, w: 362, h: 252 };

const READOUT = ["ICING ............ KEPT", "STRAWBERRIES ×3 .. KEPT", "PIPED RIM ........ KEPT", "SILHOUETTE ....... KEPT"];

const zoomAt = (f: number) => {
  if (f < M.yoursBack) return kf(f, [0, M.yoursCut], [1.5, 1.78], E.linear);
  if (f < M.moonCut) return kf(f, [M.yoursBack, M.moonCut - 4], [1.78, 1.0], E.inOutCubic);
  return kf(f, [M.moonCut, M.end], [1.0, 1.1], E.outCubic);
};

const screenRect = (view: Rect, r: Rect) => {
  const a = toScreen(view, r.x, r.y);
  const b = toScreen(view, r.x + r.w, r.y + r.h);
  return { x: a.x, y: a.y, w: b.x - a.x, h: b.y - a.y };
};

let maskSeq = 0;

const Inner: React.FC = () => {
  const f = useCurrentFrame();
  const maskId = useMemo(() => `cutouts${maskSeq++}`, []);
  const k = zoomAt(f);
  const view = viewForZoom(k, CAKE_SCREEN.x, CAKE_SCREEN.y);
  const onMoon = f >= M.moonCut;

  if (f >= M.yoursCut && f < M.yoursBack) {
    // punctuation frame
    const s = kf(f, [M.yoursCut, M.yoursBack], [1.08, 1.0], E.outCubic);
    return (
      <AbsoluteFill style={{ background: C.yellow, alignItems: "center", justifyContent: "center", overflow: "hidden" }}>
        <div style={{ fontFamily: FONT.display, fontSize: 470, color: C.ink, lineHeight: 1, transform: `scale(${s})`, letterSpacing: "-0.01em", marginTop: 40 }}>
          YOURS.
        </div>
        <MonoLabel text="DETAIL LOCK · 4/4" color={C.ink} size={15} style={{ position: "absolute", left: 72, top: 64 }} />
      </AbsoluteFill>
    );
  }

  const dim = f < M.yoursCut ? prog(f, 4, 12) * 0.55 : 0.55 * (1 - prog(f, M.yoursBack, M.yoursBack + 8));
  const shapeScr = screenRect(view, SHAPE);
  const center = toScreen(view, SHAPE.x + SHAPE.w / 2, SHAPE.y + SHAPE.h / 2);
  const chroma = onMoon ? kf(f, [M.moonCut, M.moonCut + 2], [12, 0], E.outCubic) : 0;

  const img = onMoon ? IMG.cakeMoon : IMG.cakeSrc;
  const crop = onMoon ? to17(view) : view;

  // labels for the shape box per phase
  const shapeVisible =
    f < M.yoursCut ? prog(f, 26, 32) : f < M.moonCut ? prog(f, M.yoursBack, M.yoursBack + 6) : 1 - prog(f, M.moonCut + 14, M.moonCut + 22);
  const shapeLabel = f < M.yoursCut ? "SILHOUETTE" : onMoon ? "ON THE MOON" : "YOUR CAKE";

  return (
    <AbsoluteFill style={{ background: C.ink }}>
      <ChromaSplit amount={chroma}>
        <Photo img={img} crop={crop} width={1920} height={1080} />
        <Vignette strength={onMoon ? 0.35 : 0.3} />
        {/* dim everything but the windows during the detail lock */}
        {dim > 0.001 ? (
          <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
            <defs>
              <mask id={maskId}>
                <rect x={0} y={0} width={1920} height={1080} fill="white" />
                {f < M.yoursCut
                  ? WINDOWS.map((w, i) => {
                      const r = screenRect(view, w.r);
                      const a = prog(f, w.at, w.at + 5, E.outExpo);
                      return <rect key={i} x={r.x} y={r.y} width={r.w * a} height={r.h} fill="black" />;
                    })
                  : null}
                <rect
                  x={shapeScr.x}
                  y={shapeScr.y}
                  width={shapeScr.w}
                  height={shapeScr.h}
                  fill="black"
                  opacity={f < M.yoursCut ? 0.35 * prog(f, 26, 32) : 1}
                />
              </mask>
            </defs>
            <rect x={0} y={0} width={1920} height={1080} fill="#050505" opacity={dim} mask={`url(#${maskId})`} />
          </svg>
        ) : null}
      </ChromaSplit>

      {/* detail windows */}
      {f < M.yoursCut
        ? WINDOWS.map((w, i) => {
            const r = screenRect(view, w.r);
            const a = prog(f, w.at, w.at + 6, E.outExpo);
            return (
              <React.Fragment key={i}>
                <BBox x={r.x} y={r.y} w={r.w} h={r.h} p={a} label={w.label} labelSize={15} labelPos={i === 2 ? "bottom" : "top"} />
                <div
                  style={{
                    position: "absolute",
                    left: r.x + r.w + 10,
                    top: r.y + r.h / 2 - 15,
                    display: "flex",
                    alignItems: "center",
                    gap: 6,
                    background: C.ink,
                    border: `1px solid ${C.yellow}`,
                    color: C.yellow,
                    fontFamily: FONT.mono,
                    fontSize: 13,
                    fontWeight: 700,
                    padding: "5px 8px",
                    opacity: prog(f, w.at + 3, w.at + 7),
                  }}
                >
                  <ILock size={13} color={C.yellow} stroke={2.2} /> KEEP
                </div>
              </React.Fragment>
            );
          })
        : null}

      {shapeVisible > 0.001 ? (
        <>
          <BBox
            x={shapeScr.x}
            y={shapeScr.y}
            w={shapeScr.w}
            h={shapeScr.h}
            p={shapeVisible}
            dashed={f < M.yoursCut}
            label={shapeLabel}
            labelSize={18}
            labelPos={f < M.yoursCut ? "bottom" : "top"}
            tagBg={onMoon ? C.white : C.yellow}
            style={{ opacity: clamp01(shapeVisible * 1.5) }}
          />
          <Crosshair x={center.x} y={center.y} size={26} color={C.yellow} p={shapeVisible} />
        </>
      ) : null}

      {/* detail-lock readout */}
      {f < M.yoursCut ? (
        <div
          style={{
            position: "absolute",
            left: 86,
            top: 330,
            width: 470,
            padding: "22px 24px",
            background: "rgba(10,10,10,0.78)",
            border: `1px solid rgba(254,204,21,0.6)`,
            opacity: prog(f, 8, 14),
            transform: `translateX(${(1 - prog(f, 8, 16, E.outExpo)) * -40}px)`,
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <MonoLabel text="DETAIL LOCK" color={C.yellow} size={16} weight={700} />
            <MonoLabel text={`${Math.min(4, Math.max(0, Math.floor((f - 10) / 6) + 1))}/4`} color={C.yellow} size={16} weight={700} />
          </div>
          <div style={{ height: 1, background: "rgba(254,204,21,0.4)", margin: "14px 0" }} />
          {READOUT.map((row, i) => (
            <MonoLabel key={row} text={row} p={prog(f, 12 + i * 6, 20 + i * 6)} color={C.text} size={16} style={{ marginBottom: 10 }} />
          ))}
        </div>
      ) : null}

      {/* source / result labels */}
      {!onMoon && f >= M.yoursBack ? (
        <MonoLabel text="SOURCE_01 · cake.jpg" p={prog(f, M.yoursBack + 4, M.yoursBack + 14)} color="rgba(255,255,255,0.75)" size={15} style={{ position: "absolute", left: 72, bottom: 64 }} />
      ) : null}
      {onMoon ? (
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
            background: "rgba(10,10,10,0.72)",
            border: `1px solid ${C.lineStrong}`,
            fontFamily: FONT.ui,
            fontWeight: 600,
            fontSize: 20,
            color: C.text,
            opacity: prog(f, M.moonCut + 4, M.moonCut + 10),
            transform: `translateY(${(1 - prog(f, M.moonCut + 4, M.moonCut + 12, E.outExpo)) * 20}px)`,
          }}
        >
          <EyeBadge size={34} />
          Product in Scene + Relight
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", width: 26, height: 26, borderRadius: 8, background: C.yellow }}>
            <ICheck size={16} color={C.ink} stroke={3} />
          </div>
        </div>
      ) : null}
      {onMoon ? (
        <MonoLabel text="OUTPUT · V2 EARTHRISE" p={prog(f, M.moonCut + 6, M.moonCut + 16)} color="rgba(255,255,255,0.75)" size={15} style={{ position: "absolute", right: 72, bottom: 72, textAlign: "right" }} />
      ) : null}
      {/* shutter flash into the photograph beat */}
      <Flash o={kf(f, [M.end - 4, M.end - 0.5], [0, 1], E.inCubic)} />
    </AbsoluteFill>
  );
};

export const SceneCake: React.FC = () => (
  <MotionBlur
    shutterAngle={180}
    samplesAt={(fr) => {
      // only the pull-back moves fast enough to need blur; never blend across cuts
      if (fr >= M.yoursBack + 1 && fr < M.moonCut - 4) return 4;
      return 1;
    }}
  >
    <Inner />
  </MotionBlur>
);
