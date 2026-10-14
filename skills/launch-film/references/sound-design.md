# Sound design (local SFX library, no music)

## Contents
1. Analyse the library
2. Roles and picking
3. Preparing files
4. The cue sheet
5. Ducking and VO gain
6. Checking the mix
7. Mastering

## 1. Analyse the library

`python3 scripts/sfx_analyze.py "<sfx_root>" > sfx_index.tsv`

Columns: category, file, duration, attack (first time RMS > 25 % of max), peak (time of max
RMS), end (last time RMS > 10 %), peak dBFS, RMS dBFS. The **peak** is what you align to a
cut. Libraries often bury the peak late (a "pass-by" whoosh peaking at 0.95 s) — that's why
you never place a sound by its start.

## 2. Roles and picking

| Role | Typical files | Placement |
|---|---|---|
| Whoosh short (peak 0.13–0.3 s) | "Deep, Mini, Whoosh" 1/13/14/15 | cuts, pushes, card flights |
| Whoosh pass/mid (peak 0.4–1.2 s) | "Whoosh (4/19/20)", "Deeper FX" | camera swoops, pull-backs |
| Riser | "Riser Starter/Faster", Transform "Risers" | build into a reveal (peak on reveal) |
| Impact | "Hit Impact (No FX) 2", "(with fx) 4/9", "Sub Drop", "Middle Impact" | punctuation words, hero cuts, end card |
| UI | mouse clicks, pop-ups, magnetic, granular select, approve | clicks, drops, snaps, badges |
| Typing | short typing bursts, enter | chat boxes, prompt typing |
| Scan/glitch | "Scan, Flicker, Text", "Glitch, Flicker, Text", "Number, Code" | labels typing, overlays, failures |
| Foley | camera shutter, paper flip, drop, friction | photographs, prints, drag & drop |
| Sparkle/shimmer | "Sparkle Whoosh", "Shimmer" | results appearing, logo eyes |
| List ticks | "Mini list up/down" | staggered cards |

Pick 40–70 files for a 20–30 s film. Prefer short, clean transients under speech; longer,
fuller sounds in gaps.

## 3. Preparing files

`python3 scripts/sfx_prepare.py sfx_selection.json <project>/public/sfx --ts <project>/src/sfxPeaks.ts`

`sfx_selection.json` maps a short name to `{ "src": "<abs path>", "max": seconds,
"lead": seconds-to-trim }`. The script trims, fades the tail, peak-normalises to −1 dBFS,
converts to 48 kHz stereo WAV and writes `peaks.json` measured on the trimmed file.

## 4. The cue sheet

In `src/cues.ts` each cue is `{ s: name, at: frame, v: volume, label }` where `at` is
the frame the **peak** must land on. The engine computes `from = at − peak·fps`.
- One accent per cut; layer at most a whoosh + a hit on hero cuts.
- UI sounds land on the visual action frame (click = press frame, drop = landing frame).
- Volumes before ducking: whooshes 0.25–0.5, hits 0.3–0.45, UI 0.15–0.45, ticks 0.1–0.15,
  scans 0.1–0.2.

## 5. Ducking and VO gain

- The engine reads speech intervals from the `VO` object and multiplies each SFX by
  `1 − DUCK·speech(t)` (DUCK ≈ 0.56 → −7 dB) with 50 ms attack / 180 ms release.
- A mono VO is up-mixed about +3 dB by the renderer: set `VO_GAIN ≈ 0.71` so the voice
  sits at unity and the mix doesn't clip.

## 6. Checking the mix

Render audio only: `npx remotion render <Comp> out/mix.wav --codec=wav`, then
`python3 scripts/mixcheck.py out/mix.wav <vo> <offset>`. It subtracts the VO and prints
VO vs SFX level per 250 ms. Targets: during speech (VO > −25 dB) SFX ≤ −6…−8 dB under the
voice; mix peak below −1 dBFS. Where a transition hit masks the first word after a cut,
lower it or move its peak 1–2 frames earlier.

## 7. Mastering

`scripts/master.sh` does two-pass `loudnorm` (I = −14 LUFS, TP = −1 dBTP, LRA 11) on the
rendered mix and muxes it onto the video with `-c:v copy`. Verify with
`ffmpeg -i out.mp4 -af ebur128=peak=true -f null -`.
