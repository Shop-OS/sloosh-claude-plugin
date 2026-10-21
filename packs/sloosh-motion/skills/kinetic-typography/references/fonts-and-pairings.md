# Fonts and pairings

Six families ship with the sloosh-motion-director skill, all under the SIL Open Font License. Its `new_film.sh` copies every
file into `<film>/fonts/`, with no network. No other family is fetched. Pages declare `@font-face` with `url('/fonts/<file>')`
and list the faces in `KT.boot({fonts: [...]})`, so measuring waits for them.

**Rule zero:** the brand's own font files win. Ask the user for the `.woff2` files and check that their license allows video
use. Copy them into `fonts/`, add an `@font-face`, point `.d` (or `.s`) at it, and add it to `KT.boot` fonts. A static brand
font cannot do `stretch`, `frame`'s width move or `wave`: use slam, stack and echo instead.

## Files and axes

| Family | File | Axes / styles | Used by |
|---|---|---|---|
| Archivo | `archivo-latin-wdth-{normal,italic}.woff2` | wght 100–900, wdth 62–125 | Poster (`.d` caps), Lyric (wdth 62 condensed), Caption (italic, wdth 125), Variable Stretch (`wave`, `stretch`, `frame`) |
| Inter Tight | `inter-tight-latin-wght-{normal,italic}.woff2` | wght 100–900 | Swiss display, List rows, Editorial kickers |
| Instrument Serif | `instrument-serif-latin-400-{normal,italic}.woff2` | 400, italic | Swiss accent word, Lyric breath words, Caption |
| Bodoni Moda | `bodoni-moda-latin-{500,600}-{normal,italic}.woff2` | static 500 and 600, italic | luxury end cards and `rise` mastheads (no slams) |
| Fraunces | `fraunces-latin-full-{normal,italic}.woff2` | opsz 9–144, wght 100–900, SOFT 0–100, WONK 0–1 | Editorial display + italic phrase; the "ink swell" (`wght`, `SOFT`) |
| JetBrains Mono | `jetbrains-mono-latin-wght-normal.woff2` (variable), `jetbrains-mono-latin-500-normal.woff2` (static) | wght 100–800 | Swiss labels and board, List kicker / ticker, Stretch support, Lyric index |

Drive axes with `font-variation-settings` (the engine's `KT.axes`), never with `font-stretch` tweens. Fit text at the axis values
it will END at, or at its widest state (`wave` samples it), so nothing overflows mid-move.

None of the vendored faces has a slant axis. A theme `slnt` value (for example `slnt: -10`) makes `wave` snap each letter with
a short skew on its beats instead. For a true slant, use the Archivo or Inter Tight italic file.

## Pairing rules

1. **One family first.** Get contrast from weight and width (Archivo 900/62 headline vs 700/100 kicker).
2. **Grotesk + mono** for tech and systems: the mono at 0.25–0.35× the headline, caps tracked +0.14 to +0.3 em.
3. **Grotesk or caps + one serif-italic word** for warmth and lyric breath ("Made *really* well."). Nudge the italic up 5–10% so x-heights match.
4. Never two display faces of the same class. Never default system fonts.
5. Display tracking is negative (−0.01 to −0.05 em); small caps labels are positive (+0.12 to +0.3 em). Tracking never animates, except the end card.

## Families by mood (same structure, swap `.d`)

| Mood | Family | Notes |
|---|---|---|
| Neutral premium tech | Inter Tight 800 | −0.04 em |
| Condensed impact | Archivo wdth 62, wght 900 | sport, sale |
| Wide statement | Archivo wdth 125, wght 900 (italic for hype captions) | slams, lockups |
| Width-axis workhorse | Archivo | stretch, frame, wave |
| Editorial serif | Fraunces | `rise`, `swap`, `end`; the ink swell |
| Luxury serif | Bodoni Moda 500 / 600 | no slams; `rise` and `end` only |
| Lyric breath word | Instrument Serif italic | one word per phrase |
| Mono | JetBrains Mono | boards, counters, tickers; tabular figures |

## Size table (px at a 1080 short side; the engine scales by min(W, H) / 1080)

| Role | 9:16 (box 840 wide, 720 below the rail) | 1:1 (box 900) | 16:9 (box 1690) |
|---|---|---|---|
| Hero word, fitted | 220–460 | 180–320 | 220–420 |
| Headline line (2–4 words) | 112–140 | 96–112 | 120–150 |
| Editorial display / masthead | 150–200 / fitted | 140–160 | 190–260 |
| Lyric caps | 200–240 (captions 150) | 160–190 | 180–220 |
| Kicker / label | 30–36 | 28–32 | 28–32 |
| Mono index, board | 34–40 | 30 | 30 |
| Nothing readable under | 28 | 28 | 28 |
