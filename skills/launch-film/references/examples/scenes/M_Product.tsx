import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { MotionBlur } from "../components/MotionBlur";
import { Placed } from "../components/Media";
import { BBox, Crosshair, Guides, MonoLabel, Ruler, Tag } from "../components/Tech";
import { IMG } from "../assets";
import { C, FONT } from "../theme";
import { E, kf, prog } from "../lib/anim";
import { CHAIR_C, CHAIR_SRC, CHAIR_WIN } from "../lib/chairView";

// Sequence-relative frames (starts at film frame 550). "product" ≈ 12.
const W = CHAIR_WIN;

const Inner: React.FC = () => {
  const f = useCurrentFrame();
  const slide = 1 - prog(f, 0, 7, E.outExpo);
  const tx = slide * 1700;
  const guides = prog(f, 2, 12, E.inOutCubic);
  const win = prog(f, 3, 11, E.outExpo);
  const box = prog(f, 11, 17, E.outExpo);
  const push = kf(f, [0, 32], [1.0, 1.03], E.linear);
  const xs = [W.x, W.x + W.w, 1290, 1830];
  const ys = [W.y, W.y + W.h, CHAIR_C.y];

  // window opens from the chair centre outwards
  const wx = CHAIR_C.x - (CHAIR_C.x - W.x) * win;
  const wy = CHAIR_C.y - (CHAIR_C.y - W.y) * win;
  const ww = W.w * win;
  const wh = W.h * win;

  return (
    <AbsoluteFill style={{ background: C.paper, overflow: "hidden" }}>
      <AbsoluteFill style={{ transform: `translateX(${tx}px) scale(${push})`, transformOrigin: `${CHAIR_C.x}px ${CHAIR_C.y}px` }}>
        <Guides xs={xs} ys={ys} p={guides} color="rgba(10,10,10,0.22)" thickness={1.5} squares squareP={prog(f, 8, 14)} squareSize={12} origin={{ x: CHAIR_C.x, y: CHAIR_C.y }} />
        <Ruler x={W.x} y={W.y - 22} length={W.w} p={prog(f, 6, 16)} color="rgba(10,10,10,0.45)" />
        <Ruler x={W.x - 22} y={W.y} length={W.h} vertical p={prog(f, 6, 16)} color="rgba(10,10,10,0.45)" />
        {/* the product, seen through a window cut into the sheet */}
        <div style={{ position: "absolute", left: wx, top: wy, width: ww, height: wh, overflow: "hidden" }}>
          <div style={{ position: "absolute", left: -wx, top: -wy, width: 1920, height: 1080 }}>
            <Placed img={IMG.chairSrc} scale={CHAIR_SRC.s} x={CHAIR_SRC.x} y={CHAIR_SRC.y} flip />
          </div>
        </div>
        <BBox x={W.x} y={W.y} w={W.w} h={W.h} p={box} color={C.ink} handleFill={C.yellow} handle={13} label="YOUR PRODUCT" tagBg={C.ink} tagColor={C.yellow} labelSize={18} thickness={2} />
        <Crosshair x={CHAIR_C.x} y={CHAIR_C.y} size={30} color={C.yellow} p={box} thickness={2} />
        {/* specimen sheet copy */}
        <div style={{ position: "absolute", left: 1290, top: 300, width: 540 }}>
          <Tag text="PRODUCT_03" bg={C.ink} color={C.yellow} size={18} p={prog(f, 8, 14)} />
          <div
            style={{
              marginTop: 26,
              fontFamily: FONT.display,
              fontSize: 76,
              lineHeight: 1,
              color: C.ink,
              clipPath: `inset(0 ${(1 - prog(f, 10, 18, E.outExpo)) * 100}% 0 0)`,
            }}
          >
            Armchair
          </div>
          <MonoLabel text={"OLIVE UPHOLSTERY\nWOODEN ARMS + FRAME\nSOURCE · chair.png"} p={prog(f, 12, 24)} color="rgba(10,10,10,0.7)" size={18} style={{ marginTop: 26, lineHeight: 1.6 }} />
        </div>
        <MonoLabel text="SPECIMEN SHEET / 03" p={prog(f, 4, 14)} color="rgba(10,10,10,0.6)" size={14} style={{ position: "absolute", left: 72, top: 64 }} />
        <MonoLabel text="X 673   Y 627" p={prog(f, 6, 16)} color="rgba(10,10,10,0.6)" size={14} style={{ position: "absolute", right: 72, bottom: 64, textAlign: "right" }} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const SceneProduct: React.FC = () => (
  <MotionBlur samplesAt={(fr) => (fr >= 1 && fr < 7 ? 12 : 1)} shutterAngle={200} smearAt={(fr) => ({ x: fr >= 1 && fr < 6 ? Math.max(0, 40 - fr * 7) : 0, y: 0 })}>
    <Inner />
  </MotionBlur>
);
