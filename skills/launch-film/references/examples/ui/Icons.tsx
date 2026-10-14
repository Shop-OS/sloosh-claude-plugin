import React from "react";

type P = { size?: number; color?: string; stroke?: number; style?: React.CSSProperties };

const S: React.FC<P & { children: React.ReactNode; vb?: string }> = ({ size = 18, color = "currentColor", stroke = 1.8, style, children, vb = "0 0 24 24" }) => (
  <svg
    width={size}
    height={size}
    viewBox={vb}
    fill="none"
    stroke={color}
    strokeWidth={stroke}
    strokeLinecap="round"
    strokeLinejoin="round"
    style={{ display: "block", flexShrink: 0, ...style }}
  >
    {children}
  </svg>
);

export const IPlay: React.FC<P> = (p) => (
  <S {...p}>
    <path d="M7 5.5v13l11-6.5z" />
  </S>
);
export const IPlus: React.FC<P> = (p) => (
  <S {...p}>
    <path d="M12 5v14M5 12h14" />
  </S>
);
export const IArrowUp: React.FC<P> = (p) => (
  <S {...p}>
    <path d="M12 19V5M6 11l6-6 6 6" />
  </S>
);
export const IArrowRight: React.FC<P> = (p) => (
  <S {...p}>
    <path d="M5 12h14M13 6l6 6-6 6" />
  </S>
);
export const IChevronRight: React.FC<P> = (p) => (
  <S {...p}>
    <path d="M9 6l6 6-6 6" />
  </S>
);
export const IChevronDown: React.FC<P> = (p) => (
  <S {...p}>
    <path d="M6 9l6 6 6-6" />
  </S>
);
export const IUpload: React.FC<P> = (p) => (
  <S {...p}>
    <path d="M12 16V4M7 9l5-5 5 5M4 16v3a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-3" />
  </S>
);
export const IImage: React.FC<P> = (p) => (
  <S {...p}>
    <rect x="3.5" y="4.5" width="17" height="15" rx="2.5" />
    <circle cx="9" cy="10" r="1.6" />
    <path d="M20.5 16l-5-5-8.5 8.5" />
  </S>
);
export const IVideo: React.FC<P> = (p) => (
  <S {...p}>
    <rect x="3" y="6" width="13" height="12" rx="2.5" />
    <path d="M16 10.5l5-3v9l-5-3z" />
  </S>
);
export const IText: React.FC<P> = (p) => (
  <S {...p}>
    <path d="M5 6h14M12 6v13" />
  </S>
);
export const ISun: React.FC<P> = (p) => (
  <S {...p}>
    <circle cx="12" cy="12" r="4" />
    <path d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2M5.3 5.3l1.4 1.4M17.3 17.3l1.4 1.4M5.3 18.7l1.4-1.4M17.3 6.7l1.4-1.4" />
  </S>
);
export const IBell: React.FC<P> = (p) => (
  <S {...p}>
    <path d="M6 16V11a6 6 0 1 1 12 0v5l1.5 2h-15z" />
    <path d="M10 20.5a2.2 2.2 0 0 0 4 0" />
  </S>
);
export const ISparkle: React.FC<P> = (p) => (
  <S {...p}>
    <path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z" />
  </S>
);
export const ICompass: React.FC<P> = (p) => (
  <S {...p}>
    <circle cx="12" cy="12" r="8.5" />
    <path d="M15.5 8.5l-2 5-5 2 2-5z" />
  </S>
);
export const IHeart: React.FC<P> = (p) => (
  <S {...p}>
    <path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z" />
  </S>
);
export const IShare: React.FC<P> = (p) => (
  <S {...p}>
    <circle cx="6" cy="12" r="2.2" />
    <circle cx="18" cy="6" r="2.2" />
    <circle cx="18" cy="18" r="2.2" />
    <path d="M8 11l8-4M8 13l8 4" />
  </S>
);
export const ICheck: React.FC<P> = (p) => (
  <S {...p}>
    <path d="M5 12.5l4.5 4.5L19 7.5" />
  </S>
);
export const ILock: React.FC<P> = (p) => (
  <S {...p}>
    <rect x="5" y="10.5" width="14" height="10" rx="2" />
    <path d="M8 10.5V8a4 4 0 0 1 8 0v2.5" />
  </S>
);
export const ICoin: React.FC<P> = ({ size = 18, style }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" style={{ display: "block", ...style }}>
    <circle cx="12" cy="12" r="10" fill="#FECC15" />
    <circle cx="12" cy="12" r="6.2" fill="none" stroke="#AF8705" strokeWidth="1.8" />
  </svg>
);
export const ISearch: React.FC<P> = (p) => (
  <S {...p}>
    <circle cx="11" cy="11" r="6.5" />
    <path d="M16 16l4 4" />
  </S>
);
export const ISliders: React.FC<P> = (p) => (
  <S {...p}>
    <path d="M4 7h10M18 7h2M4 17h4M12 17h8" />
    <circle cx="16" cy="7" r="2" />
    <circle cx="10" cy="17" r="2" />
  </S>
);
export const IFlask: React.FC<P> = (p) => (
  <S {...p}>
    <path d="M9 3h6M10 3v6l-5 9a2 2 0 0 0 1.8 3h10.4A2 2 0 0 0 19 18l-5-9V3" />
  </S>
);
export const IGrid: React.FC<P> = (p) => (
  <S {...p}>
    <rect x="4" y="4" width="7" height="7" rx="1.5" />
    <rect x="13" y="4" width="7" height="7" rx="1.5" />
    <rect x="4" y="13" width="7" height="7" rx="1.5" />
    <rect x="13" y="13" width="7" height="7" rx="1.5" />
  </S>
);
export const IInfo: React.FC<P> = (p) => (
  <S {...p}>
    <circle cx="12" cy="12" r="8.5" />
    <path d="M12 11v5M12 8h.01" />
  </S>
);
export const IStar: React.FC<P & { fill?: string }> = ({ size = 18, color = "#FECC15", fill = "#FECC15", style }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" style={{ display: "block", ...style }}>
    <path
      d="M12 3.2l2.6 5.5 6 .8-4.4 4.1 1.1 5.9L12 16.6l-5.3 2.9 1.1-5.9-4.4-4.1 6-.8z"
      fill={fill}
      stroke={color}
      strokeWidth="1.2"
      strokeLinejoin="round"
    />
  </svg>
);
