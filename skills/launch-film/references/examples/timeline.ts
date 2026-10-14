// All times derive from the PART 3 voiceover transcription (whisper.cpp small.en,
// phrase boundaries cross-checked with ffmpeg silencedetect at -35 dB).
// The VO is placed VO_OFFSET frames into the film to allow a short grid pre-roll.

export const FPS = 30;
export const VO_OFFSET = 18; // frames (0.6s)

const v = (voSeconds: number) => voSeconds + VO_OFFSET / FPS; // VO time -> film seconds

// Film-time (seconds) for each spoken phrase.
export const VO = {
  meetSloosh: { start: v(0.05), end: v(0.94), sloosh: v(0.46) },
  bringIdea: { start: v(1.27), end: v(2.28), idea: v(1.97) },
  choose: { start: v(2.55), end: v(3.7), make: v(3.36) },
  creative: { start: v(4.02), end: v(5.09), workflows: v(4.51) },
  prepared: { start: v(5.31), end: v(7.1), help: v(6.16), there: v(6.79) },
  bringPhoto: { start: v(7.49), end: v(8.26), photo: v(7.94) },
  explore: { start: v(8.52), end: v(10.14), possibilities: v(9.18) },
  details: { start: v(10.42), end: v(12.35), detailsWord: v(10.74), yours: v(11.95) },
  yourCake: { start: v(12.68), end: v(13.47), cake: v(13.1) },
  onTheMoon: { start: v(13.72), end: v(14.53), moon: v(14.17) },
  yourPhotograph: { start: v(14.79), end: v(15.85), photograph: v(15.18) },
  visualStory: { start: v(16.06), end: v(17.47), visual: v(16.37), story: v(16.91) },
  yourProduct: { start: v(17.76), end: v(18.61), product: v(18.15) },
  campaign: { start: v(18.83), end: v(20.84), campaignWord: v(18.95), feels: v(19.7), you: v(20.38) },
  fileEnd: v(21.08),
};

// Scene table in frames. Every boundary is a designed match cut.
export const SCENES = {
  logo: { from: 0, dur: 54 }, // Meet Sloosh.
  idea: { from: 54, dur: 38 }, // You bring the idea.
  choose: { from: 92, dur: 44 }, // Choose what you want to make.
  creative: { from: 136, dur: 40 }, // Creative workflows
  spaces: { from: 176, dur: 64 }, // already prepared to help you get there.
  bringPhoto: { from: 240, dur: 33 }, // Bring your photo.
  explore: { from: 273, dur: 57 }, // Explore the possibilities.
  cake: { from: 330, dur: 132 }, // Keep the details… / Your cake. / On the moon.
  cup: { from: 462, dur: 88 }, // Your photograph. / A new visual story.
  product: { from: 550, dur: 32 }, // Your product.
  finale: { from: 582, dur: 168 }, // A campaign that feels like you. + resolve
} as const;

export const TOTAL_FRAMES = 750;

/** Seconds relative to the start of a scene, for a film-time timestamp. */
export const rel = (scene: keyof typeof SCENES, filmSeconds: number) =>
  filmSeconds - SCENES[scene].from / FPS;
