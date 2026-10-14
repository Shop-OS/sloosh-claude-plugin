import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { C } from "../theme";
import { clamp01, E, prog } from "../lib/anim";
import { BBox, MonoLabel, Tag } from "../components/Tech";
import { Photo } from "../components/Media";
import type { ImgAsset } from "../assets";
import { lerpRect, Rect } from "../lib/cropCamera";

export type SheetTile = { img: ImgAsset; crop: Rect; label: string };

/**
 * Editorial contact sheet: a row of square crops with labels above, corner handles and
 * thin arcs from the first (source) tile to each variant. Optionally the first tile expands
 * to full frame between `expand0` and `expand1` (frames), its crop interpolating to `expandTo`
 * — use the next scene's opening view so the hand-off is seamless.
 */
export const ContactSheet: React.FC<{
  tiles: SheetTile[];
  bg?: string;
  ink?: string;
  tile?: number;
  gap?: number;
  expand0?: number;
  expand1?: number;
  expandTo?: Rect;
  tag?: string;
  note?: string;
}> = ({ tiles, bg = C.accent, ink = C.ink, tile = 262, gap = 24, expand0 = 999, expand1 = 1000, expandTo, tag, note }) => {
  const f = useCurrentFrame();
  const expand = expandTo ? prog(f, expand0, expand1, E.inOutQuart) : 0;
  const rowX = 960 - (tiles.length * tile + (tiles.length - 1) * gap) / 2;
  const rowY = 540 - tile / 2 - 20;
  const src = tiles[0];
  const crop = expandTo ? lerpRect(src.crop, expandTo, expand) : src.crop;
  const box = { x: rowX * (1 - expand), y: rowY * (1 - expand), w: tile + (1920 - tile) * expand, h: tile + (1080 - tile) * expand };
  return (
    <AbsoluteFill style={{ background: bg, overflow: "hidden" }}>
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0, opacity: 1 - expand }}>
        {tiles.slice(1).map((_, i) => {
          const x0 = rowX + tile / 2;
          const x1 = rowX + (i + 1) * (tile + gap) + tile / 2;
          const y = rowY + tile + 26;
          const p = prog(f, 1.5 + i, 6 + i, E.inOutCubic);
          return (
            <path
              key={i}
              d={`M${x0} ${y} C ${x0} ${y + 90 + i * 18}, ${x1} ${y + 90 + i * 18}, ${x1} ${y}`}
              stroke={ink}
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
      {tiles.map((t, i) => {
        if (i === 0) return null;
        const x = rowX + i * (tile + gap);
        const a = prog(f, i * 0.75, 3.6 + i * 0.75, E.outExpo);
        return (
          <div key={t.label} style={{ position: "absolute", left: x + (1 - a) * 260, top: rowY, opacity: (1 - expand) * clamp01(a * 2) }}>
            <Photo img={t.img} crop={t.crop} width={tile} height={tile} />
            <MonoLabel text={t.label} color={ink} size={15} weight={700} style={{ position: "absolute", left: 0, top: -30 }} />
            <BBox x={0} y={0} w={tile} h={tile} p={a} color={ink} handleFill={C.white} handle={11} />
          </div>
        );
      })}
      <div style={{ position: "absolute", left: box.x, top: box.y, width: box.w, height: box.h }}>
        <Photo img={src.img} crop={crop} width={box.w} height={box.h} />
      </div>
      <div style={{ position: "absolute", left: rowX, top: rowY, opacity: 1 - expand }}>
        <MonoLabel text={src.label} color={ink} size={15} weight={700} style={{ position: "absolute", left: 0, top: -30 }} />
        <BBox x={0} y={0} w={tile} h={tile} p={prog(f, 0, 3)} color={ink} handleFill={bg} handle={11} />
      </div>
      {tag ? (
        <div style={{ position: "absolute", left: 72, top: 64, opacity: 1 - expand }}>
          <Tag text={tag} bg={ink} color={bg} size={15} p={prog(f, 0, 4)} />
        </div>
      ) : null}
      {note ? (
        <MonoLabel text={note} color={ink} size={14} p={prog(f, 1, 6)} style={{ position: "absolute", right: 72, top: 70, textAlign: "right", opacity: 1 - expand }} />
      ) : null}
    </AbsoluteFill>
  );
};
