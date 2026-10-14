import React from "react";
import { C, FONT } from "../theme";
import { clamp01, E } from "../lib/anim";
import { Photo } from "../components/Media";
import type { ImgAsset } from "../assets";

/**
 * A deliberately generic, unbranded AI chat window — "the old way" in contrast scenes.
 * Neutral greys only; never imitate a real competitor's UI or name.
 * Compose a scene from these blocks and drive their props from your own timing.
 */
const G = {
  bg: "#151618",
  panel: "#1B1C1F",
  bubble: "#26272B",
  border: "rgba(255,255,255,0.09)",
  text: "#E8E8EA",
  muted: "#8D8E93",
};

export const ChatWindow: React.FC<{ width?: number; height?: number; title?: string; children: React.ReactNode; style?: React.CSSProperties }> = ({
  width = 1180,
  height = 800,
  title = "New chat",
  children,
  style,
}) => (
  <div
    style={{
      position: "relative",
      width,
      height,
      borderRadius: 22,
      background: G.bg,
      border: `1px solid ${G.border}`,
      boxShadow: "0 40px 120px rgba(0,0,0,0.6)",
      overflow: "hidden",
      fontFamily: FONT.ui,
      ...style,
    }}
  >
    <div style={{ height: 58, display: "flex", alignItems: "center", gap: 10, padding: "0 22px", borderBottom: `1px solid ${G.border}`, color: G.muted, fontSize: 15 }}>
      <div style={{ width: 12, height: 12, borderRadius: 99, background: "#3A3B40" }} />
      <div style={{ width: 12, height: 12, borderRadius: 99, background: "#3A3B40" }} />
      <div style={{ width: 12, height: 12, borderRadius: 99, background: "#3A3B40" }} />
      <div style={{ marginLeft: 14 }}>{title}</div>
    </div>
    <div style={{ position: "absolute", left: 0, right: 0, top: 58, bottom: 0 }}>{children}</div>
  </div>
);

export const UserBubble: React.FC<{ text: string; p?: number; img?: { img: ImgAsset; crop?: { x: number; y: number; w: number; h: number } }; style?: React.CSSProperties }> = ({
  text,
  p = 1,
  img,
  style,
}) => {
  const n = Math.round(text.length * clamp01(p));
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 10, ...style }}>
      {img ? (
        <div style={{ borderRadius: 14, overflow: "hidden", border: `1px solid ${G.border}` }}>
          <Photo img={img.img} crop={img.crop} width={200} height={150} />
        </div>
      ) : null}
      <div style={{ maxWidth: 640, background: G.bubble, color: G.text, fontSize: 24, lineHeight: 1.4, padding: "14px 20px", borderRadius: 20 }}>
        {text.slice(0, n)}
        {p < 1 ? <span style={{ opacity: 0.7 }}>▍</span> : null}
      </div>
    </div>
  );
};

/** Assistant result: an image card that "develops" from a shimmer while generating. */
export const AiResult: React.FC<{
  img: { img: ImgAsset; crop?: { x: number; y: number; w: number; h: number } };
  reveal: number;
  width?: number;
  height?: number;
  caption?: string;
  style?: React.CSSProperties;
}> = ({ img, reveal, width = 560, height = 315, caption = "Here's your image.", style }) => {
  const r = clamp01(reveal);
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 10, ...style }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, color: G.muted, fontSize: 18 }}>
        <div style={{ width: 26, height: 26, borderRadius: 99, background: "#3A3B40", display: "flex", alignItems: "center", justifyContent: "center", color: G.text, fontSize: 14 }}>✦</div>
        {r < 1 ? "Generating…" : caption}
      </div>
      <div style={{ position: "relative", width, height, borderRadius: 16, overflow: "hidden", background: G.panel, border: `1px solid ${G.border}` }}>
        <div style={{ position: "absolute", inset: 0, opacity: E.inOutCubic(r), filter: `blur(${(1 - r) * 24}px)` }}>
          <Photo img={img.img} crop={img.crop} width={width} height={height} />
        </div>
        {r < 1 ? (
          <div
            style={{
              position: "absolute",
              inset: 0,
              background: `linear-gradient(100deg, rgba(255,255,255,0) ${r * 100 - 30}%, rgba(255,255,255,0.10) ${r * 100}%, rgba(255,255,255,0) ${r * 100 + 30}%)`,
            }}
          />
        ) : null}
      </div>
    </div>
  );
};

export const Composer: React.FC<{ text?: string; p?: number; sendPress?: number; placeholder?: string; width?: number }> = ({
  text = "",
  p = 1,
  sendPress = 0,
  placeholder = "Message…",
  width = 1060,
}) => {
  const n = Math.round(text.length * clamp01(p));
  const shown = text.slice(0, n);
  return (
    <div
      style={{
        width,
        height: 72,
        borderRadius: 18,
        background: G.panel,
        border: `1px solid ${G.border}`,
        display: "flex",
        alignItems: "center",
        padding: "0 12px 0 24px",
        boxSizing: "border-box",
        gap: 14,
      }}
    >
      <div style={{ color: G.muted, fontSize: 26 }}>+</div>
      <div style={{ flex: 1, color: shown ? G.text : G.muted, fontSize: 22, whiteSpace: "nowrap", overflow: "hidden" }}>
        {shown || placeholder}
        {shown && p < 1 ? <span style={{ opacity: 0.7 }}>▍</span> : null}
      </div>
      <div
        style={{
          width: 48,
          height: 48,
          borderRadius: 99,
          background: "#E8E8EA",
          color: G.bg,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: 24,
          fontWeight: 700,
          transform: `scale(${1 - 0.12 * clamp01(sendPress)})`,
        }}
      >
        ↑
      </div>
    </div>
  );
};

export const ChatButton: React.FC<{ label: string; press?: number; icon?: string; style?: React.CSSProperties }> = ({ label, press = 0, icon = "↻", style }) => (
  <div
    style={{
      display: "inline-flex",
      alignItems: "center",
      gap: 8,
      height: 44,
      padding: "0 18px",
      borderRadius: 12,
      border: `1px solid ${G.border}`,
      background: press > 0 ? "#2F3035" : G.panel,
      color: G.text,
      fontFamily: FONT.ui,
      fontSize: 17,
      fontWeight: 500,
      transform: `scale(${1 - 0.06 * clamp01(press)})`,
      ...style,
    }}
  >
    <span style={{ fontSize: 19 }}>{icon}</span>
    {label}
  </div>
);

/** Failure annotation tag: ✕ + label in the warning colour. */
export const XTag: React.FC<{ text: string; p?: number; size?: number; style?: React.CSSProperties }> = ({ text, p = 1, size = 16, style }) => (
  <div
    style={{
      display: "inline-flex",
      alignItems: "center",
      gap: size * 0.45,
      background: C.warn,
      color: C.white,
      fontFamily: FONT.mono,
      fontWeight: 700,
      fontSize: size,
      letterSpacing: "0.06em",
      padding: `${size * 0.32}px ${size * 0.62}px`,
      clipPath: `inset(0 ${(1 - E.outExpo(clamp01(p))) * 100}% 0 0)`,
      whiteSpace: "nowrap",
      ...style,
    }}
  >
    ✕ {text}
  </div>
);
