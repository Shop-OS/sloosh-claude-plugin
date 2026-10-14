import React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from "remotion";
import { Video } from "@remotion/media";
import type { ImgAsset } from "../assets";

/**
 * Shows the source rectangle `crop` (logical pixels) of an image inside a
 * width×height box, cover-fitted. With `flip`, `crop` is given in mirrored
 * coordinates (as if the picture had been flipped horizontally first).
 */
export const Photo: React.FC<{
  img: ImgAsset;
  width: number;
  height: number;
  crop?: { x: number; y: number; w: number; h: number };
  flip?: boolean;
  radius?: number;
  style?: React.CSSProperties;
  imgStyle?: React.CSSProperties;
}> = ({ img, width, height, crop, flip = false, radius = 0, style, imgStyle }) => {
  const c = crop ?? { x: 0, y: 0, w: img.w, h: img.h };
  const scale = Math.max(width / c.w, height / c.h);
  const cx = c.x + c.w / 2;
  const cy = c.y + c.h / 2;
  const left = width / 2 - cx * scale;
  const top = height / 2 - cy * scale;
  return (
    <div style={{ position: "relative", width, height, overflow: "hidden", borderRadius: radius, ...style }}>
      <Img
        src={img.src}
        style={{
          position: "absolute",
          left,
          top,
          width: img.w * scale,
          height: img.h * scale,
          maxWidth: "none",
          transform: flip ? "scaleX(-1)" : undefined,
          ...imgStyle,
        }}
      />
    </div>
  );
};

/** Places a whole image in frame space: displayed = logical * scale at (x, y). */
export const Placed: React.FC<{
  img: ImgAsset;
  scale: number;
  x: number;
  y: number;
  flip?: boolean;
  style?: React.CSSProperties;
}> = ({ img, scale, x, y, flip = false, style }) => (
  <Img
    src={img.src}
    style={{
      position: "absolute",
      left: x,
      top: y,
      width: img.w * scale,
      height: img.h * scale,
      maxWidth: "none",
      transform: flip ? "scaleX(-1)" : undefined,
      ...style,
    }}
  />
);

/**
 * A video clip shown through a view rectangle (in the clip's pixel space), like Photo.
 * `trimBefore` is in frames of the composition fps. Clips are muted by default.
 */
export const ClipView: React.FC<{
  src: string;
  clipW: number;
  clipH: number;
  width: number;
  height: number;
  crop?: { x: number; y: number; w: number; h: number };
  trimBefore?: number;
  playbackRate?: number;
  flip?: boolean;
  style?: React.CSSProperties;
}> = ({ src, clipW, clipH, width, height, crop, trimBefore = 0, playbackRate = 1, flip = false, style }) => {
  const c = crop ?? { x: 0, y: 0, w: clipW, h: clipH };
  const scale = Math.max(width / c.w, height / c.h);
  const left = width / 2 - (c.x + c.w / 2) * scale;
  const top = height / 2 - (c.y + c.h / 2) * scale;
  return (
    <div style={{ position: "relative", width, height, overflow: "hidden", ...style }}>
      <div
        style={{
          position: "absolute",
          left,
          top,
          width: clipW * scale,
          height: clipH * scale,
          transform: flip ? "scaleX(-1)" : undefined,
        }}
      >
        <Video
          src={src}
          muted
          trimBefore={trimBefore}
          playbackRate={playbackRate}
          objectFit="fill"
          style={{ width: "100%", height: "100%" }}
        />
      </div>
    </div>
  );
};

/** Zooms its children by k around a frame-space point (camera push). */
export const Zoom: React.FC<{
  k: number;
  cx: number;
  cy: number;
  dx?: number;
  dy?: number;
  children: React.ReactNode;
  style?: React.CSSProperties;
}> = ({ k, cx, cy, dx = 0, dy = 0, children, style }) => (
  <AbsoluteFill
    style={{
      transformOrigin: "0 0",
      transform: `translate(${cx + dx}px, ${cy + dy}px) scale(${k}) translate(${-cx}px, ${-cy}px)`,
      ...style,
    }}
  >
    {children}
  </AbsoluteFill>
);

/** Animated film grain, overlay-blended (plates from scripts/grain.py in public/fx). */
export const Grain: React.FC<{ opacity?: number; blend?: React.CSSProperties["mixBlendMode"] }> = ({
  opacity = 0.07,
  blend = "overlay",
}) => {
  const frame = useCurrentFrame();
  const i = Math.floor(frame / 2) % 8;
  const ox = ((Math.floor(frame / 2) * 137) % 61) - 30;
  const oy = ((Math.floor(frame / 2) * 89) % 47) - 23;
  return (
    <AbsoluteFill style={{ pointerEvents: "none", mixBlendMode: blend, opacity, overflow: "hidden" }}>
      <Img
        src={staticFile(`fx/grain_${i}.png`)}
        style={{ position: "absolute", left: -40 + ox, top: -40 + oy, width: 2000, height: 1160, maxWidth: "none" }}
      />
    </AbsoluteFill>
  );
};

export const Vignette: React.FC<{ strength?: number; color?: string }> = ({ strength = 0.4, color = "0,0,0" }) => (
  <AbsoluteFill
    style={{
      pointerEvents: "none",
      background: `radial-gradient(ellipse 75% 70% at 50% 50%, rgba(${color},0) 55%, rgba(${color},${strength}) 100%)`,
    }}
  />
);

/** Full-frame flash used on shutter / impact beats. */
export const Flash: React.FC<{ o: number; color?: string }> = ({ o, color = "#FFFFFF" }) =>
  o <= 0.001 ? null : <AbsoluteFill style={{ background: color, opacity: o, pointerEvents: "none" }} />;
