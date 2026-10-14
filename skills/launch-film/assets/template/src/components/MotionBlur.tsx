import React, { useMemo } from "react";
import { AbsoluteFill, Freeze, useCurrentFrame } from "remotion";

let mbId = 0;

/**
 * Sub-frame motion blur. Renders the children several times at fractional
 * frames inside the shutter window and averages them with plus-lighter.
 *
 * `samplesAt(frame)` lets a scene ask for blur only while its camera is fast,
 * so still moments cost a single render. `smearAt(frame)` adds an axis-aligned
 * gaussian smear (px) that fills the gaps between samples on whip pans.
 */
export const MotionBlur: React.FC<{
  children: React.ReactNode;
  shutterAngle?: number;
  samples?: number;
  samplesAt?: (frame: number) => number;
  smearAt?: (frame: number) => { x: number; y: number };
}> = ({ children, shutterAngle = 180, samples = 8, samplesAt, smearAt }) => {
  const frame = useCurrentFrame();
  const id = useMemo(() => `smear${mbId++}`, []);
  const n = Math.max(1, Math.round(samplesAt ? samplesAt(frame) : samples));
  const smear = smearAt ? smearAt(frame) : { x: 0, y: 0 };
  const hasSmear = smear.x > 0.3 || smear.y > 0.3;
  const shutter = shutterAngle / 360;
  const body =
    n <= 1 ? (
      <AbsoluteFill>{children}</AbsoluteFill>
    ) : (
      <AbsoluteFill style={{ isolation: "isolate" }}>
        {new Array(n).fill(true).map((_, i) => {
          // Trailing shutter: samples spread over [frame - shutter, frame].
          const t = frame - shutter * (i / (n - 1));
          return (
            <AbsoluteFill key={`mb-${i}`} style={{ mixBlendMode: "plus-lighter", filter: `opacity(${1 / n})` }}>
              <Freeze frame={t}>{children}</Freeze>
            </AbsoluteFill>
          );
        })}
      </AbsoluteFill>
    );
  if (!hasSmear) return body;
  return (
    <AbsoluteFill>
      <svg width="0" height="0" style={{ position: "absolute" }}>
        <filter id={id} x="-10%" y="-10%" width="120%" height="120%">
          <feGaussianBlur stdDeviation={`${smear.x} ${smear.y}`} edgeMode="duplicate" />
        </filter>
      </svg>
      <AbsoluteFill style={{ filter: `url(#${id})` }}>{body}</AbsoluteFill>
    </AbsoluteFill>
  );
};
