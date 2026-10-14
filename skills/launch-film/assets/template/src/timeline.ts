// Paste the block printed by scripts/transcribe.sh here. Times are film seconds
// (VO time + VO_OFFSET). Every scene boundary below should be a designed match cut.

export const FPS = 30;
export const VO_OFFSET = 15; // frames of pre-roll before the first word

const v = (voSeconds: number) => voSeconds + VO_OFFSET / FPS;

export const VO = {
  // example — replace with transcription output
  line1: { start: v(0.05), end: v(0.94) },
  line2: { start: v(1.27), end: v(2.28) },
};

export const SCENES = {
  open: { from: 0, dur: 45 },
  next: { from: 45, dur: 45 },
} as const;

export const TOTAL_FRAMES = 90;
