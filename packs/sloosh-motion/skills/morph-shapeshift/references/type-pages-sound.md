# Type, pages and sound

Read this with SKILL.md when you set the copy, build or change a `ui/*.html` page, or write `audio.py`.

## 1. Type system

One family carries every word that sells: **Archivo variable, italic, width 125, weight 900**. Counters use
**Inter Tight 700**; spaced lines use Inter Tight 600. Both fonts come with the director scaffold in `fonts/`.
Use white `#FFFFFF` and ONE accent (default yellow `#F6C945`, or a colour sampled from the logo). Use red `#E5262A`
only for the end-card rules. Measure every element after `document.fonts.load` and fit it to the safe zone
(9:16: top 240, bottom 660, sides 120; 16:9: sides 104, top 86, bottom 96; 1:1 and 4:5: sides 96, top 86,
bottom 110; all at a short side of 1080). 1:1 and 4:5 use the 9:16 sizes. The ECHO never climbs above the chin line.
Apply every whole-frame hit after the type, so it strikes the words too.

| Lockup | 9:16 (1080 wide) | 16:9 (1920 wide) | In and out | Placement |
|---|---|---|---|---|
| FORM (state tag) | counter 26 px +0.24em accent; word 112 px white | 24 px; 104 px | the word rolls up in a masked slot over 0.32 s (expo-out) on the key landing, and out 0.16 s upward before the next | `bl`: bottom-left of the safe zone (photoreal); `under`: centred at 62% (9:16), 64% (4:5), 70% (1:1) or 77% (16:9) of H (code) |
| STACK (lockup A) | 118 px white / 168 px accent, tucked -0.13em | 104 / 150 px | `K.lockupA`: mask wipe 0.16 s + 44 px slide; out to the right in 0.2 s | bottom-left of the safe zone |
| ECHO (lockup B) | hero 260 px accent, 2-3 outlined copies, small word 44 px | 300 px, small 40 px | `K.echo`: lands 1.25 to 1.0, the ghosts cascade | `ECHO_POS.bottom` = the hero baseline: 0.56 H on faces (the torso), 0.42 H elsewhere |
| END | traced logo 560 px wide, title 92 px, line 26 px +0.32em | logo 640 px, title 96 px, line 24 px | the logo comes in 1.12 to 1 from blur; the title slams; red rules grow from the centre; the line rises | logo centred at 44% H; or `END_LOGO = False` and a text block at `END_Y` under a logo the morph page landed |

Copy rules: one word per form (ORIGINAL, WIREFRAME, REPTILE, X-RAY; TAP., LOAD., PLAY.), stacks of at most 2 x 2
words, words in capitals. `ui/type.html` (the same in both examples) reads TYPE, COPY, TYPE_POS, ECHO_POS,
FORM_LABEL, END_LOGO and END_Y from tl.json. It never needs hand-edited times.

The eye line at 26% and the torso in the middle of the keys are deliberate. The FORM tag and the STACK sit
bottom-left and the ECHO sits on the torso, so no word ever covers the face.

## 2. Code pages

Every page defines `window.render(t)`, pure in t: no CSS animation, no timers, no animation timelines. Load order:
`/lib/kit.js`, `/vendor/flubber.min.js`, `/lib/morphkit.js`. `render_html.py` serves the film folder, so these
paths and `/fonts/...` and `/ui/logo.json` resolve inside the film. Times come from tl.json.

| Page | Contents | `render(t)` choreography |
|---|---|---|
| `ui/morph.html` (12 s) | dot grid, the shape (with a drop shadow), six content groups, a typed prompt + send button, cursor, 3 rings, tile icon, full logo | `MK.chain` over 9 box keys; a handoff per state; micro-actions; typing with an accent tail; a measured cursor; rings; colour lag to the dark tile; the eyes pop, glance and blink; the wordmark reveal and centring slide |
| `ui/liquid.html` (9 s) | paper radial, 4 goo circles, crisp letter paths, layered logo | pour 0.1-0.9, split 1.5-2.7, orbit 2.7-4.5, merge 4.4-5.2 + wobble, hand-off 6.0, letters 6.05-7.05, logo 7.05 |
| `ui/shards.html` (7 s) | slate vignette, 24 shards, blade, layered logo | fly-in 0.2-2.4, blade 2.6, key flash 2.7, fold 3.2-4.3, logo 4.3-4.55, pull-back 1.06 to 1.0 |
| `ui/type.html` | FORM, STACK, ECHO, END | cues from TYPE |

Render: `python3 lib/render_html.py ui/<page>.html --dur <len> --out frames/<page> --jobs 1`. Add `--opaque` for
liquid and shards, which paint their own world. Add `--fps 4` for a quick look before the full render. In `edit.py`
an `fk.Overlay("frames/morph")` sits on a `tl.BG` colour row. The camera push and the drop punch apply to the whole
composite with `fk.camera`, then `fk.hits`, then `fk.Finish(vignette=0, grain=2.5)`. A page placed later in a film
uses `fk.Overlay(folder, start=T)`.

All pages need `ui/logo.json`. Make it from the user's real logo with `python3 lib/logo_to_path.py refs/brand_logo.png --out ui/logo`. refs/logo.png is only the placeholder that `make_placeholders.py` writes.

**morphkit API (all pure):** `MK.box(cx,cy,w,h,r)`, `MK.chain(t, keys, def)` returns `{d, i, u}`,
`MK.boxAt(A,B,u,{squash})`, `MK.ptsAt(A,B,u,{rotate})`, `MK.flub(A,B)(u)`, `MK.combine(pieces,target)`,
`MK.separate(source,pieces)`, `MK.circle/roundRect/polygon/blob/shards`, `MK.fit/fitAll(paths,cx,cy,size)`,
`MK.color/colorLag`, `MK.anticipate`, `MK.overshoot`, `MK.press`, `MK.handoff`, `MK.rings(t,t0,{n,stagger,dur,scale})`,
`MK.goo(id,std,svg)`, `MK.loadLogo()`, `MK.logoSVG(L)`, and the eases `MK.E.expoInOut/expoOut/p3InOut/p3In/back/elastic/sine`.
Geometry is cached per shape object, so define the keys once, outside `render`.

## 3. Sound

| Film | Score (`ak.score`) | Arrangement |
|---|---|---|
| Morph Chain | `trap`, 120, F#m, breath = DROP - T_BREATH | filtered intro with heartbeats; a tape-stop "psych" 0.34 s before the breath; silence in the breath; the full groove on the drop |
| Send Morph | `house`, 120, Am | `ak.lowpass_region(music, 0, DROP, 1400, 0.7)` under the UI so the clicks read; it opens on the drop |
| Liquid | `ambient`, 100 | the merge wobble and the letters land on downbeats |
| Shards | `cinematic`, 96 | the blade on a bar line, the fold landing on the next |

**SFX map** (`lib/morphsfx.py` + the director's audiokit):

| Event | SFX | Gain | Placement |
|---|---|---|---|
| Every visible morph | `ms.shimmer(0.7)` | -13 dB | it peaks on the landing: place it at landing - 0.56 |
| Transition clip | morph swell, `ms.morph_swell(0.9)` in code | -15 dB | 0.25 s into the window (`tl.CLIP_STARTS`) |
| Pre-drop cuts | `ak.whoosh(0.3)` | -18 dB | peaks on the cut (`tl.PRE_CUTS`) |
| 0.25 s match cuts | `ak.shutter()` | -13 dB | each cut |
| FORM landings and UI state landings | `ak.tick()` | -12 to -14 dB | the landing frame |
| Negative hit | `ak.glitch_sfx(0.12)` in code | -12 dB | the hit |
| Send click | `ak.click()` + `ms.ring()` x3 (0.08 s apart, rising) | -8 / -14 dB | the click |
| Eyes pop (drop) | `ak.sparkle()` (+ the score's impact) | -10 dB | DROP |
| Wordmark grows, echo, logo | `ak.whoosh(0.5)`, `ak.impact(1.2-1.4)` | -14 / -9 dB | grow start and landing |
| Goo split and merge | `ms.goo(3)` | -14 dB | each neck snap and the merge |

Put no SFX on invisible cuts inside holds. VO is optional and needs the director's voice setup: one shouted line on
the drop ("Every form."), one normal line on the end card, with `ak.duck(music, regions, to=0.45)`. Master to
-14 LUFS. Read the RMS report, then ask the user to listen.
