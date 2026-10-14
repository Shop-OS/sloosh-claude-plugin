import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { FONT, C } from "../theme";
import { E, prog } from "../lib/anim";

/**
 * A giant word with a node rail under it. A signal fills the rail between `run0` and
 * `run1` (frames) and each letter lights up as the signal passes — a workflow running.
 * Optionally collapses (scale + blur) between `collapse0` and `collapse1`.
 */
export const RailWord: React.FC<{
  word: string;
  size?: number;
  bg?: string;
  color?: string;
  lit?: string;
  run0?: number;
  run1?: number;
  collapse0?: number;
  collapse1?: number;
  children?: React.ReactNode;
}> = ({ word, size = 228, bg = C.ink, color = C.white, lit = C.accent, run0 = 1, run1 = 14, collapse0 = 999, collapse1 = 1000, children }) => {
  const f = useCurrentFrame();
  const run = prog(f, run0, run1, E.inOutCubic);
  const collapse = prog(f, collapse0, collapse1, E.inOutQuart);
  const enter = prog(f, 0, 5, E.outExpo);
  const letters = word.split("");
  const n = letters.length;
  return (
    <AbsoluteFill style={{ background: bg, overflow: "hidden" }}>
      <AbsoluteFill style={{ backgroundImage: "radial-gradient(rgba(255,255,255,0.08) 1.2px, transparent 1.2px)", backgroundSize: "30px 30px", opacity: 0.8 }} />
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
        <div
          style={{
            position: "relative",
            display: "flex",
            alignItems: "flex-end",
            transform: `scale(${1 - 0.8 * collapse})`,
            opacity: 1 - collapse,
            filter: collapse > 0.05 ? `blur(${collapse * 8}px)` : undefined,
            marginTop: -40,
          }}
        >
          <div style={{ position: "absolute", left: 40, right: 40, bottom: -46, height: 4, borderRadius: 2, background: "rgba(255,255,255,0.18)" }} />
          <div style={{ position: "absolute", left: 40, bottom: -46, height: 4, borderRadius: 2, width: `calc((100% - 80px) * ${run})`, background: lit, boxShadow: `0 0 18px ${lit}` }} />
          {letters.map((ch, i) => {
            const at = n > 1 ? i / (n - 1) : 1;
            const on = run >= at - 0.001;
            const pop = prog(run, at - 0.05, at + 0.03, E.outBack) * (1 - prog(run, at + 0.06, at + 0.16));
            return (
              <div
                key={i}
                style={{
                  position: "relative",
                  fontFamily: FONT.display,
                  fontSize: size,
                  lineHeight: 1,
                  color: on ? lit : color,
                  transform: `translateY(${(1 - enter) * (i % 2 ? 160 : -160)}px) scale(${1 + 0.07 * pop})`,
                  transformOrigin: "50% 100%",
                  whiteSpace: "pre",
                }}
              >
                {ch}
                {ch.trim() ? (
                  <div
                    style={{
                      position: "absolute",
                      left: "50%",
                      bottom: -55,
                      width: 22,
                      height: 22,
                      marginLeft: -11,
                      borderRadius: 999,
                      background: on ? lit : bg,
                      border: `3px solid ${on ? lit : "rgba(255,255,255,0.45)"}`,
                      boxSizing: "border-box",
                    }}
                  />
                ) : null}
              </div>
            );
          })}
        </div>
      </AbsoluteFill>
      {children}
    </AbsoluteFill>
  );
};
