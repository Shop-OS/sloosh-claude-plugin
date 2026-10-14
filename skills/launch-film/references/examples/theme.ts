import { loadFont as loadBowlby } from "@remotion/google-fonts/BowlbyOne";
import { loadFont as loadCaveat } from "@remotion/google-fonts/Caveat";
import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { loadFont as loadMono } from "@remotion/google-fonts/JetBrainsMono";

// Brand tokens captured from beta.sloosh.ai (computed styles) and the supplied logo SVG.
const bowlby = loadBowlby("normal", { weights: ["400"], subsets: ["latin"] });
const caveat = loadCaveat("normal", { weights: ["600", "700"], subsets: ["latin"] });
const inter = loadInter("normal", {
  weights: ["400", "500", "600", "700"],
  subsets: ["latin"],
});
const mono = loadMono("normal", { weights: ["400", "500", "700"], subsets: ["latin"] });

export const FONT = {
  // Site headline face: "Bowlby One"
  display: `${bowlby.fontFamily}, Inter, sans-serif`,
  // Site accent face: "Caveat"
  script: `${caveat.fontFamily}, cursive`,
  // Site body face: SF Pro Text with Inter fallback
  ui: `"SF Pro Text", "SF Pro Display", -apple-system, ${inter.fontFamily}, sans-serif`,
  // Technical annotations (editorial reference language)
  mono: `${mono.fontFamily}, ui-monospace, monospace`,
};

export const C = {
  // Surfaces (site: --neutral-950 / --layer-1..4)
  ink: "#0A0A0A",
  layer1: "#141414",
  layer2: "#1C1C1C",
  layer3: "#262626",
  layer4: "#303030",
  line: "rgba(255,255,255,0.08)",
  lineStrong: "rgba(255,255,255,0.14)",
  dim: "#707070",
  // Text
  white: "#FFFFFF",
  text: "#FAFAFA",
  textSubtle: "#D4D4D4",
  textMuted: "#A3A3A3",
  // Brand yellow (site CTA + logo gradient)
  yellow: "#FECC15",
  yellowTop: "#FDD943",
  yellowBottom: "#FAC01A",
  yellowEdge: "#AF8705",
  yellowText: "#FDD943",
  // Editorial paper (light punctuation frames)
  paper: "#EEECE6",
  paperLine: "rgba(10,10,10,0.14)",
  // Spacelab node accents (seen on /spacelab)
  nodeText: "#34D399",
  nodeImage: "#60A5FA",
  nodeVideo: "#A78BFA",
};

export const YELLOW_GRADIENT = `linear-gradient(180deg, ${C.yellowTop} 0%, ${C.yellowBottom} 100%)`;

export const W = 1920;
export const H = 1080;
export const FPS = 30;
