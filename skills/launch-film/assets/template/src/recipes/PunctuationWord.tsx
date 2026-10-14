import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { FONT } from "../theme";
import { E, kf } from "../lib/anim";
import { MonoLabel } from "../components/Tech";

/**
 * A single giant word filling the frame on a solid colour — the 3–6 frame "punctuation"
 * beat that sits exactly on a spoken word. Settles from 1.08 → 1.0 over its duration.
 */
export const PunctuationWord: React.FC<{
  text: string;
  bg: string;
  color: string;
  size?: number;
  dur?: number;
  label?: string;
  labelColor?: string;
  tracking?: string;
}> = ({ text, bg, color, size = 470, dur = 6, label, labelColor, tracking = "-0.01em" }) => {
  const f = useCurrentFrame();
  const s = kf(f, [0, dur], [1.08, 1.0], E.outCubic);
  return (
    <AbsoluteFill style={{ background: bg, alignItems: "center", justifyContent: "center", overflow: "hidden" }}>
      <div
        style={{
          fontFamily: FONT.display,
          fontSize: size,
          lineHeight: 1,
          color,
          transform: `scale(${s})`,
          letterSpacing: tracking,
          whiteSpace: "nowrap",
          marginTop: size * 0.08,
        }}
      >
        {text}
      </div>
      {label ? (
        <MonoLabel text={label} color={labelColor ?? color} size={15} style={{ position: "absolute", left: 72, top: 64 }} />
      ) : null}
    </AbsoluteFill>
  );
};
