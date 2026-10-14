import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { C } from "../theme";
import { E, hash, prog } from "../lib/anim";
import { ClipView, Photo } from "../components/Media";
import type { ImgAsset } from "../assets";

export type WallItem =
  | { kind: "img"; img: ImgAsset; crop?: { x: number; y: number; w: number; h: number } }
  | { kind: "clip"; src: string; w: number; h: number; trimBefore?: number };

/**
 * "Content flood": a wall of tiles that fills ever faster while the camera pulls back.
 * Tiles appear in order of distance from the centre; `waves` lists frame times where a new
 * ring of tiles bursts in. Optionally `glitch` (0..1) desaturates/jitters tiles ("slop").
 */
export const MosaicWall: React.FC<{
  items: WallItem[];
  cols?: number;
  rows?: number;
  cell?: number;
  gap?: number;
  zoom: (f: number) => number;
  reveal: (f: number) => number; // fraction of tiles visible 0..1
  glitch?: (f: number) => number;
  bg?: string;
  playEvery?: number; // every nth tile that is a clip is allowed to play (cost control)
}> = ({ items, cols = 21, rows = 13, cell = 210, gap = 14, zoom, reveal, glitch = () => 0, bg = C.ink }) => {
  const f = useCurrentFrame();
  const k = zoom(f);
  const shown = reveal(f);
  const g = glitch(f);
  const gw = cols * cell + (cols - 1) * gap;
  const gh = rows * cell * 0.5625 + (rows - 1) * gap;
  const ch = cell * 0.5625;
  const tiles: { i: number; j: number; d: number }[] = [];
  for (let j = 0; j < rows; j++) for (let i = 0; i < cols; i++) {
    const dx = (i - (cols - 1) / 2) / cols;
    const dy = (j - (rows - 1) / 2) / rows;
    tiles.push({ i, j, d: Math.hypot(dx, dy * 1.4) + hash(i * 7.1 + j * 3.3) * 0.08 });
  }
  const order = [...tiles].sort((a, b) => a.d - b.d);
  const rank = new Map(order.map((t, r) => [`${t.i}-${t.j}`, r / order.length]));
  return (
    <AbsoluteFill style={{ background: bg, overflow: "hidden" }}>
      <div
        style={{
          position: "absolute",
          left: 960 - gw / 2,
          top: 540 - gh / 2,
          width: gw,
          height: gh,
          transformOrigin: "50% 50%",
          transform: `scale(${k})`,
        }}
      >
        {tiles.map((t) => {
          const r = rank.get(`${t.i}-${t.j}`) ?? 1;
          if (r > shown) return null;
          const a = prog(shown, r, r + 0.04, E.outBack);
          const it = items[(t.i * 7 + t.j * 13) % items.length];
          const jx = g > 0 ? (hash(t.i * 3 + t.j * 5 + Math.floor(f / 2)) - 0.5) * 14 * g : 0;
          return (
            <div
              key={`${t.i}-${t.j}`}
              style={{
                position: "absolute",
                left: t.i * (cell + gap) + jx,
                top: t.j * (ch + gap),
                width: cell,
                height: ch,
                borderRadius: 10,
                overflow: "hidden",
                transform: `scale(${0.6 + 0.4 * a})`,
                opacity: Math.min(1, a * 1.5),
                filter: g > 0 ? `saturate(${1 - 0.6 * g}) contrast(${1 + 0.25 * g})` : undefined,
                boxShadow: "0 10px 24px rgba(0,0,0,0.5)",
              }}
            >
              {it.kind === "img" ? (
                <Photo img={it.img} crop={it.crop} width={cell} height={ch} />
              ) : (
                <ClipView src={it.src} clipW={it.w} clipH={it.h} width={cell} height={ch} trimBefore={it.trimBefore ?? 0} />
              )}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
