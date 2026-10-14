import React from "react";
import { C, FONT } from "../theme";
import type { ImgAsset } from "../assets";
import { Photo } from "../components/Media";
import { Eyes, Logo } from "../brand/Logo";
import { clamp01, E } from "../lib/anim";
import {
  IArrowUp,
  IBell,
  IChevronRight,
  ICoin,
  ICompass,
  IFlask,
  IGrid,
  IImage,
  IInfo,
  IPlay,
  IPlus,
  ISun,
  IText,
  IUpload,
  IVideo,
} from "./Icons";

// ---------------------------------------------------------------- buttons

export const YellowBtn: React.FC<{
  label: string;
  icon?: React.ReactNode;
  press?: number;
  size?: "sm" | "md" | "lg" | "xl";
  style?: React.CSSProperties;
  glow?: number;
}> = ({ label, icon, press = 0, size = "md", style, glow = 0 }) => {
  const dims = {
    sm: { h: 36, fs: 14, px: 16, r: 8, sh: 3 },
    md: { h: 44, fs: 16, px: 20, r: 12, sh: 3 },
    lg: { h: 64, fs: 22, px: 30, r: 16, sh: 5 },
    xl: { h: 84, fs: 30, px: 40, r: 20, sh: 6 },
  }[size];
  const pr = clamp01(press);
  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: dims.fs * 0.5,
        height: dims.h,
        padding: `0 ${dims.px}px`,
        borderRadius: dims.r,
        background: C.yellow,
        color: C.ink,
        fontFamily: FONT.ui,
        fontWeight: 600,
        fontSize: dims.fs,
        whiteSpace: "nowrap",
        transform: `translateY(${pr * dims.sh}px)`,
        boxShadow: `0 ${dims.sh * (1 - pr)}px 0 0 ${C.yellowEdge}${glow > 0 ? `, 0 0 ${60 * glow}px ${10 * glow}px rgba(254,204,21,${0.35 * glow})` : ""}`,
        ...style,
      }}
    >
      {icon}
      {label}
    </div>
  );
};

export const OutlineBtn: React.FC<{ label: string; size?: "sm" | "md" | "lg"; style?: React.CSSProperties; icon?: React.ReactNode }> = ({
  label,
  size = "md",
  style,
  icon,
}) => {
  const d = { sm: { h: 36, fs: 14, px: 14, r: 8 }, md: { h: 44, fs: 16, px: 18, r: 12 }, lg: { h: 64, fs: 22, px: 28, r: 16 } }[size];
  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 8,
        height: d.h,
        padding: `0 ${d.px}px`,
        borderRadius: d.r,
        border: `1.5px solid ${C.yellow}`,
        color: C.yellowText,
        fontFamily: FONT.ui,
        fontWeight: 600,
        fontSize: d.fs,
        background: "rgba(254,204,21,0.04)",
        boxShadow: `0 3px 0 0 ${C.yellowEdge}`,
        whiteSpace: "nowrap",
        ...style,
      }}
    >
      {icon}
      {label}
    </div>
  );
};

export const BetaPill: React.FC<{ scale?: number }> = ({ scale = 1 }) => (
  <div
    style={{
      fontFamily: FONT.ui,
      fontWeight: 600,
      fontSize: 11 * scale,
      letterSpacing: "0.08em",
      color: C.yellowText,
      border: `1px solid rgba(254,204,21,0.55)`,
      background: "rgba(254,204,21,0.08)",
      borderRadius: 999,
      padding: `${3 * scale}px ${9 * scale}px`,
    }}
  >
    BETA
  </div>
);

/** Small yellow "space" badge with the mascot eyes (seen on every Spaces card). */
export const EyeBadge: React.FC<{ size?: number; look?: { x: number; y: number } }> = ({ size = 22, look }) => (
  <div
    style={{
      width: size,
      height: size,
      borderRadius: size * 0.26,
      background: C.yellow,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      boxShadow: `0 ${size * 0.08}px 0 ${C.yellowEdge}`,
    }}
  >
    <div style={{ background: C.ink, borderRadius: size * 0.2, padding: size * 0.1, display: "flex" }}>
      <Eyes width={size * 0.56} look={look} />
    </div>
  </div>
);

// ---------------------------------------------------------------- nav

const NAV = ["Explore", "Image", "Video", "Spaces", "Spacelab", "Assets", "Docs", "MCP", "Upgrade"];

export const NavBar: React.FC<{ width?: number; active?: string; logoLook?: { x: number; y: number } }> = ({
  width = 1440,
  active = "Explore",
  logoLook,
}) => (
  <div
    style={{
      width,
      height: 64,
      display: "flex",
      alignItems: "center",
      padding: "0 20px",
      boxSizing: "border-box",
      background: C.ink,
      borderBottom: `1px solid ${C.line}`,
      fontFamily: FONT.ui,
      color: C.textSubtle,
      gap: 12,
    }}
  >
    <Logo width={78} look={logoLook} />
    <BetaPill />
    <div style={{ flex: 1, display: "flex", justifyContent: "center", alignItems: "center", gap: 6 }}>
      {NAV.map((n, i) => {
        const isActive = n === active;
        const icon =
          n === "Explore" ? <ICompass size={15} color={C.yellow} /> : n === "Spaces" ? <IGrid size={15} /> : n === "Spacelab" ? <IFlask size={15} /> : null;
        return (
          <React.Fragment key={n}>
            {i === 1 || i === 3 || i === 5 ? <span style={{ color: C.layer4, fontSize: 18, margin: "0 2px" }}>⟨</span> : null}
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 6,
                padding: "7px 12px",
                borderRadius: 10,
                fontSize: 14,
                fontWeight: isActive ? 600 : 500,
                color: n === "Upgrade" ? C.yellowText : isActive ? C.text : C.textSubtle,
                background: isActive ? C.layer2 : "transparent",
              }}
            >
              {isActive || n === "Spaces" || n === "Spacelab" ? icon : null}
              {n}
              {n === "Video" ? (
                <span
                  style={{
                    fontSize: 10,
                    fontWeight: 600,
                    color: C.yellowText,
                    background: "#393114",
                    borderRadius: 5,
                    padding: "2px 5px",
                  }}
                >
                  New
                </span>
              ) : null}
            </div>
          </React.Fragment>
        );
      })}
    </div>
    <ISun size={18} color={C.textSubtle} />
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 7,
        background: C.layer2,
        borderRadius: 10,
        padding: "7px 12px",
        fontSize: 13,
        fontWeight: 600,
        color: C.yellowText,
      }}
    >
      <ICoin size={16} />
      250.00 credits
    </div>
    <IBell size={19} color={C.textSubtle} />
    <div
      style={{
        width: 32,
        height: 32,
        borderRadius: 999,
        background: "linear-gradient(135deg,#FECC15,#F97316 55%,#7C3AED)",
        border: `2px solid ${C.layer3}`,
      }}
    />
  </div>
);

// ---------------------------------------------------------------- prompt bar

export const PromptBar: React.FC<{
  text?: string;
  placeholder?: string;
  width?: number;
  scale?: number;
  sendPress?: number;
  caret?: boolean;
  attachment?: React.ReactNode;
}> = ({ text = "", placeholder = "Create your own ideas", width = 400, scale = 1, sendPress = 0, caret = false, attachment }) => (
  <div
    style={{
      width: width * scale,
      height: 48 * scale,
      borderRadius: 14 * scale,
      background: C.layer2,
      border: `${1 * scale}px solid ${C.layer4}`,
      boxShadow: `0 ${18 * scale}px ${50 * scale}px rgba(0,0,0,0.55)`,
      display: "flex",
      alignItems: "center",
      gap: 12 * scale,
      padding: `0 ${8 * scale}px 0 ${14 * scale}px`,
      boxSizing: "border-box",
      fontFamily: FONT.ui,
    }}
  >
    <IPlus size={18 * scale} color={C.textMuted} />
    {attachment}
    <div
      style={{
        flex: 1,
        fontSize: 15 * scale,
        color: text ? C.text : C.textMuted,
        whiteSpace: "nowrap",
        overflow: "hidden",
      }}
    >
      {text || placeholder}
      {caret ? <span style={{ color: C.yellow, marginLeft: 2 * scale }}>|</span> : null}
    </div>
    <div
      style={{
        width: 32 * scale,
        height: 32 * scale,
        borderRadius: 9 * scale,
        background: C.yellow,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        transform: `translateY(${clamp01(sendPress) * 2 * scale}px)`,
        boxShadow: `0 ${2 * scale * (1 - clamp01(sendPress))}px 0 ${C.yellowEdge}`,
      }}
    >
      <IArrowUp size={17 * scale} color={C.ink} stroke={2.4} />
    </div>
  </div>
);

// ---------------------------------------------------------------- headings

export const Heading: React.FC<{
  children: React.ReactNode;
  size?: number;
  color?: string;
  style?: React.CSSProperties;
}> = ({ children, size = 24, color = C.text, style }) => (
  <div
    style={{
      fontFamily: FONT.display,
      fontSize: size,
      lineHeight: 1.04,
      color,
      letterSpacing: size > 40 ? "0.3px" : "0px",
      ...style,
    }}
  >
    {children}
  </div>
);

export const Accent: React.FC<{ children: React.ReactNode; color?: string }> = ({ children, color = C.yellowText }) => (
  <span style={{ color }}>{children}</span>
);

// ---------------------------------------------------------------- cards

export const ToolCard: React.FC<{
  img: ImgAsset;
  crop?: { x: number; y: number; w: number; h: number };
  label: string;
  width?: number;
  highlight?: number;
  lift?: number;
}> = ({ img, crop, label, width = 330, highlight = 0, lift = 0 }) => (
  <div
    style={{
      width,
      height: 116,
      borderRadius: 14,
      background: C.layer1,
      border: `1.5px solid ${highlight > 0 ? `rgba(254,204,21,${0.25 + 0.75 * highlight})` : C.line}`,
      display: "flex",
      alignItems: "center",
      gap: 18,
      padding: "0 14px",
      boxSizing: "border-box",
      fontFamily: FONT.ui,
      fontWeight: 600,
      fontSize: 18,
      color: C.text,
      transform: `translateY(${-lift}px)`,
      boxShadow: lift > 0 ? `0 ${lift * 1.2}px ${lift * 2.4}px rgba(0,0,0,0.55)` : undefined,
    }}
  >
    <Photo img={img} crop={crop} width={86} height={86} radius={10} />
    {label}
  </div>
);

export const ModelCard: React.FC<{
  img: ImgAsset;
  crop?: { x: number; y: number; w: number; h: number };
  label: string;
  dot?: string;
  width?: number;
  height?: number;
}> = ({ img, crop, label, dot = C.yellow, width = 218, height = 158 }) => (
  <div style={{ position: "relative", width, height, borderRadius: 12, overflow: "hidden", background: C.layer2 }}>
    <Photo img={img} crop={crop} width={width} height={height} />
    <div
      style={{
        position: "absolute",
        inset: 0,
        background: "linear-gradient(to top, rgba(0,0,0,0.78) 0%, rgba(0,0,0,0) 45%)",
      }}
    />
    <div
      style={{
        position: "absolute",
        left: 12,
        bottom: 12,
        display: "flex",
        alignItems: "center",
        gap: 8,
        fontFamily: FONT.ui,
        fontSize: 14,
        fontWeight: 600,
        color: C.text,
      }}
    >
      <div style={{ width: 20, height: 20, borderRadius: 6, background: C.white, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ width: 10, height: 10, borderRadius: 3, background: dot }} />
      </div>
      {label}
    </div>
  </div>
);

/** Spaces workflow card: inputs → dotted arrow → output, title and blurb. */
export const WorkflowCard: React.FC<{
  inputs: { img: ImgAsset; crop?: { x: number; y: number; w: number; h: number }; flip?: boolean }[];
  output: { img: ImgAsset; crop?: { x: number; y: number; w: number; h: number } };
  title: string;
  blurb: string;
  width?: number;
  highlight?: number;
  lift?: number;
  look?: { x: number; y: number };
}> = ({ inputs, output, title, blurb, width = 452, highlight = 0, lift = 0, look }) => {
  const thumbH = Math.round(width * 0.5);
  return (
    <div
      style={{
        width,
        borderRadius: 14,
        background: C.layer1,
        border: `1.5px solid ${highlight > 0 ? `rgba(254,204,21,${0.2 + 0.8 * highlight})` : C.line}`,
        overflow: "hidden",
        fontFamily: FONT.ui,
        transform: `translateY(${-lift}px)`,
        boxShadow: `0 ${10 + lift}px ${30 + lift * 2}px rgba(0,0,0,${0.35 + 0.25 * clamp01(lift / 30)})${highlight > 0 ? `, 0 0 0 ${3 * highlight}px rgba(254,204,21,${0.18 * highlight})` : ""}`,
      }}
    >
      <div
        style={{
          position: "relative",
          height: thumbH,
          background: "radial-gradient(120% 120% at 70% 40%, #262626 0%, #121212 60%, #0c0c0c 100%)",
        }}
      >
        <div style={{ position: "absolute", left: 12, top: 12, zIndex: 3 }}>
          <EyeBadge size={24} look={look} />
        </div>
        {inputs.map((inp, i) => (
          <div
            key={i}
            style={{
              position: "absolute",
              left: width * 0.07 + i * width * 0.06,
              top: thumbH * 0.2 + i * thumbH * 0.18,
              transform: `rotate(${i === 0 ? -6 : 5}deg)`,
              borderRadius: 8,
              boxShadow: "0 10px 24px rgba(0,0,0,0.6)",
              border: "2px solid rgba(255,255,255,0.9)",
              overflow: "hidden",
              zIndex: 2 - i,
            }}
          >
            <Photo img={inp.img} crop={inp.crop} flip={inp.flip} width={width * 0.2} height={width * 0.2} />
          </div>
        ))}
        <svg width={width * 0.14} height={20} style={{ position: "absolute", left: width * 0.39, top: thumbH * 0.5 - 10 }}>
          <path d={`M2 10 L${width * 0.14 - 10} 10`} stroke={C.yellow} strokeWidth={2} strokeDasharray="2 6" strokeLinecap="round" />
          <path d={`M${width * 0.14 - 14} 4 L${width * 0.14 - 6} 10 L${width * 0.14 - 14} 16`} stroke={C.yellow} strokeWidth={2} fill="none" />
        </svg>
        <div
          style={{
            position: "absolute",
            right: width * 0.05,
            top: thumbH * 0.08,
            borderRadius: 10,
            overflow: "hidden",
            boxShadow: "0 16px 36px rgba(0,0,0,0.65)",
          }}
        >
          <Photo img={output.img} crop={output.crop} width={width * 0.44} height={thumbH * 0.84} />
        </div>
      </div>
      <div style={{ padding: "14px 16px 16px" }}>
        <div style={{ fontSize: 17, fontWeight: 600, color: C.white }}>{title}</div>
        <div style={{ fontSize: 13, color: C.textSubtle, marginTop: 4, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
          {blurb}
        </div>
      </div>
    </div>
  );
};

/** Upload slot from a space's run panel. */
export const UploadSlot: React.FC<{
  label: string;
  width?: number;
  height?: number;
  filled?: { img: ImgAsset; crop?: { x: number; y: number; w: number; h: number }; flip?: boolean; name: string };
  fillP?: number;
  hover?: number;
}> = ({ label, width = 360, height = 118, filled, fillP = 0, hover = 0 }) => {
  const f = clamp01(fillP);
  return (
    <div
      style={{
        position: "relative",
        width,
        height,
        borderRadius: 12,
        background: C.layer2,
        border: `1.5px ${hover > 0 ? "dashed" : "solid"} ${hover > 0 ? `rgba(254,204,21,${0.4 + 0.6 * hover})` : C.layer3}`,
        overflow: "hidden",
        fontFamily: FONT.ui,
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: 6,
          opacity: 1 - f,
        }}
      >
        <div style={{ width: 30, height: 30, borderRadius: 999, background: C.layer4, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <IUpload size={15} color={C.textSubtle} />
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 14, fontWeight: 600, color: C.text }}>
          {label} <span style={{ color: C.yellow }}>*</span> <IInfo size={13} color={C.textMuted} />
        </div>
        <div style={{ fontSize: 12, color: C.textMuted }}>JPG or PNG</div>
      </div>
      {filled ? (
        <div
          style={{
            position: "absolute",
            inset: 8,
            borderRadius: 8,
            overflow: "hidden",
            opacity: f,
            transform: `scale(${0.92 + 0.08 * E.outBack(f)})`,
          }}
        >
          <Photo img={filled.img} crop={filled.crop} flip={filled.flip} width={width - 16} height={height - 16} />
          <div
            style={{
              position: "absolute",
              left: 8,
              bottom: 8,
              display: "flex",
              alignItems: "center",
              gap: 6,
              background: "rgba(10,10,10,0.78)",
              borderRadius: 7,
              padding: "4px 8px",
              fontSize: 12,
              color: C.text,
              fontWeight: 600,
            }}
          >
            <div style={{ width: 14, height: 14, borderRadius: 4, background: C.yellow, display: "flex", alignItems: "center", justifyContent: "center", color: C.ink, fontSize: 10, fontWeight: 800 }}>
              ✓
            </div>
            {filled.name}
          </div>
        </div>
      ) : null}
    </div>
  );
};

// ---------------------------------------------------------------- spacelab nodes

export const NODE_COLORS = {
  text: { fg: C.nodeText, bg: "rgba(52,211,153,0.10)", border: "rgba(52,211,153,0.35)" },
  image: { fg: C.nodeImage, bg: "rgba(96,165,250,0.08)", border: "rgba(96,165,250,0.45)" },
  video: { fg: C.nodeVideo, bg: "rgba(167,139,250,0.08)", border: "rgba(167,139,250,0.45)" },
  model: { fg: C.yellow, bg: "rgba(254,204,21,0.08)", border: "rgba(254,204,21,0.5)" },
};

export const NodeLabel: React.FC<{ kind: keyof typeof NODE_COLORS; text: string; scale?: number }> = ({ kind, text, scale = 1 }) => {
  const c = NODE_COLORS[kind];
  const Icon = kind === "text" ? IText : kind === "image" ? IImage : kind === "video" ? IVideo : IPlay;
  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 6 * scale,
        padding: `${4 * scale}px ${8 * scale}px`,
        borderRadius: 7 * scale,
        background: c.bg,
        color: c.fg,
        fontFamily: FONT.ui,
        fontSize: 13 * scale,
        fontWeight: 600,
      }}
    >
      <Icon size={13 * scale} color={c.fg} />
      {text}
    </div>
  );
};

export const Port: React.FC<{ kind: keyof typeof NODE_COLORS; size?: number }> = ({ kind, size = 22 }) => {
  const c = NODE_COLORS[kind];
  const Icon = kind === "text" ? IText : kind === "image" ? IImage : kind === "video" ? IVideo : IPlay;
  return (
    <div
      style={{
        width: size,
        height: size,
        borderRadius: 999,
        background: C.ink,
        border: `1.5px solid ${c.border}`,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <Icon size={size * 0.52} color={c.fg} />
    </div>
  );
};

/** Section "see all" link */
export const SeeAll: React.FC<{ label?: string }> = ({ label = "All models" }) => (
  <div style={{ display: "flex", alignItems: "center", gap: 4, fontFamily: FONT.ui, fontSize: 14, color: C.textSubtle }}>
    {label} <IChevronRight size={14} color={C.textSubtle} />
  </div>
);
