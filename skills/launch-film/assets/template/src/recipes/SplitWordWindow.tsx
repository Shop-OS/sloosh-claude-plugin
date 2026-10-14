import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { FONT, C } from "../theme";
import { E, kf, prog } from "../lib/anim";
import { BBox, Crosshair } from "../components/Tech";
import { Photo } from "../components/Media";
import type { ImgAsset } from "../assets";

/**
 * Giant word split into two halves that slide apart around a square image window that
 * cycles through images every `every` frames ("CREA [img] TIVE").
 */
export const SplitWordWindow: React.FC<{
  left: string;
  right: string;
  images: { img: ImgAsset; crop?: { x: number; y: number; w: number; h: number } }[];
  bg?: string;
  color?: string;
  size?: number;
  every?: number;
  window?: number;
  tagPrefix?: string;
}> = ({ left, right, images, bg = C.accent, color = C.ink, size = 300, every = 2, window = 440, tagPrefix = "OUTPUT_0" }) => {
  const f = useCurrentFrame();
  const inP = prog(f, 0, 7, E.outExpo);
  const drift = kf(f, [0, 30], [0, -50], E.linear);
  const gap = window * 0.57 + 40 * inP;
  const idx = Math.min(images.length - 1, Math.floor(Math.max(0, f - 1) / every)) % images.length;
  const win = prog(f, 0, 6, E.outBack);
  const half = window / 2;
  return (
    <AbsoluteFill style={{ background: bg, overflow: "hidden" }}>
      <div style={{ position: "absolute", right: 960 + gap + drift - (1 - inP) * 600, top: 540 - size * 0.62, fontFamily: FONT.display, fontSize: size, lineHeight: 1, color, whiteSpace: "nowrap" }}>
        {left}
      </div>
      <div style={{ position: "absolute", left: 960 + gap - drift - (1 - inP) * 600, top: 540 - size * 0.62, fontFamily: FONT.display, fontSize: size, lineHeight: 1, color, whiteSpace: "nowrap" }}>
        {right}
      </div>
      <div style={{ position: "absolute", left: 960 - half, top: 540 - half, width: window, height: window, transform: `scale(${0.4 + 0.6 * win})`, boxShadow: "0 30px 60px rgba(0,0,0,0.3)" }}>
        <Photo img={images[idx].img} crop={images[idx].crop} width={window} height={window} />
      </div>
      <BBox x={960 - half} y={540 - half} w={window} h={window} p={prog(f, 2, 9)} color={color} handleFill={bg} label={`${tagPrefix}${idx + 1}`} tagBg={color} tagColor={bg} labelSize={14} />
      <Crosshair x={960} y={540} color={C.white} size={24} p={prog(f, 3, 8)} />
    </AbsoluteFill>
  );
};
