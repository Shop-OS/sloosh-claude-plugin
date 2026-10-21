# Moves reference (lib/ktkit.js)

Every scene in `tl.py` is `S(id, move, in, out, beats, **options)`. Its words come from `COPY[id]`, a list of strings: lines, words or
items, depending on the move. Sizes are px at a 1080 short side, and the engine scales them for other formats. Times are film seconds.
Each `render(t)` is pure.

**Common options:**
- `size`, `max`: the start size and the fit cap.
- `y`: placement in the box, 0 top to 1 bottom.
- `box=[l, top, r, bot]`: fractions of the frame; the default is the format's safe zone. `noRail`: skip the vertical-feed rail rule for decorative or top bands.
- `align` (`center` | `left`); `accent=[i]` / `outline=[i]`: line or word indices; `axes={"wght":900,"wdth":100}`.
- `inv` (see each move); `exit` (`wipe` | `up` | `squeeze` | `cut`); `kicker`: a small tracked line above.
- `z`: the stacking order; `pre` / `post`: the visibility margins, default 0.12 / 0.45 s.

**Copy markup** (word level): `*word*` is the serif-italic accent face (`.it`), `^word^` the accent colour, `_word_` an outline.

**Timing law:** the next scene lands at least 0.25 s after the previous `out` (exits take 0.2–0.25 s), unless that exit is `cut`.

| Move | COPY | Options (defaults) | Numbers | Don't use when |
|---|---|---|---|---|
| `stack` | lines | `beats` one per line; `fill` (True: every line spans the box) / `fillW` 1; `lead` −0.02 em; `enter` rise / `wipe`; `inv=[(t, line, word or -1, dur 0.15)]`; `flash=[hex,…]` (4-frame landing colours); `push` 0.025; `drift` 10 | rise 0.4 s quartic out, starts 0.07 s before the beat; wipe 0.16 s plus a 44 px slide | > 4 lines on 9:16; > 10 characters per line (break the line) |
| `slam` | words | `inv=[i]` lands word i inverted for `invDur` 0.2 s; `fillW` 1; `max` 460 | 1.35 → 1 and blur 12 → 0 in 0.13 s, then a 2% overshoot | serif / luxury briefs; more than 6 in a row without a hold |
| `stretch` | lines | `w0` / `w1` (theme `wdth`), `g0` / `g1` 900, `dur` 0.9, `lead` 0.07 em | fitted at w1; wdth eases quartic out; exit squeezes in 0.25 s | static fonts (never fake it with scaleX) |
| `frame` | [word] | `w0` / `w1`, `wght` 900, `margin` 48, `top` / `bot` (default: the safe band), `dur` 0.55 | scaleY = band ÷ measured cap height | words over 6 letters (too thin); more than once per film |
| `echo` | [small, hero] | `n` 3 copies, `gap` 0.66 cap, `dir` 1 (down) / −1, `walk` k extra beats (the fill walks down), `y` 0.3 | hero 1.25 → 1 in 0.35 s; copies stagger 60 ms | the hero word is longer than 8 characters |
| `flap` | [text, label?] | `roll` 0.45, `step` 0.05, `rate` 2 frames, `size` 150, `kicker` | lock_i = in + roll + i × step; tiles 0.8 em | long sentences (≤ 14 characters); serif presets |
| `count` | [value like "40%" / "1,299", label?] | `dur` 0.9, `start` 0, `fillW` 0.92, `max` 520, `kicker` | true odometer carry; vertical blur capped at 18 px | numbers the user did not give |
| `list` | [stem, item…, payoff] | `beats` one per item (the last is the payoff landing), `band` 0.47, `size` 132, `stemSize` 96, `stemFont` `d`/`s`, `bar` 14, `lastDur` 0.75 | first step 0.6 s out, the others 0.36 s in-out, the last 0.75 s out; rows dim by distance | > 8 items; items wider than the box (they are fitted down) |
| `grid` | [word] | `rows` 9, `cols` 3, `full` True (whole frame), `hero` (cell index, default centre), `origin`, `lag` 0.035, `hold` 0.1, `checker` True, `font` | cells enter by distance; waves on `beats`; the hero grows after the others leave | the word must be read (it is texture) |
| `ticker` | [text] | `y` 0.74 on 9:16 and 0.885 on other formats, `size` 64, `speed` 140 px/s, `dir`, `gaps=[(a, b)]`, `font` | x = −speed × t mod the measured unit | Swiss / editorial calm (keep it mono and small there) |
| `zoom` | [word] | `letter` (index; auto finds O 0 Q D B P 9 6 A 8 R), `dur` 0.55–1.0, `S` 40, `hole` [0.2, 0.3] (fractions of the letter box) | the counter is put at frame centre; scale e^(ln S × u^2.4); add a `cut` field row at `out − dur` | words without a counter letter; twice per film |
| `lyric` | rows with markup | `beats` one per word, in reading order; `size` 200 (caps; serif `serif` × 1.0 em); `inv=[word index]`, `invDur` 0.18; `lead` 0.02 em; `slamFrom` 1.35 | caps slam in 0.2 s; serif rise in 0.42 s; the phrase hard-cuts at `out` | more than 3 words per row on 9:16 |
| `lockA` | [line 1, line 2] | none (the director kit numbers) | `K.lockupA`: 0.16 s wipe, 0.07 s line lag, 0.2 s out | centred over a subject |
| `rise` | lines (with `*italic*`) | `stagger` 0.06, `swing` 3°, `dur` 0.9, `fill`, `strike=[(line, word, t)]`, `marker=[(line, word, t)]` (colour `--mark`), `swell=[(line, word, t, from_axes, to_axes, dur)]`, `inv`, `flash` | words share one size (the widest line fits the box); `fill` is capped to the box height; a `swell` widens its word and reflows the rest of the line: swell the last word of a line, or leave room | dark editorial over busy footage (use the shadow + plate `dim`) |
| `swap` | [old line, new line] | `beats=[old lands, swap]`, `size` 150, `accentNew`, `flash` (hex) | old word k leaves in 0.22 s; new word k rises 0.24 s later | the new line is > 1.4× wider than the old one |
| `wave` | [word] | `ax={"wght":[200,900],"wdth":[125,62]}` (Archivo ranges), `freq` 0.7, `spread` 0.75, `beats` (skew snaps when the theme has `slnt`), `snapT` 0.14 | fitted to the widest sampled state | static fonts |
| `end` | [title, sub?] | `size` 96, `track=[0.62, 0.40]`, `dur` 1.2, `rule` 140, `font` `d`/`s`, `y` 0.45 | fitted at the final tracking | titles over 18 characters (tracking gets too wide) |

## Craft rules (they hold for every move)

- **Easing:** entrances decelerate (quartic or quintic out, 0.35–0.9 s); exits accelerate (cubic in, about 60% of the entrance); moves between positions use in-out. No bounce or elastic. The only overshoot is the slam's 2%.
- **Landing frames sit ON the beat.** Masked entrances start 0.07 s early, because a quartic out covers most of its travel in the first fifth.
- **Stagger budgets:** 15–35 ms per character (≤ 0.5 s per word); 60–120 ms per word as a flourish; 0.25–0.4 s per word when synced to speech.
- **Rhythm:** after 3–4 identical hits, change something: a hold, a scale, a field or a layout.
- **Every hold moves:** a push of 2–2.5%, a counter-drift, a ticker or an axis breath. Only the final 0.5 s is frozen.
- **Character-level motion** (flap, wave, track) is for tech, playful or brand-sign moments; statements animate as words or lines.
- **Measure, never guess:** the engine fits with Range widths after `document.fonts.load`. If you add a custom element, measure it the same way (`KT.textW`, `KT.ink`, `getBoundingClientRect`) before positioning anything.
