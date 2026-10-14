# Pitfalls (each one cost real time once)

| Symptom | Cause | Fix |
|---|---|---|
| `captureElementImage ... No cached paint record` | `HtmlInCanvasMotionBlur` broken in this renderer build | Use the engine `MotionBlur` (Freeze samples + plus-lighter) |
| Motion blur shows a ghost of the previous shot on the first frame after an internal cut | trailing shutter samples straddle the cut | `samplesAt` returns 1 on the first frame after the cut |
| Masks/filters render with another sample's geometry | duplicate SVG `id`s across motion-blur copies | module counter + `useMemo` for every id |
| Zoom-through ends on a nearly white frame | push not finished before the boundary | finish the zoom 1–2 frames early; log-space `k` |
| Whip pans strobe | too few samples for the per-frame distance | 16 samples + `smearAt` gaussian |
| 3D page looks tiny in a dark void | camera z too negative | working distance z 100–500; see motion-and-camera §4 |
| Important button cut off at frame bottom | focus point too high | lower `ty` / add `sy` so the action is inside the safe area |
| Contact-sheet expansion not complete at the cut | expansion timed past scene end | end it ≥ 1 frame before the boundary |
| Crop shows the poster's own headline next to the overlay copy | baked-in text | `cleanplate.py`, or choose crops excluding the text |
| Overlay headline invisible over a dark object | dark-on-dark | move the text to clear wall area (right-aligned stack) |
| Mix clips (+2 dBFS) | mono VO up-mixed +3 dB, SFX too hot | `VO_GAIN ≈ 0.71`, ducking, lower transition hits |
| `ffmpeg … offset=0.44inear=true` parse error | zsh `$OFF:l` modifier | write `${OFF}` before any `:` |
| PIL import fails in your own script | `python3 -I` drops user site-packages | run your scripts without `-I` (keep `-I` for untrusted downloads) |
| Bash `cd` moved the session's working directory | `cd` persists | absolute paths everywhere |
| Whisper word times slightly late/early | whisper token alignment | cross-check with `silencedetect` (phrase starts/ends) |
| Script PDF wording ≠ recorded VO | revised recording | transcribe; never build from the PDF |
| HEVC 10-bit clip slow or wrong colours | codec | `prep_video.sh` to H.264 yuv420p |
| Images soft when zoomed | logical PNG scaled > 1.2× | 2× Lanczos HD versions |
| Pixel wipe leaves dark squares at the end | accent cells still on at p = 1 | only draw accent cells while p < 0.82 |
| First frame of a part is a blank colour for many frames | animations start late | start guides/drawing on frame 0–2 |
| Same product repeated across an end card | lazy layout | rebalance: one card per story/product |
