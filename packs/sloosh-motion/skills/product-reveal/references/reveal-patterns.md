# Product Reveal: what good reveal films share

This file sums up what strong product reveal films have in common. Use it to choose a template and to judge a cut. It is for your understanding only. Never put any of it in a prompt as a reference to a real film, maker or product.

## 1. Shared patterns

1. **Hooks** (the first 1.5 s) come in three families:
   - a silhouette or rim from black
   - an extreme macro that is already moving
   - a tiny product in a vast single-colour void

   None opens on a logo or text.
2. **Reveal mechanics.** Each film has one primary mechanic:
   - light-up (from rim only to the full key)
   - a light sweep along an edge or a body line
   - a macro tour, then a pull-back
   - exploded, then reassembled
   - levitation, then a landing on a pedestal or into the case
   - a texture or ingredient world
   - a feature-physics demo (a splash, a squash, a plug-in)
   - a repetition array
   - lifestyle hands
3. **The product is withheld, then given once.** The full, sharp, frontal product appears at 55 to 75% of the runtime, not at 0 s. (This skill's default lands it on DROP at about 54%.)
4. **The world colour is the product's colour family.** A red serum in a red world, titanium in black, a white tube in greige, a grey shoe in graphite. One accent comes from the product itself (an LED, a button, the logo colour).
5. **Type is rare:**
   - 0 to 4 short callouts (1 to 3 words each, one at a time, centred or on a leader line)
   - then an end card: the wordmark (top third or centre), the product name, and a tiny tracked tagline (about 1.5% of the width, tracking 0.3 to 0.6 em)
6. **Endings:**
   - a packshot on a pedestal, a rock or a floor, with a reflection
   - the background lifts or changes for the end card
   - a hold of 2 to 4.5 s (a fragrance film can hold up to about 6 s)
   - an optional light-down bookend
7. **Pacing:**
   - luxury: 1.5 to 3.5 s per shot, or one continuous take
   - playful tech: 0.4 to 0.8 s detail cuts with whip-ins and motion blur
   - one speed ramp or strobe moment at 50 to 60% of the runtime
8. **Light:**
   - one hard key, one or two rims, and negative fill
   - specular streaks travel along the material
   - the exposure stays continuous across cuts

Exploded and spec films share a further pattern: one continuous take on pure black with a cold rim; a speed ramp into a slow-motion separation along one vertical axis; a few macro holds, each with one tracked callout (a huge numeral, a small wide-tracked label and a leader line pinned to a part), shown one at a time with hard snaps; then reassembly in reverse order with mechanical snaps, and a locked final frame with the title resolving from blur.

Nature and ingredient films share another: an identity anchor (the single most distinctive feature of the product reads in every beat), a fixed palette taken only from the product, condensation or texture described in physical terms, museum-slow motion with one levitation beat, and no type on screen.

## 2. Beat templates

**T1: Dark Luxury Light-Sweep (15 s)**
- rim hook 0-2
- light-up 2-3.6
- three macros with sweeps 3.6-8.4
- strobe and hero at 8.4
- hero arc 8.4-11
- background lift and end card 11-15

**T2: Splash / Levitation (15 s)**
- a tiny product in a single-colour void 0-1.5
- the label macro 1.5-3.5 (code: label_macro.py on the real cutout)
- a levitation tumble 3.5-5
- a texture or splash world with three benefit words 5-10
- a flare whip at 10
- the descent onto the pedestal 10-12.5
- end card 12.5-15

**T3: Exploded View (15 s)**
- hero push 0-1.5
- slow-motion separation 1.5-3.5
- a fly-through between the layers and 3 or 4 spec holds 3.5-10
- reassembly 10-12.5
- locked title 12.5-15

**T4: Clean Studio Turntable (12 to 15 s)**
- a floating spin 0-1
- whip-in macros 1-6 (0.5 to 0.8 s each)
- a feature-physics demo 6-10
- hero spin and end card 10-15

**T5: Ingredient Hyper-motion Tunnel (15 s)**
- a tactile macro 0-2
- a trigger whip 2-2.8
- the tunnel 2.8-5.3
- the return 5.3-6
- a counter-orbit assembly 6-10.5
- an overhead hero 10.5-12
- a graphic end card 12-15

**T6: Lifestyle Unboxing (15 s)**
- a material macro 0-1.5
- hands open the box 1.5-4
- the product lifts 4-6
- three in-use cuts with one serif line each 6-11
- a floating hero 11-12.5
- end card 12.5-15

**T7: Nature World (15 s)**
- a condensation boom-up 0-2.5
- a depth row 2.5-4.5
- levitation with the ingredients in orbit 4.5-8.5
- a closure macro 8.5-11
- a slow-motion impact and hold 11-15
- no type

The default film in examples/dark_luxury follows T1 on a 96 BPM grid (see the SKILL.md story template). The other templates are starting points: rebuild the beat table in tl.py, keep withhold-then-give, and keep one primary mechanic.

## 3. Categories

This table suggests a beat template from section 2 for each category. The look of the film (the sub-preset) follows the category default in SKILL.md section 1. When the two differ, use the SKILL.md default unless the user picks another look.

| Category | First pick | Second pick |
|---|---|---|
| Fragrance | Dark Luxury Light-Sweep | Splash / Levitation |
| Skincare and beauty | Splash / Levitation | Ingredient Tunnel |
| Sneakers and footwear | Dark Luxury (a material macro variant) | Exploded View |
| Gadgets, audio and cameras | Exploded View | Clean Studio Turntable |
| Watches, jewellery and accessories | Dark Luxury Light-Sweep | Nature World (a rock packshot) |
| Food and drink | Ingredient Tunnel | Nature World |
| Home and furnishing | Lifestyle Unboxing | Clean Studio |
