# Feature announcement mode (saas-product-video)

One feature, one idea, 10 to 15 seconds. From the frames alone, the viewer can say: "Now you can ___ in ___." This mode uses the same engine, pages, prompt blocks, Sloosh rounds and spending rules as the walkthrough in SKILL.md, at a faster pace. Read SKILL.md first. This file holds only what differs.

The working film is `examples/feature-announcement-12s/`: tl.py, edit.py, audio.py, ui/feature.html, ui/type.html, ui/toggle.html (the Before/After tile only) and ui/logo.svg. Lay it over a new film folder with `bash scripts/use_example.sh <film> feature --placeholders`.

---

## Style

A keynote bumper for one capability. A realistic pain shot, a NEW pill that pops with a sparkle, a feature name that lands like a slam with a shine bar across it, then the real product doing the one thing, with a click on the beat and a visible change.
- **One feature.** One click (two at most), one transformation. If the brief lists three features, offer three films.
- **Proof is a transformation:** A becomes B (one card becomes three sizes, a draft becomes a finished post, a list becomes a chart), or a before/after toggle over footage.
- **AI only for the camera:** the opener (a person at a laptop, a hand on a phone) and, for the toggle only, the customer's world. No UI, text or logos in any generation.
- **Real UI, rebuilt in HTML** from the user's screenshots or a URL capture. Never an invented feature. Results that are not from the product carry "Example output".
- Hype type (Archivo italic, width 125, weight 900) and one editorial serif line. Measured, auto-fitted, one accent.

**Never in this mode:**
- one clip prompt for the whole film, or any generated text, UI, logo, transition or caption;
- a real brand, product line, famous person or film name in a prompt (describe the look physically);
- a feature list ("and also ..."): one feature per film;
- a flat full-frame screenshot held still, a crossfade between scenes, a click that changes nothing;
- typed (guessed) cursor positions, a different font per line, text over the face or over another line;
- numbers shown as real when they are not verified (label them "Example output" or "Example data");
- emoji, "!!", stock dashboards that have nothing to do with the product.

## Intake

Ask at most 4 questions, as in the director's intake.

| # | Question | Options | Default |
|---|---|---|---|
| 1 | Where it runs, length | square feed post 1:1, portrait feed post 4:5, vertical short video 9:16, web or video site 16:9; 10, 12 or 15 s; "all formats" | **1:1, 12 s**, 30 fps |
| 2 | Look | **A Becomes B** (default), **Before/After Toggle** (a feature that changes media), **Keynote Hype** (dark, harder, techno), **Changelog Loop** (8 s, code only, a seamless loop), **Code Only** (no generations), "match my reference" | A Becomes B |
| 3 | Inputs | 2 or 3 screenshots (the screen before, the feature's control, the result) or a URL; a logo; a brand colour; the opener person: "me" (a face photo and consent: "Is this you, or someone who agreed?") or a fictional person | a fictional person |
| 4 | Words and sound | Copy: "write it", or the feature name, the benefit and the CTA. Sound: original techno score (default), score and voice-over, or the user's own track | write it; score |

**Copy to write:** the pain as one hype stack ("ONE POST." / "NINE SIZES."); NEW, the feature name (1 to 3 words) and a benefit line of 4 to 8 words ("Every channel size, in one click."); the real UI labels; the payoff stack ("EVERY" / "CHANNEL."); the end card (product, "<Feature> is live.", CTA, URL).

**Treatment (the one screen the user approves; the example film):**
```
FEATURE DROP · Example Studio "Auto-Resize" · 12 s · 1:1 1080 · 30 fps · techno 120 BPM, original score
0.0  AI    desk, a founder leans into the laptop glow      ONE POST. / NINE SIZES.
0.8  AI    phone, a thumb taps                             (same lockup)
1.3  AI    push into the screen -> white
2.0  code  NEW · AUTO-RESIZE · "Every channel size, in one click."
4.0  DROP  the real editor springs in; click Auto-Resize; click All channels
6.1  code  one post becomes 1:1, 9:16 and 16:9, a check on each
8.5  AI    phone / desk / phone, every beat effect on      EVERY / CHANNEL.
10.0 code  end card: Example Studio · Auto-Resize is live. · [Try it free] · example.com
Type: Archivo italic hype stacks, Instrument Serif benefit line, brand accent #FF6A3D.
Sound: filtered intro, riser, breath, drop on the window, low-passed under the UI, wide open on the payoff;
       a click per click, pops on the menu and the checks, a sparkle on NEW and on A -> B.
Generations: 2 stills, then 2 clips, each round with its own quote.
```
The treatment itself is free. Each round of generations gets its own quote and approval later (SKILL.md, section 4).

## Timeline

Default: 12 s at 120 BPM (one beat = 0.5 s), techno in A minor. Full file: `examples/feature-announcement-12s/tl.py`.
```python
W, H, FPS = 1080, 1080, 30; BPM = 120.0; B = 60.0 / BPM; GENRE, KEY = "techno", "Am"
T_RUSH = 2.5 * B; T_NAME = 4 * B              # 1.25 rush into the screen, 2.0 NEW pill + name (page time 0)
DROP = 8 * B; T_BREATH = DROP - 3 / FPS       # 4.0 the window springs in
T_PAY = DROP + 9 * B; T_END = DROP + 12 * B   # 8.5 payoff, 10.0 end card
LEN = T_END + 4 * B                           # 12.0
FEAT_NAT = T_PAY - T_NAME                     # 6.5: feature.html is rendered at exactly this length
def p2t(p): return T_NAME + p                 # page time -> film time (for the SFX)
FEAT_CUES = {"click": [3.0, 4.0], "pop": [0.15, 3.05, 5.0, 5.25, 5.5], "sparkle": [0.15, 4.1],
             "whoosh": [1.8, 4.08], "shine": 0.8}          # page time; the clicks sit on beats (film 5.0, 6.0)
TYPE = {"lockA_1": [0.15, 1.15], "lockA_2": [T_PAY + 0.1, T_END - 0.2], "end": [T_END, LEN]}
END_CLICK = T_END + 1.2
HITS = [(T_PAY, "negative", 2), (T_PAY + 2 * B, "red", 2)]
```

| Time | Beat | Source | Move | Type | SFX |
|---|---|---|---|---|---|
| 0.00-0.75 | Pain | AI desk clip (0.4-1.15) | push 1.00 to 1.06 | A "ONE POST. / NINE SIZES." | whoosh |
| 0.75-1.25 | Pain | AI phone clip (1.1-1.6) | 1.10 to 1.00 | (same lockup) | whoosh |
| 1.25-2.00 | Rush | AI desk clip (1.8-2.55) | zoom 1.1 to 1.9 into the screen, zoom blur, white | none | riser, impact |
| 2.00-3.90 | NEW and name | feature.html 0-1.9 | pill pops with a sparkle; the name slams 1.3 to 1 with blur; shine bar; benefit words blur in; exit up | NEW pill, name, serif benefit | pop, sparkle, swish, ticks |
| 3.90-4.00 | Breath | black | 3 frames | none | silence |
| 4.00-8.50 | **DROP: the feature** | feature.html 2.0-6.5 at 2x | the window springs in; macro on the feature chip; click (5.0); the menu pops; click the option (6.0); A becomes B; checks pop; slow push | UI labels | clicks, pops, sparkle; music low-passed |
| 8.50-10.0 | Payoff | 3 AI windows | inverted frame, punch, beat punches, red frame, zoom blur, whiteout | A "EVERY / CHANNEL." | impact, glitch, shutter |
| 10.0-12.0 | End card | brand dark | logo pops, wordmark tracks in, CTA rises, the cursor clicks it (11.2) | D End Card | sparkle, click |

**10 s:** drop the payoff (T_PAY = T_END = 8.0); a 2 s end card. **15 s:** T_PAY 9.5 (one more UI beat: a second example of the same feature), a 2 s payoff, a 3.5 s end card (LEN 15.0).
```python
# 10 s: no payoff section
T_PAY = T_END = DROP + 8 * B; LEN = T_END + 4 * B             # 8.0 / 10.0; FEAT_NAT = 6.0 (shorten the hold)
# 15 s: a second example of the same feature, a 2 s payoff, a 3.5 s end card
T_PAY = DROP + 11 * B; T_END = T_PAY + 4 * B; LEN = T_END + 7 * B   # 9.5 / 11.5 / 15.0
```
Keep the clicks on beats when you retime. FEAT_CUES are page time: page 3.0 = film 5.0 = a beat.

**All formats:** the pages lay themselves out from the W and H in tl.json. Change `W, H` (1080x1920, 1920x1080 or 1080x1350), render again, make the sheets again. Nothing is cropped.

| Format | Name card | Window | A becomes B | Lockups |
|---|---|---|---|---|
| 1:1 1080x1080 | centred, name 140 px | 900x820, centred | one row of three | A 96/136 at x 72, bottom 84 |
| 9:16 1080x1920 | centred at 42% height, name 150 px | 940x1180 at 46% height | the widest result on top, two below | A 118/168 at x 120, bottom at y 1260 |
| 4:5 1080x1350 | centred at 42% height, name 150 px | 940x1053 at 46% height | the widest result on top, two below | A 118/168 at x 120, bottom 96 |
| 16:9 1920x1080 | centred, name 168 px | 1400x840, centred | one row of three | A 118/168 at x 104, bottom 96 |

## Shots

Two AI shots by default: desk and phone. The Before/After tile adds the world shot. Use the prompt blocks in SKILL.md, section 3, with these changes:
- **desk:** "space low-left for type" instead of "room on the right for type".
- **phone:** the same edit of the approved desk still.
- **world** (Before/After only): the media the feature changes. For example the user's real product on a wet kerb at dusk, or the customer's own photo before a relight.

Clips: start frame = the approved still, aspect ratio = the film's, about 5 s, no generated audio, one action and one move:
- c1 desk: "leans in toward the screen, the screen light brightens on the face; slow push-in".
- c2 phone: "taps twice, the phone tilts slightly toward the camera; static macro, tiny handheld drift".
- c3 world: "a soft light sweep travels across the product; slow push-in, 3%".
Add the person or product block from SKILL.md and the closing sentence "One continuous shot with no cuts, text, extra people or new objects."

**Counts:** 2 stills and 2 clips (Before/After: 3 and 3). **Code Only and Changelog Loop:** no generations. The hook becomes the name card on the gradient, with the pain lockup typed in.

The opener windows are short (0.5 to 0.75 s). Pick the cleanest, most decisive moment of each clip: the lean, the tap. After each clip, run `python3 lib/sheets.py clip clips/c1.mp4` and write the clean windows (in the first 60 to 70%) into SHOTS as in-points.

Review each still at full size with the review list in SKILL.md, section 4. For the world shot, also reject any changed product part, shape, colour or label.

## Edit

Default SHOTS (10 rows, 9 cuts; no AI window over 0.75 s):
```python
(0.00, 0.75, "clips/c1.mp4", 0.40, 1.0, 1.00, 1.06, .45, .45, ""),            # desk (lockup A)
(0.75, T_RUSH, "clips/c2.mp4", 1.10, 1.0, 1.10, 1.00, .55, .50, ""),          # phone
(T_RUSH, T_NAME, "clips/c1.mp4", 1.80, 1.0, 1.10, 1.90, .56, .40, "rush"),     # into the screen -> white
(T_NAME, T_BREATH, "black", ..., "page:feat"), (T_BREATH, DROP, "black", ..., "hard"),
(DROP, T_PAY, "black", ..., "page:feat"),                                     # the feature
(T_PAY, T_PAY+B, "clips/c2.mp4", 2.40, 1.0, 1.14, 1.00, .55, .5, "punch shake"),
(T_PAY+B, T_PAY+2B, "clips/c1.mp4", 2.90, 1.0, 1.00, 1.08, .45, .45, "ramp"),
(T_PAY+2B, T_END, "clips/c2.mp4", 0.30, 1.0, 1.00, 1.10, .55, .5, "zblur whiteout"),
(T_END, LEN, "#0B0B0F", ..., "card"),
```
render(t): cuts, then `saaskit.rush`, then the page (`fk.Overlay("frames/feature", start=T_NAME)` with the zoom from `saaskit.punch_in(t, DROP)`), then the type, then `fk.hits`, then `saaskit.whip_at` at T_PAY, then the finish (footage: contrast, vignette, bloom, grain 6; page and card: grain 2.5), then the flash. `CutList(beats=BEATS, fx_from=T_PAY, fx_to=T_END)` turns the beat punch and downbeat split on only in the payoff.

**Budget (12 s):** 1 rush, 1 breath, 1 drop punch, 1 whip, 2 hits, 1 whiteout. Nothing touches the UI except the punch, the whip and the grain.

| Move | What you see | How |
|---|---|---|
| Rush into the screen | the push into the laptop streaks and burns white | row zoom 1.1 to 1.9 and `saaskit.rush` |
| Breath, then drop | 3 black frames, then the window springs in on the downbeat | a `hard` black row; the flash; `saaskit.punch_in(t, DROP, 0.06)` on the 2x frames |
| Whip into the payoff | the UI streaks out, the footage slams in inverted | `saaskit.whip_at` at T_PAY and a negative hit at T_PAY |
| Payoff | 3 cuts in 3 beats, a punch per beat, a split on downbeats, a red frame, a burn to white | tags and the CutList beat effects |
| Other formats | the same film at 9:16, 16:9 or 4:5 | the pages lay out again from W and H; for a page that exists only at 16:9, use `saaskit.Reframe` |

**Before/After Toggle tile in code** (the media the feature changes; ui/toggle.html was tested at 1:1, 4:5, 9:16 and 16:9):
```python
# tl.py
T_TOG = T_PAY - 2 * B; T_CLICK = T_PAY                         # BEFORE for 2 beats; the click opens the payoff
COPY["toggle"] = ["OFF", "STUDIO", "LIGHT"]; HITS = [(T_CLICK, "negative", 2), (T_CLICK + 2 * B, "red", 2)]
# edit.py: the page row ends at T_TOG, then
(tl.T_TOG, tl.T_CLICK, "clips/c3.mp4", 0.50, 1.0, 1.00, 1.03, .5, .55, "flat hard"),   # BEFORE, deliberately flat
(tl.T_CLICK, tl.T_CLICK + B, "clips/c3.mp4", 1.50, 1.0, 1.16, 1.00, .5, .55, "punch shake leak"),  # same moment, ON
_L["TOG"] = fk.Overlay("frames/toggle", start=tl.T_TOG)       # inside layers(); in render(t): img = L["TOG"].over(img, t) before the type
# filmkit applies the "flat" tag once inside cuts.render(t); add nothing in render(t)
# render: python3 lib/render_html.py ui/toggle.html --dur <T_END - T_TOG> --jobs 1 --out frames/toggle
# audio.py: music = ak.lowpass_region(music, tl.T_TOG, tl.T_CLICK, 500, 0.45); click + impact + sparkle on T_CLICK
```
Use it when "before" and "after" show in footage: relight, upscale, background swap, colour grade, cleanup. The click is on a beat, the footage switches on that exact frame, and the toggle shrinks to a bottom-left badge.

## Type

Archivo italic, width 125, weight 900 (hype); Inter Tight 600-800 (UI, pill, end card); Instrument Serif italic (the benefit line, the end-card line). White and the brand accent (and its lighter gradient end); ink #1A1714 on the light name card. ui/type.html is the same page as in the walkthrough; ui/feature.html sets the name card. new_film.sh copies the fonts into fonts/.

| Lockup | 1:1 (1080) | 9:16 (1080 wide) | 16:9 (1920) | In / out | Placement |
|---|---|---|---|---|---|
| **A Hype Stack** | 96 / 136 px | 118 / 168 | 118 / 168 | mask wipe left to right 0.16 s and a 44 px slide; out to the right in 0.2 s | bottom-left: x 72 / 120 / 104; bottom 84 / y 1260 / 96 |
| **N Name Card** | pill 28 px caps 0.2 em; name 140 px; serif benefit 54 px | 30 / 150 / 58 | 30 / 168 / 64 | the pill pops (back 2.2) with 8 sparks; the name 1.3 to 1 with blur 12 to 0 in 0.32 s; shine bar 0.45 s; benefit words blur in 0.09 s apart; exit up 120 px with blur | centred (9:16 at 42% height), auto-fit to the safe width |
| **C Slam** (Keynote Hype) | 190 px | 200 | 240 | 1.35 to 1, blur 12 to 0 in 4 frames | centred at 40% |
| **D End Card** | logo 104, wordmark 88, serif line 46, CTA 36, URL 24 | 112 / 96 / 52 / 40 / 26 | 120 / 104 / 54 / 38 / 26 | the logo pops, the wordmark tracks 0.30 to -0.02 em, the line blurs in, the CTA rises, the cursor clicks on END_CLICK | centred column |

4:5 uses the 9:16 sizes, with the hype stack 96 px above the bottom. Measure every position after the fonts load. Auto-fit anything wider than the safe zone. HITS hit the type too. With VO, a line lands on each lockup.

## Feature page

ui/feature.html is opaque. Page time 0 = T_NAME. Render it with `--dur 6.5 --scale 2`. It lays itself out for 1:1, 4:5, 9:16 and 16:9. Replace its CONFIG block and window markup with the real product.

| Page time | Scene | Choreography |
|---|---|---|
| 0.00-1.90 | Name card | brand-tint gradient blobs drift; the NEW pill pops (0.15) with 8 accent sparks; the name lands (0.30-0.62); shine bar (0.8); benefit words blur in (0.9 + 0.09 i); everything exits up with blur (1.72-1.90) |
| 2.00-2.90 | Window | springs from rx 26°, ry -24°, y +300, scale 0.8 (spring 0.6, 11); settles flat by 3.2 |
| 2.45-3.50 | The control | the camera dives to the feature chip (1.75x); the cursor moves from off-frame to the MEASURED chip; click at 3.0 (the chip squashes, accent border); the menu pops (back 1.8); the camera frames the menu |
| 3.45-4.50 | The option | the cursor moves to the MEASURED target option; hover tint; click at 4.0; the menu closes |
| 4.05-5.60 | A becomes B | three copies of the 4:5 post morph (quartic, 0.12 s apart) to 1:1, 9:16 and 16:9 and spread into a row; an accent ring and a check label pop on each (5.0, 5.25, 5.5); the camera pulls back |
| 5.60-6.50 | Hold | slow push 1.0 to 1.07 |

**Rebuild the feature's UI** (full procedure in `references/ui-rebuild.md`):
1. Get the screens: the user's screenshots, or a capture of the URL the user gave (1440x900 at 2x). Logged-in apps need the user's screenshots. Ask once.
2. Anonymise: one fictional person and company. Remove badges and banners. Never add an element the product does not have.
3. Sample the tokens (background, surface, ink, muted, accent, radius, font) into the page's CSS. Set tl.ACCENT to the accent.
4. Rebuild only what the film shows: the window chrome, the toolbar with the feature's control, the work area or list the feature acts on, the menu or dialog it opens, the result. Use the 2x screenshot as an image only for dense areas that never move or zoom.
5. Compare one rendered frame with the screenshot side by side. It must be recognisable at first glance. If not, fix it.

**CONFIG fields** (top of feature.html): chip (the label of the feature's control), menu (its real options), target (the index of the option clicked), sizes and aspects (the results), image (the user's real asset or an approved still). The window chrome, toolbar chips and rail come from the screenshots. Keep their radii, weights and colours.

**A becomes B, by feature type** (one object, one transformation, a check on each result):

| Feature | A | B | Proof detail |
|---|---|---|---|
| Resize, reformat | one 4:5 post | 1:1, 9:16 and 16:9 | each card morphs from A's box, with a label and a check |
| Generate, AI write | an empty card with the typed prompt | the finished card (image and caption) | gradient letters type in, then a shimmer turns solid |
| Summarise, report | a long list of rows | a 3-bullet summary card or a chart | the rows collapse into the card; numbers count up (Example data) |
| Schedule, publish | a draft card | a calendar slot with a "Scheduled" pill | the card flies into the slot and lands as a thumbnail |
| Integrate, sync | a Connect button | "Connected" with a check, and items flowing in | squash, sparkle, check (the walkthrough's connect move) |
| Batch, bulk | one item | a grid of 12 | the cascade of tiles |

Rules: the camera is one {px, py, s, ax, ay} state per frame, measured at identity, then set. Every cursor leg goes between MEASURED boxes after the camera. The clicked element squashes with the cursor. Click, pop and sparkle times come from FEAT_CUES, so audio.py lands each sound on its frame. For another A to B, keep the structure and swap the objects.

ui/type.html is transparent; render it with `--dur LEN`. ui/toggle.html is for the Before/After tile only.

## Sound

`ak.score("techno", 120, LEN, DROP, "Am")`: a filtered intro under the pain and the name card, a riser into the white, the breath, the drop on the window, the groove low-passed at 1.4 kHz and 60% under the UI so the two clicks read, a 2-frame gap, then wide open on the payoff, and a tail on the end card. A lighter, clean feel: house at 118. Keynote Hype: techno at 128 with slams. With the user's own track, its drop lands on tl.DROP (the director's sound section).

| Cue | SFX | Gain (dB) |
|---|---|---|
| hook cuts | whoosh(0.3) | -18 |
| rush, white | riser, impact(1.0) | -10, -16 |
| NEW pill | pop and sparkle | -12, -11 |
| shine bar, benefit words | whoosh(0.4, up=False), a tick per word | -20, -21 |
| feature clicks (FEAT_CUES click times through p2t) | click | -8 |
| the menu, each check | pop | -12 |
| A becomes B | sparkle and whoosh | -11, -16 |
| payoff | riser(2B) into it, impact, glitch_sfx on the negative, shutter on the red | -12, -6, -13 |
| lockups, end card, CTA | shutter, sparkle, click | -12, -12, -9 |

VO is optional: "One post. Nine sizes." / "New. Auto-Resize." / "Try it free." (normal), with the music ducked to 45%. It needs a text-to-speech engine that is already on the user's computer, or one the user agrees to install. Otherwise skip the VO or use the user's own recorded lines.

| Section | Music | Why |
|---|---|---|
| 0-2.0 hook and rush | the score's intro (filtered, sub drone, sparse kick), a riser into the white | tension, the pain |
| 2.0-3.9 name card | the same filtered bed, a snare roll into the breath | anticipation |
| 3.9-4.0 breath | silence (ak.gap) | makes the drop land |
| 4.0-8.5 the feature | the full groove low-passed at 1.4 kHz, 60% | the clicks and pops read |
| 8.5-10.0 payoff | wide open after a 2-frame gap, an impact on the first frame | the result feels big |
| 10.0-12.0 end card | the groove, an end impact and the tail | resolve |

## Build steps

1. Intake, then the treatment above: the beat table, 2 AI stills and clips, 2 pages, the exact lines and the sound plan. One approval. The treatment is free.
2. `bash <director>/scripts/new_film.sh <brand>_feature 1x1 30`, then `bash <saas>/scripts/use_example.sh <brand>_feature feature --placeholders`.
3. Run the stills rounds (SKILL.md, section 4). While they run: get the screens (capture or collect, anonymise, tokens), set the COPY in tl.py, the CONFIG and window markup in feature.html, and ui/logo.svg.
4. Fast page check: `python3 lib/render_html.py ui/feature.html --dur 6.5 --fps 4 --jobs 1 --out frames/feature_dbg`. Tile the PNGs, look, fix.
5. Approve the stills, run the clips round, run sheets.py clip, and write the clean windows into SHOTS.
6. Render: type.html with `--dur 12`, feature.html with `--dur 6.5 --scale 2` (use `--jobs 1` on a shared machine).
7. `python3 edit.py out/sheet.jpg 0.3,0.9,1.6,2.4,3.0,4.1,4.8,5.05,5.6,6.05,7.3,8.2,8.6,9.2,10.6,11.25`. Look at the sheet. Fix.
8. `python3 audio.py` (read the RMS report), `python3 edit.py`, `python3 lib/sheets.py film out/<name>_v1.mp4 3.5 9 --fps 6`, then `python3 audio.py out/<name>_v1.mp4`. Deliver as in the director's delivery section.
9. **Other formats** (one folder per format, so each stays exact): run new_film.sh for `<brand>_feature_9x16 9x16 30`. Copy tl.py, edit.py, audio.py, ui/ and the approved plates/ and clips/ over it. Set `W, H` in tl.py to the folder's size. Render type.html and feature.html again and make the sheets at the same times. Fix anything that crowds the 9:16 safe zone (top 240, bottom 660, sides 120). For 4:5, use `4x5` and keep 96 px clear at the top and bottom. AI stills for each format are made at that aspect, never cropped from 1:1: edit the approved 1:1 still to the new aspect with "keep everything, extend the frame". That is a new round with its own quote and approval.

## QA

- [ ] One-sentence test from the frames: "Now you can ___ in ___."
- [ ] The feature name is readable by 2.6 s, the real UI is on screen by 4.1 s, the transformation is complete by 7.6 s.
- [ ] The feature, its control and its labels exist in the product. Results that are not from the product carry "Example output".
- [ ] The cursor tip is on the chip at 5.0 and on the option at 6.0 (check those frames). The target squashes. The change follows within 0.1 s.
- [ ] No text over text (name and benefit, lockup and face, end card and cursor). Every line is inside the safe zone in every delivered format.
- [ ] No generated frame shows UI, text, logos or a readable screen. The person, room and light match across the two shots.
- [ ] A breath before the drop; clicks on beats; payoff cuts on beats; -14 LUFS.

| Looks AI-ish or cheap | Concrete fix |
|---|---|
| The opener looks generated (plastic skin, rim glow) | Make the still again with the camera and lens line, underexposure, pores, the screen as the key light. Use 0.5 to 0.75 s windows |
| A generated screen shows fake UI | The screen faces away or is a plain glow. Never ask for screen content |
| The name card looks like a template | The hype face at full size, the pill in the brand gradient, a real shine bar and sparks, the serif benefit line |
| The feature does not read | One control, one click on the beat, a macro on the control, then a pull-back to show the whole result |
| A to B looks like a slideshow | Morph from the same box (FLIP style), stagger 0.12 s, a check pop on each result |
| Too much happens | Cut to one click. Hold the result 0.9 s. At most 3 payoff cuts |
| The menu hides behind the work area | Give the menu wrapper its own z-index above the cards (the example page does) |
| 9:16 results are too small | Use the stacked 9:16 layout (the widest result on top, two below) and 24 px labels |
| The end-card cursor lands off the button | It is measured from the button each frame. If it misses, the button moved after the measure: measure after K.set |

## Tiles

| Tile | One line | Changes from the default |
|---|---|---|
| **A Becomes B** | one object turns into the result inside the real UI | default |
| **Before/After Toggle** | the feature changes media: OFF over flat footage, a click on the beat, ON in full grade | 3 AI shots (adds world); the toggle code in the Edit section above; render ui/toggle.html with `--dur T_END-T_TOG`; overlay `fk.Overlay("frames/toggle", start=tl.T_TOG)` before the type; the flat look is filmkit's `flat` tag; the music is low-passed at 500 Hz, 45% from T_TOG to T_CLICK |
| **Keynote Hype** | black, harder, techno 128, more cuts | a dark name card (#0B0B0F, white name, accent pill); slams on the payoff beats; 5 payoff cuts; a `duo` hit; denser SFX |
| **Changelog Loop** | 8 s, code only, seamless | no AI rows; the page runs 0-8 s and its last 0.5 s eases every element back to frame 0 (check position and speed at the seam); a small logo in a corner, no end card |
| **Code Only** | no generations | the hook is the name card itself (0-2 s) with lockup A typed over the gradient |

**Keynote Hype recipe:** GENRE = "techno", BPM = 128. The name card on #0B0B0F with a white name and an accent pill. `TYPE["slams"] = [T_PAY + B, T_PAY + 2 * B, T_PAY + 3 * B]` with three words. The payoff becomes 5 rows of one beat each (tags punch shake, ramp, duo, zblur, whiteout). HITS adds `(T_PAY + 3 * B, "duo", 2)`. An impact(0.9) on every slam. A "shout" VO line on each slam if VO is on.

**Changelog Loop recipe:** no AI rows; LEN = 8.0. The page is the whole film (page:feat from 0 to LEN, no breath). The A to B happens at 3.0 and holds to 6.5. From 6.5 to 8.0 every element eases back to its frame-0 state with the same easing reversed. Render frame LEN and frame 0 and compare them: they must match, and nothing may still move at the seam. Put the score's drop at 0, so the loop point is a bar line. A small logo top-left, no end card.

## Template card

- **Name:** Feature Drop. **Promise:** one new feature, announced like a keynote in 12 seconds.
- **Required:** the feature name and a one-line benefit; 2 or 3 screenshots or a URL. **Optional:** logo, brand colour, CTA and URL, the user's face photo (with consent), a clip of the media the feature changes, the user's own track.
- **Defaults:** 12 s, 1:1 1080x1080, 30 fps, A Becomes B, techno 120 BPM, original score and SFX.
- **Generations:** 2 stills and 2 clips (Before/After: 3 and 3; Code Only and Changelog Loop: none). The quote of each round decides the price.
- **Tiles:** A Becomes B, Before/After Toggle, Keynote Hype, Changelog Loop, Code Only.
