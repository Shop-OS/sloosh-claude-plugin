import React, { useMemo } from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { C, FONT } from "../theme";
import { E, prog } from "../lib/anim";
import { BBox, MonoLabel } from "../components/Tech";
import { Photo, Vignette } from "../components/Media";
import type { ImgAsset } from "../assets";
import { Rect, rectToScreen } from "../lib/cropCamera";

let seq = 0;

export type DetailWindow = { r: Rect; label: string; at: number; chip?: string; labelPos?: "top" | "bottom" };

/**
 * A full-frame photo seen through a view rect with detail windows opened over features;
 * everything outside the windows is dimmed. Windows are in image pixels so they stay pinned
 * while `view` animates. Optional readout panel lists the details (typed on).
 */
export const DetailWindows: React.FC<{
  img: ImgAsset;
  view: Rect;
  windows: DetailWindow[];
  dim?: number;
  accent?: string;
  readout?: { title: string; rows: string[]; at: number; x?: number; y?: number };
  flip?: boolean;
}> = ({ img, view, windows, dim = 0.55, accent = C.accent, readout, flip = false }) => {
  const f = useCurrentFrame();
  const id = useMemo(() => `dw${seq++}`, []);
  const d = prog(f, 2, 10) * dim;
  return (
    <AbsoluteFill style={{ background: C.ink }}>
      <Photo img={img} crop={view} width={1920} height={1080} flip={flip} />
      <Vignette strength={0.3} />
      {d > 0.001 ? (
        <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
          <defs>
            <mask id={id}>
              <rect x={0} y={0} width={1920} height={1080} fill="white" />
              {windows.map((w, i) => {
                const r = rectToScreen(view, w.r);
                const a = prog(f, w.at, w.at + 5, E.outExpo);
                return <rect key={i} x={r.x} y={r.y} width={r.w * a} height={r.h} fill="black" />;
              })}
            </mask>
          </defs>
          <rect x={0} y={0} width={1920} height={1080} fill="#050505" opacity={d} mask={`url(#${id})`} />
        </svg>
      ) : null}
      {windows.map((w, i) => {
        const r = rectToScreen(view, w.r);
        const a = prog(f, w.at, w.at + 6, E.outExpo);
        return (
          <React.Fragment key={i}>
            <BBox x={r.x} y={r.y} w={r.w} h={r.h} p={a} color={accent} label={w.label} labelSize={15} labelPos={w.labelPos ?? "top"} />
            {w.chip ? (
              <div
                style={{
                  position: "absolute",
                  left: r.x + r.w + 10,
                  top: r.y + r.h / 2 - 15,
                  background: C.ink,
                  border: `1px solid ${accent}`,
                  color: accent,
                  fontFamily: FONT.mono,
                  fontSize: 13,
                  fontWeight: 700,
                  padding: "5px 8px",
                  opacity: prog(f, w.at + 3, w.at + 7),
                }}
              >
                {w.chip}
              </div>
            ) : null}
          </React.Fragment>
        );
      })}
      {readout ? (
        <div
          style={{
            position: "absolute",
            left: readout.x ?? 86,
            top: readout.y ?? 330,
            width: 470,
            padding: "22px 24px",
            background: "rgba(10,10,10,0.78)",
            border: `1px solid ${accent}`,
            opacity: prog(f, readout.at, readout.at + 6),
          }}
        >
          <MonoLabel text={readout.title} color={accent} size={16} weight={700} />
          <div style={{ height: 1, background: accent, opacity: 0.4, margin: "14px 0" }} />
          {readout.rows.map((row, i) => (
            <MonoLabel key={row} text={row} p={prog(f, readout.at + 4 + i * 6, readout.at + 12 + i * 6)} color={C.text} size={16} style={{ marginBottom: 10 }} />
          ))}
        </div>
      ) : null}
    </AbsoluteFill>
  );
};
