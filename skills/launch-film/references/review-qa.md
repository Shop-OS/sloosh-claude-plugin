# Review loop and QA checklist

You cannot watch the film or hear it, so review is measurement plus contact sheets.

## 1. Render fast, look often
`bash scripts/render_review.sh <project> <Comp> <out_dir> [from-to]` renders a JPEG
sequence (q85, concurrency 8) — a 25 s film takes about a minute. Then:

```bash
python3 scripts/sheet.py <out_dir> <sheet.jpg> "92,95,98,101,104,108" 4 480
```

Make one sheet per scene with frames at the cut, mid-moves, and every labelled beat. Read
each sheet critically, as a viewer would.

## 2. What to look for
- **Framing**: does the subject fill the frame? Any shot where UI floats small in a void,
  or the important element sits at the frame edge (e.g. a button half cut off)?
- **Legibility**: can the viewer read the line that matters at that moment?
- **Empty frames**: first/last frames of scenes that show nothing (a whip that starts
  off-screen is fine for 1 frame, not 3).
- **Cuts**: does the last frame of a shot already equal the first frame of the next for
  tile/zoom-through hand-offs? Does an object-locked cut actually lock?
- **Doubled or clipped text**: cropped posters showing original headline + your copy;
  labels overlapping cards; text crossing dark hair/objects (dark-on-dark).
- **Layering**: cards overlapping labels; tags hidden behind other cards.
- **Motion blur**: strobing copies (needs more samples or smear) or blending across a cut.
- **Variety**: the end card shouldn't repeat one product four times.

## 3. Match-cut verification
`bash scripts/blend_check.sh <seq_dir_or_mp4> <frame> <out.jpg>` blends frame N−1 and N
50/50 (with a grid). The shared object should overlap. Adjust measured boxes or offsets if
not.

## 4. Full-resolution spot checks
Extract 2–3 frames from the final file (`ffmpeg -ss T -i out.mp4 -frames:v 1 f.jpg`) and
look at them at 100 % — text sharpness, image softness from over-scaling, grain level.
For 4K, crop a 1600×900 region.

## 5. Audio
- `python3 scripts/mixcheck.py out/mix.wav public/vo/x.mp3 <offset>`: VO gain should be
  ≈ 1.0, mix peak < −1 dBFS, SFX ≥ 6–8 dB under speech.
- Mastered file: `-14 LUFS`, `-1 dBTP` (`ebur128=peak=true`).

## 6. Final checklist
- [ ] Every scene boundary is a designed match cut (or deliberate punctuation)
- [ ] Cuts land 0–2 frames before the phrase they illustrate
- [ ] Brand fonts/colours everywhere; reference palette not leaking in
- [ ] No user account data on screen; no invented claims or numbers
- [ ] Mocks labelled and listed; mirrored images and clean plates noted
- [ ] Motion blur on fast moves only; no blending across cuts
- [ ] SFX from the user's library only, no music unless asked; peaks on cuts
- [ ] Mix: voice clear, no clipping; master −14 LUFS / −1 dBTP
- [ ] Output: 1920×1080 H.264 High bt709 30 fps, AAC 48 kHz 320 k (+ 4K if requested)
- [ ] README with shot map, mocks, how to re-render
