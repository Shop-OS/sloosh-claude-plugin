import { loadFont as loadDisplay } from "@remotion/google-fonts/BowlbyOne";
import { loadFont as loadScript } from "@remotion/google-fonts/Caveat";
import { loadFont as loadUi } from "@remotion/google-fonts/Inter";
import { loadFont as loadMono } from "@remotion/google-fonts/JetBrainsMono";

// Replace with the brand captured from the website (references/brand-capture.md).
// Keep the role names: components in src/components depend on them.
const display = loadDisplay("normal", { weights: ["400"], subsets: ["latin"] });
const script = loadScript("normal", { weights: ["600", "700"], subsets: ["latin"] });
const ui = loadUi("normal", { weights: ["300", "400", "500", "600", "700"], subsets: ["latin"] });
const mono = loadMono("normal", { weights: ["400", "500", "700"], subsets: ["latin"] });

export const FONT = {
  display: `${display.fontFamily}, sans-serif`,
  script: `${script.fontFamily}, cursive`,
  ui: `"SF Pro Text", -apple-system, ${ui.fontFamily}, sans-serif`,
  mono: `${mono.fontFamily}, ui-monospace, monospace`,
};

export const C = {
  // surfaces
  ink: "#0A0A0A",
  layer1: "#141414",
  layer2: "#1C1C1C",
  layer3: "#262626",
  layer4: "#303030",
  line: "rgba(255,255,255,0.08)",
  lineStrong: "rgba(255,255,255,0.14)",
  // text
  white: "#FFFFFF",
  text: "#FAFAFA",
  textSubtle: "#D4D4D4",
  textMuted: "#A3A3A3",
  // accent (brand CTA colour) + its pressed-key edge
  accent: "#FECC15",
  accentTop: "#FDD943",
  accentBottom: "#FAC01A",
  accentEdge: "#AF8705",
  accentText: "#FDD943",
  // editorial paper frames
  paper: "#EEECE6",
  paperLine: "rgba(10,10,10,0.2)",
  // failures / "wrong" annotations (use sparingly)
  warn: "#EF4444",
};

export const W = 1920;
export const H = 1080;
