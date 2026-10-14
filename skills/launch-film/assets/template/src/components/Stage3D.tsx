import React from "react";
import { AbsoluteFill } from "remotion";

export type Cam = {
  /** page-space point that sits at the centre of the frame */
  tx: number;
  ty: number;
  /** translateZ of the page at the focus point (0 = 1:1, negative = farther) */
  z: number;
  rx: number;
  ry?: number;
  rz: number;
  /** screen offset of the focus point */
  sx?: number;
  sy?: number;
};

/** Perspective stage. Children are planes placed with <Plane3D>. */
export const Stage3D: React.FC<{
  perspective?: number;
  children: React.ReactNode;
  background?: string;
  style?: React.CSSProperties;
}> = ({ perspective = 1500, children, background, style }) => (
  <AbsoluteFill
    style={{
      perspective,
      perspectiveOrigin: "960px 540px",
      overflow: "hidden",
      background,
      ...style,
    }}
  >
    {children}
  </AbsoluteFill>
);

/** A page-sized plane oriented by an orbit camera around (tx, ty). */
export const Plane3D: React.FC<{
  cam: Cam;
  width: number;
  height: number;
  children: React.ReactNode;
  style?: React.CSSProperties;
}> = ({ cam, width, height, children, style }) => (
  <div
    style={{
      position: "absolute",
      left: 0,
      top: 0,
      width,
      height,
      transformOrigin: "0 0",
      transformStyle: "preserve-3d",
      transform: `translate3d(${960 + (cam.sx ?? 0)}px, ${540 + (cam.sy ?? 0)}px, ${cam.z}px) rotateX(${cam.rx}deg) rotateY(${cam.ry ?? 0}deg) rotateZ(${cam.rz}deg) translate3d(${-cam.tx}px, ${-cam.ty}px, 0px)`,
      ...style,
    }}
  >
    {children}
  </div>
);

/** Lifts children off the page plane by `h` px with a soft contact shadow. */
export const Float: React.FC<{
  x: number;
  y: number;
  h: number;
  w?: number;
  hgt?: number;
  rot?: number;
  tilt?: number;
  shadow?: number;
  children: React.ReactNode;
  billboard?: number;
}> = ({ x, y, h, w = 0, hgt = 0, rot = 0, tilt = 0, shadow = 0.45, children, billboard = 0 }) => (
  <>
    {shadow > 0 && w > 0 ? (
      <div
        style={{
          position: "absolute",
          left: x + w * 0.08 + h * 0.06,
          top: y + hgt * 0.1 + h * 0.1,
          width: w * 0.84,
          height: hgt * 0.84,
          borderRadius: 30,
          background: `rgba(0,0,0,${shadow})`,
          filter: `blur(${10 + h * 0.18}px)`,
          transform: `rotate(${rot}deg)`,
        }}
      />
    ) : null}
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        transformStyle: "preserve-3d",
        transformOrigin: "50% 100%",
        transform: `translateZ(${h}px) rotate(${rot}deg) rotateX(${-billboard + tilt}deg)`,
      }}
    >
      {children}
    </div>
  </>
);
