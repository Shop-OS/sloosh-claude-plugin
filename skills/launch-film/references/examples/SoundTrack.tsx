import React from "react";
import { Audio } from "@remotion/media";
import { staticFile, useVideoConfig } from "remotion";
import { VO, VO_OFFSET } from "./timeline";

// Peak offsets (seconds) measured with an RMS envelope on the trimmed Botanica V4 files.
const PEAK: Record<string, number> = {
  whoosh_short_a: 0.27,
  whoosh_short_b: 0.19,
  whoosh_short_c: 0.15,
  whoosh_tiny: 0.13,
  whoosh_pass: 0.95,
  whoosh_mid_a: 0.43,
  whoosh_mid_b: 0.43,
  whoosh_mid_c: 0.57,
  whoosh_deep: 1.19,
  whoosh_big: 1.35,
  sparkle_whoosh: 0.31,
  sparkle_whoosh_b: 0.65,
  shimmer: 0.49,
  botanical_whoosh: 0.27,
  botanical_whoosh_b: 0.65,
  riser_short: 0.79,
  riser_faster: 1.01,
  riser_starter: 1.13,
  hit_clean: 0.07,
  hit_fx_short: 0.07,
  hit_fx_b: 0.09,
  sub_drop: 0.01,
  middle_impact: 0.59,
  riser_bang: 1.65,
  glitch_impact: 0.15,
  formation: 0.03,
  speed_transform: 0.53,
  stretching: 0.69,
  sliding_count: 0.47,
  flip: 0.39,
  click_a: 0.03,
  click_b: 0.01,
  click_c: 0.03,
  pop_a: 0.01,
  pop_b: 0.01,
  magnetic: 0.07,
  select_a: 0.05,
  select_b: 0.17,
  approve: 0.13,
  approve_b: 0.01,
  sparkle_button: 0.27,
  shutter: 0.33,
  paper_flip: 0.27,
  drop: 0.03,
  friction: 0.51,
  typing_a: 0.41,
  typing_b: 0.21,
  key_single: 0.03,
  scan_a: 0.35,
  scan_b: 0.89,
  scan_c: 0.25,
  glitch_text_a: 0.03,
  glitch_text_b: 0.15,
  glitch_text_c: 0.11,
  code_scan: 0.49,
  splash_a: 0.17,
  splash_b: 0.01,
  splash_c: 0.07,
  list_up: 0.09,
  list_up_b: 0.09,
  list_down: 0.09,
};

type Cue = { s: keyof typeof PEAK | string; at: number; v: number; label: string };

// `at` = film frame where the sound's peak should land.
export const CUES: Cue[] = [
  // A · Meet Sloosh
  { s: "scan_a", at: 10, v: 0.16, label: "guides draw" },
  { s: "riser_starter", at: 34, v: 0.2, label: "build to the eyes" },
  { s: "formation", at: 18, v: 0.2, label: "letters rise" },
  { s: "select_b", at: 22, v: 0.12, label: "letter tick" },
  { s: "pop_a", at: 31, v: 0.34, label: "eyes open" },
  { s: "hit_fx_short", at: 38, v: 0.3, label: "yellow punctuation" },
  { s: "glitch_text_c", at: 41, v: 0.16, label: "black punctuation" },
  { s: "whoosh_short_a", at: 51, v: 0.36, label: "push through pupil" },
  // B · You bring the idea
  { s: "friction", at: 66, v: 0.13, label: "sketching" },
  { s: "splash_a", at: 71, v: 0.1, label: "berries" },
  { s: "magnetic", at: 77, v: 0.3, label: "idea frame snaps" },
  { s: "whoosh_short_b", at: 91, v: 0.5, label: "whip out" },
  // C · Choose what you want to make
  { s: "whoosh_deep", at: 97, v: 0.22, label: "page arrives" },
  { s: "list_up", at: 98, v: 0.13, label: "chips" },
  { s: "list_up_b", at: 104, v: 0.11, label: "chips" },
  { s: "whoosh_pass", at: 112, v: 0.22, label: "swoop down the page" },
  { s: "click_a", at: 118, v: 0.45, label: "choose Food Styling" },
  { s: "approve", at: 120, v: 0.22, label: "selected" },
  { s: "glitch_text_b", at: 127, v: 0.24, label: "pixel wipe" },
  { s: "whoosh_tiny", at: 134, v: 0.28, label: "into yellow" },
  // D · Creative workflows
  { s: "hit_clean", at: 137, v: 0.4, label: "CREATIVE slam" },
  { s: "code_scan", at: 145, v: 0.13, label: "output flashes" },
  { s: "hit_fx_b", at: 153, v: 0.34, label: "WORKFLOWS cut" },
  { s: "sliding_count", at: 164, v: 0.2, label: "signal through the chain" },
  { s: "pop_b", at: 170, v: 0.3, label: "badge" },
  // E · Prepared
  { s: "whoosh_mid_b", at: 182, v: 0.22, label: "pull back from badge" },
  { s: "list_up_b", at: 182, v: 0.13, label: "cards stagger" },
  { s: "list_up", at: 188, v: 0.11, label: "cards stagger" },
  { s: "select_a", at: 216, v: 0.14, label: "hover" },
  { s: "click_c", at: 222, v: 0.45, label: "select workflow" },
  { s: "whoosh_short_c", at: 239, v: 0.34, label: "push into card" },
  // F · Bring your photo
  { s: "whoosh_tiny", at: 247, v: 0.24, label: "print flies in" },
  { s: "paper_flip", at: 250, v: 0.18, label: "print" },
  { s: "drop", at: 256, v: 0.36, label: "drop into slot" },
  { s: "pop_a", at: 261, v: 0.2, label: "scene photo" },
  { s: "click_a", at: 268, v: 0.45, label: "Generate" },
  { s: "sparkle_button", at: 270, v: 0.28, label: "generate sparkle" },
  { s: "whoosh_short_a", at: 273, v: 0.32, label: "push into cake" },
  // G · Explore the possibilities
  { s: "whoosh_mid_c", at: 285, v: 0.33, label: "canvas reveal" },
  { s: "list_up_b", at: 289, v: 0.12, label: "outputs" },
  { s: "shimmer", at: 295, v: 0.3, label: "possibilities" },
  { s: "list_up", at: 296, v: 0.1, label: "outputs" },
  { s: "glitch_text_a", at: 317, v: 0.28, label: "contact sheet cut" },
  { s: "splash_b", at: 318, v: 0.18, label: "tiles slide" },
  { s: "whoosh_tiny", at: 328, v: 0.28, label: "source tile expands" },
  // H–J · Details / Your cake / On the moon
  { s: "scan_c", at: 340, v: 0.18, label: "detail windows" },
  { s: "glitch_text_c", at: 341, v: 0.11, label: "window" },
  { s: "glitch_text_c", at: 346, v: 0.1, label: "window" },
  { s: "glitch_text_c", at: 351, v: 0.1, label: "window" },
  { s: "code_scan", at: 356, v: 0.1, label: "readout" },
  { s: "hit_clean", at: 376, v: 0.42, label: "YOURS." },
  { s: "hit_fx_short", at: 376, v: 0.22, label: "YOURS. layer" },
  { s: "whoosh_mid_a", at: 394, v: 0.28, label: "pull back to the baker" },
  { s: "whoosh_short_a", at: 428, v: 0.27, label: "match cut to the moon" },
  { s: "sub_drop", at: 428, v: 0.22, label: "moon weight" },
  { s: "shimmer", at: 437, v: 0.2, label: "stars" },
  { s: "shutter", at: 460, v: 0.42, label: "shutter flash" },
  // K–L · Your photograph / A new visual story
  { s: "paper_flip", at: 467, v: 0.2, label: "print lands" },
  { s: "magnetic", at: 472, v: 0.24, label: "focus lock" },
  { s: "whoosh_short_c", at: 499, v: 0.22, label: "match cut to café" },
  { s: "hit_fx_short", at: 499, v: 0.15, label: "match cut layer" },
  { s: "speed_transform", at: 514, v: 0.2, label: "storyboard forms" },
  { s: "list_up", at: 510, v: 0.13, label: "frames" },
  { s: "list_up_b", at: 517, v: 0.11, label: "frames" },
  { s: "sliding_count", at: 534, v: 0.14, label: "playhead" },
  { s: "whoosh_short_b", at: 548, v: 0.3, label: "whip to product" },
  // M · Your product
  { s: "scan_a", at: 556, v: 0.16, label: "guides" },
  { s: "magnetic", at: 562, v: 0.3, label: "product frame" },
  { s: "glitch_text_a", at: 564, v: 0.11, label: "label" },
  // N–O · Campaign + resolve
  { s: "botanical_whoosh", at: 582, v: 0.34, label: "match cut to poster" },
  { s: "hit_clean", at: 582, v: 0.34, label: "poster" },
  { s: "formation", at: 586, v: 0.22, label: "campaign board" },
  { s: "list_up", at: 591, v: 0.13, label: "format" },
  { s: "list_up_b", at: 595, v: 0.12, label: "format" },
  { s: "list_up", at: 599, v: 0.11, label: "format" },
  { s: "whoosh_big", at: 660, v: 0.28, label: "spread / pull back" },
  { s: "select_a", at: 647, v: 0.11, label: "logo letters" },
  { s: "select_b", at: 652, v: 0.11, label: "logo letters" },
  { s: "pop_a", at: 657, v: 0.38, label: "eyes open on 'you'" },
  { s: "shimmer", at: 660, v: 0.24, label: "eyes sparkle" },
  { s: "middle_impact", at: 667, v: 0.28, label: "headline lands" },
  { s: "list_up_b", at: 683, v: 0.14, label: "CTAs" },
  { s: "click_a", at: 715, v: 0.5, label: "Start creating" },
  { s: "approve_b", at: 716, v: 0.28, label: "confirm" },
  { s: "sparkle_button", at: 719, v: 0.24, label: "button glow" },
  { s: "magnetic", at: 731, v: 0.12, label: "blink" },
];

// Spoken phrases in film seconds (from the transcription) for sidechain-style ducking.
const SPEECH: [number, number][] = Object.values(VO).flatMap((p) =>
  typeof p === "object" ? [[p.start, p.end] as [number, number]] : [],
);

/** 1 while the voice is speaking (with 50 ms attack / 180 ms release), else 0. */
const speechAt = (sec: number) => {
  let v = 0;
  for (const [a, b] of SPEECH) {
    if (sec >= a - 0.05 && sec <= b + 0.18) {
      const att = Math.min(1, (sec - (a - 0.05)) / 0.05);
      const rel = sec > b ? 1 - (sec - b) / 0.18 : 1;
      v = Math.max(v, Math.max(0, Math.min(att, rel)));
    }
  }
  return v;
};

const SFX_TRIM = 0.8; // global bed level
const DUCK = 0.56; // amount removed while the voice is speaking (≈ -7 dB)
// The mono VO is up-mixed ~+3 dB by the renderer; bring it back to unity.
const VO_GAIN = 0.71;

export const SoundTrack: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <>
      <Audio name="Voiceover · PART 3" src={staticFile("vo/part3.mp3")} from={VO_OFFSET} volume={VO_GAIN} premountFor={fps} />
      {CUES.map((c, i) => {
        const peak = PEAK[c.s] ?? 0;
        const from = Math.max(0, Math.round(c.at - peak * fps));
        return (
          <Audio
            key={`${c.s}-${i}`}
            name={`SFX · ${c.label}`}
            src={staticFile(`sfx/${c.s}.wav`)}
            from={from}
            volume={(f) => c.v * SFX_TRIM * (1 - DUCK * speechAt((from + f) / fps))}
            premountFor={fps}
          />
        );
      })}
    </>
  );
};
