# Sub-preset swaps (saas-product-video)

The example film (`examples/ui-walkthrough-30s/`) is **UI Walkthrough**. Every other tile starts from it: change the
listed tokens and files, keep the toolchain, the beat grid and the QA. Accent = the brand's accent everywhere
(`tl.ACCENT`, `tl.ACCENT2` = its lighter gradient end).

## Creative Team Intro (all HTML, editorial; the "AI creative team" film)
- `tl.py`: no hook AI rows; story = intro (0–5 s) → typing screen → build steps → cascade → tagline + feature card →
  black end card listing the roles `{ product shots · lifestyle scenes · short videos · campaigns }`. 30–40 s, 16:9, 24 fps.
- Pages: `intro.html` (longer: 3 editorial lines, the bracket build twice), `ui.html` reduced to S5–S8 (composer,
  photos, typing, send), `build.html` with the thermal hero, 4 steps and 12 tiles, a `tagline.html` (gradient,
  serif line, one feature card). Joins between pages: `fk.mosaic_wipe` 0.3 s (pixel dissolves), never crossfades.
- AI: 0–2 stills only (a blurred portrait for the intro, a hero image for the thermal reveal); 0 clips.
- Sound: `ambient` or `house` at 100–110 BPM, soft; ticks for type, soft pops for cards, sweeps for transitions.

## Dark Glow (dev tools, AI, infra)
`ui.html :root` → `--bg:#0B0B10; --surface:#14141B; --side:#101016; --line:rgba(255,255,255,.08); --ink:#F2F2F5; --mute:#8D8C9C`.
- Stage background `radial-gradient(60% 50% at 50% 110%, <accent>33, #07070A 70%)`; ribbons at 0.18 opacity.
- Window shadow adds `0 0 120px <accent>40`; the build page becomes the one LIGHT beat (`#F4F5F8`, dark ink).
- Type unchanged (hype stack reads on dark). Sound: `techno` 124–128 BPM.

## Mobile App (consumer apps; 9:16 master)
- `tl.py` `W, H = 1080, 1920`, FPS 30. Opener = the phone still and clip (hand on a phone), no desk.
- `ui.html` → a phone frame 500×1080 (radius 80, bezel 16) as the window; scenes become screen pushes inside the phone;
  taps instead of the arrow cursor (a 64 px translucent disc that squashes, plus a ripple). Measured targets as always.
- Captions in the top band (y 260–640); bottom 660 px clear.

## Data Story (analytics, finance, growth)
- `build.html` S2 becomes stat moments: a count-up on a growing curve (`K.counter` + an SVG path drawn by
  `stroke-dashoffset`), a "2X → 3X" pill, one dark statement line. Every number labelled **Example data** unless the
  user verified it.
- Hook lockups use the customer's own pain numbers only when true ("9 TABS." / "1 REPORT.").

## 9:16, 1:1 and 4:5 from the 16:9 master (any tile)
- Pages that lay themselves out (`type.html`, `intro.html`, `build.html`, `toggle.html`) re-render at the film's W and H.
- `ui.html` stays a 1920×1080 design: render it with `--w 1920 --h 1080 --scale 2`. edit.py then shows it through
  `saaskit.Reframe("frames/ui", REFRAME, start=tl.T_UI, speed=tl.UI_SP)`, a crop that follows the action:
  keys `(t, fx, fy, zoom)` on each scene's focus (the chip, the menu, the sidebar, the status cell, the composer, the send button).
  Below zoom 1 the whole page shows over a blurred copy of itself, so a wide scene stays whole.
