import React from "react";
import { Audio } from "@remotion/media";
import { staticFile, useVideoConfig } from "remotion";
import { SFX_PEAKS } from "./sfxPeaks";

/**
 * Cue-sheet sound engine.
 * - Each cue names the film frame where the sound's PEAK must land (`at`); the engine
 *   subtracts the measured peak offset (sfxPeaks.ts, written by scripts/sfx_prepare.py).
 * - SFX are ducked while the voice speaks (sidechain-style, from phrase intervals).
 * - Mono VOs are up-mixed ~+3 dB by the renderer, so VO gain defaults to 0.71.
 */
export type Cue = { s: string; at: number; v: number; label: string };
export type VoTrack = { name: string; src: string; from: number; gain?: number };

/** Phrase intervals (film seconds) from a VO object: { key: { start, end, ... } }. */
export const speechFrom = (vo: Record<string, unknown>): [number, number][] =>
  Object.values(vo).flatMap((p) =>
    p && typeof p === "object" && "start" in p && "end" in p
      ? [[(p as { start: number }).start, (p as { end: number }).end] as [number, number]]
      : [],
  );

const speechAt = (speech: [number, number][], sec: number) => {
  let v = 0;
  for (const [a, b] of speech) {
    if (sec >= a - 0.05 && sec <= b + 0.18) {
      const att = Math.min(1, (sec - (a - 0.05)) / 0.05);
      const rel = sec > b ? 1 - (sec - b) / 0.18 : 1;
      v = Math.max(v, Math.max(0, Math.min(att, rel)));
    }
  }
  return v;
};

export const SoundTrack: React.FC<{
  vo: VoTrack[];
  cues: Cue[];
  speech: [number, number][];
  /** global SFX bed level */
  trim?: number;
  /** fraction removed while the voice speaks (0.56 ≈ -7 dB) */
  duck?: number;
  /** offset (frames) added to every cue — lets a part's cue sheet sit inside a longer film */
  offset?: number;
}> = ({ vo, cues, speech, trim = 0.8, duck = 0.56, offset = 0 }) => {
  const { fps } = useVideoConfig();
  return (
    <>
      {vo.map((t) => (
        <Audio key={t.name} name={`VO · ${t.name}`} src={t.src} from={t.from} volume={t.gain ?? 0.71} premountFor={fps} />
      ))}
      {cues.map((c, i) => {
        const peak = SFX_PEAKS[c.s] ?? 0;
        const from = Math.max(0, Math.round(offset + c.at - peak * fps));
        return (
          <Audio
            key={`${c.s}-${i}`}
            name={`SFX · ${c.label}`}
            src={staticFile(`sfx/${c.s}.wav`)}
            from={from}
            volume={(f) => c.v * trim * (1 - duck * speechAt(speech, (from + f) / fps))}
            premountFor={fps}
          />
        );
      })}
    </>
  );
};
