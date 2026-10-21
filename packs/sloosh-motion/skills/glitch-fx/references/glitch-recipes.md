# Glitch recipes: exact calls per artefact (per-frame Python in edit.py is the default, clipfx.py bakes are optional)

`C=<director>/scripts/clipfx.py`, where `<director>` is the sloosh-motion-director skill folder (a sibling of glitch-fx). Default route: every artefact below has a per-frame function in `lib/glitchkit.py` (table at the end), applied in edit.py
on the clean footage, frame-exact. Use the clipfx bakes only for the real datamosh (always) and for long sustained treatments.
All clipfx outputs H.264 yuv420p BT.709 CRF 16, no audio (add `keep_audio=1` on the filter treatments).
Trim to the seconds you need first (`ffmpeg -ss <in> -t <len> -i x.mp4 -c:v libx264 -crf 16 x_t.mp4`): the numpy engine is CPU-bound.

## Hits on footage (baked windows)
| Artefact | Command | Notes |
|---|---|---|
| Slice displacement + RGB split | `python3 $C glitch in.mp4 out.mp4 mode=slices+rgb times=0.53,1.53 frames=4 amp=0.08 n=12 seed=3` | amp = fraction of width; 42% of bands move; intensity decays to 50% over the window |
| Macroblock corruption | `... mode=blocks+rgb times=… frames=4 bs=48 amp=0.18 tint=ff2d7a` | blocks copied from offset positions, 25% channel-swapped, some tinted, some posterised |
| Pixel-sort drips | `... mode=sort times=… frames=6 thr=150 cols=0.35 len=220` | bright pixels smear downward on 35% of columns; slow (row loop) — keep windows short |
| Sine wave warp | `... mode=wave amp=0.035 wl=320 hz=1` (no `times` = whole clip) | the "liquid" look of Ref A; also `+scan` |
| Static / signal lost | `... mode=static times=… frames=3` | half-res luma snow 75% + one bright roll band |
| Tear dashes | `... mode=static+tear` or `mode=tear tint=ffd6e6` | white/pink 2–6 px dashes + thin band shifts (Ref A @ 7.6 s) |
| Scanline darkening | `... mode=scan` (only during hits) or `scanlines gap=4 op=0.3` (whole clip, fast) | never < 3 px pitch at 1080 wide |
| Any filter treatment as a hit | `python3 $C hits in.mp4 out.mp4 times=… kind=<threshold|invert|xray|duotone|posterize|thermal|pixelate|rgbsplit> frames=3` | the director's hits command; works with the filter treatments |

## Transitions
| Artefact | Command |
|---|---|
| Real datamosh A→B | `python3 $C datamosh a.mp4 b.mp4 out.mp4 len=0.8` (mosh starts at duration(A); `len=0` = never resolves) |
| Pixel mosaic out | `python3 $C hits a.mp4 a_px.mp4 times=<last 4 frames> kind=pixelate frames=4 s=48` |
| White line wipe | `gk.Transitions(footage, [(t, "linewipe", 5)])` |
| Slice cut / block cut / mosaic | `gk.Transitions` kinds `slicecut` `blockcut` `mosaic` |

## Sustained looks (whole shot)
| Look | Command |
|---|---|
| VHS fast | `python3 $C vhslite in.mp4 out.mp4` (fast: plain filters, no geq) |
| VHS heavy (slow geq) | `python3 $C vhs in.mp4 out.mp4` (≈ 1 min per 3 s at 1080x1920) |
| Echo ghosting | `python3 $C echo in.mp4 out.mp4 n=8` |
| Thermal false colour | `python3 $C thermal in.mp4 out.mp4 preset=turbo` (also magma, inferno, plasma) |
| Lens CA (permanent, subtle) | `python3 $C ca in.mp4 out.mp4 px=3` |
| Cyan data mono | `python3 $C duotone in.mp4 out.mp4 dark=03080a light=7fe3f0` then `scanlines gap=4 op=0.25` |
| Mirror totem (Cyber) | `ffmpeg -i in.mp4 -vf "crop=iw/2:ih:0:0,split[a][b];[b]hflip[c];[a][c]hstack" out.mp4` |
| Selective colour (Mono + One) | `python3 $C selective in.mp4 out.mp4 color=2fa84f sim=0.25` |

## glitchkit.py equivalents (per frame, seeded by the film frame number)
| Artefact | Call | Cost at 1080x1920 |
|---|---|---|
| RGB split | `gk.rgb(img, k, px)` | 5 ms |
| Slice displacement | `gk.slices(img, f, k, n=12, amp=0.09)` | 6 ms |
| Macroblocks | `gk.blocks(img, f, k, cover=0.18, tint=accent)` | 12 ms |
| Pixel-sort drips | `gk.sort(img, f, k, thr=150, cols=0.35)` (vectorised, half res) | 40-125 ms (machine-dependent; keep windows short) |
| Sine wave warp | `gk.wave(img, t, k, amp=0.035)` | 30 ms |
| Static | `gk.static(img, f, k)` | 7 ms |
| Tear dashes | `gk.tear(img, f, k)` | 2 ms |
| Block-noise confetti | `gk.noise(img, f, k, colors)` | 7 ms |
| VHS | `gk.vhs(img, f)` | 65 ms |
| Scanlines | `gk.scan(img, 4, 0.2)` | 4 ms |
| X-ray / scan reveal | `gk.xray(img)`, `gk.xray_scan(img, lt, f)` | 37 / 80 ms |
| Thermal | `gk.thermal(img, drift)` | 65 ms |
| Mono + one hue | `gk.mono(img, "#hex")` | 20 ms |
| Psych strobe | `gk.psych(img, f, lf, n)` | 30 ms |
| Type tear | `gk.over(img, TYPE, t, tears=[(t0, frames)])` | 25 ms |

## Measured hit rhythms from the reference edits
- Ref B (24 fps): 1.625 · 1.917 · 2.0 · 2.667 · [3.625 · 3.75 · 3.833 · 3.917] · [5.208 · 5.292] · [9.875 · 10.042]. Burst = 4 changes in 0.29 s, then ≥ 1.3 s calm.
- Ref C (30 fps): [0.267 · 0.3 · 0.433 · 0.6] · 1.967 · [4.733 · 4.8 · 4.9 · 4.967 · 5.067 · 5.133 · 5.233 · 5.3 · 5.4] · 5.8 · 5.9 · 6.067. Invert strobe every 2–3 frames for 0.67 s.
- Ref D (30 fps): clusters of 4–10 hits, intra-cluster gaps 0.07–0.47 s, inter-cluster 0.6–2.6 s; the 12.2–14.3 s cluster repeats at 23.2–25.27 s (11 s phrase loop).
- Ref A and Ref E: no hits; a sustained treatment per shot, swapped every 2.7–3.4 s by a 2 px white line wipe.
