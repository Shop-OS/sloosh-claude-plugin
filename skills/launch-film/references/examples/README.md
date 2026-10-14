# Worked example — Sloosh launch film, PART 3 (25 s)

The complete source of a delivered film. Brand: Sloosh (beta.sloosh.ai) — black `#0A0A0A`,
yellow `#FECC15`, Bowlby One. VO: "Meet Sloosh. You bring the idea. Choose what you want to
make. Creative workflows already prepared to help you get there. Bring your photo. Explore the
possibilities. Keep the details that make it yours. Your cake. On the moon. Your photograph. A
new visual story. Your product. A campaign that feels like you."

These files import the engine paths of the original project (`../components/*`, `../lib/*`,
`../theme`, `../ui/*`, `../brand/*`). The example `theme.ts` uses `C.yellow*` names where the
template uses `C.accent*`.

| Scene file | VO | Techniques to borrow |
|---|---|---|
| `scenes/A_Logo.tsx` | Meet Sloosh. | paper specimen grid (`Guides`, squares, crosshair, construction circle, corner labels); wordmark letters rising from masks; eyes pop on the brand word; 3-frame accent → dark punctuation; **zoom-through** the pupil in log space with 28 blur samples |
| `scenes/B_Idea.tsx` | You bring the idea. | hand-drawn SVG idea (pathLength stroke draw), Caveat handwriting reveal, "YOUR IDEA" bbox; **whip-out** with smear |
| `scenes/C_Choose.tsx` | Choose what you want to make. | **3D website fly-over** (`Stage3D/Plane3D`, `path` camera keys), billboarded floating chips with contact shadows, projected cursor click on a real tool card, tilt-shift, **pixel-block wipe** to accent |
| `scenes/D_Creative.tsx` | Creative workflows | **split word around an image window** (2-frame image cycling), hard cut to **rail word** with a running signal, collapse into the eye badge (**graphic match**) |
| `scenes/E_Spaces.tsx` | …prepared to help you get there. | pull-back from the badge (z 1260 → working distance), staggered card entrances radiating from the target, hover + click on the real workflow card, pinned tag via `project()`, **push-in hand-off** |
| `scenes/F_BringPhoto.tsx` | Bring your photo. | rebuilt run page; drag a photo print into an upload slot on the word "photo"; slot fills; Generate enabled + pressed; push into the slot image (**hand-off**) |
| `scenes/G_Explore.tsx` | Explore the possibilities. | node canvas (prompt + inputs → model → six outputs lifted in Z, far nodes for breadth); hard cut to a yellow **contact sheet**; source tile **expands** into the next scene's opening view |
| `scenes/HIJ_Cake.tsx` | Keep the details… / Your cake. / On the moon. | **crop camera**; detail windows with dimmed surround + KEEP chips + readout; 5-frame "YOURS." punctuation; pull back to the baker; **object-locked match cut** to the moon result with persistent bbox and 2-frame RGB split; flash out |
| `scenes/KL_Cup.tsx` | Your photograph. / A new visual story. | photo print with viewfinder focus box; **in-frame swap** to the café result (cup locked); print shrinks into a 3×2 storyboard with a sequential highlight; whip-out |
| `scenes/M_Product.tsx` | Your product. | **specimen sheet**: guides, rulers, accent squares, the product seen through a window pre-aligned with the poster |
| `scenes/NO_Finale.tsx` | A campaign that feels like you. + end card | **window expand** into the poster, poster shrinks into a 4-format campaign board (clean plates + re-typeset copy), **continuous camera** spread into floating cards around the logo; eyes open on "you", follow the cursor to the CTA, blink |

Support files:
- `brand/Logo.tsx`, `brand/logoPaths.ts` — SVG wordmark with per-letter reveal masks and animatable eyes (`look`, `eyeOpen`, socket/pupil colours).
- `ui/Kit.tsx`, `ui/Pages.tsx`, `ui/Icons.tsx` — UI rebuilt from the live site's computed styles: nav, key-shadow buttons, prompt bar, tool/model/workflow cards, upload slots, node labels/ports, Explore/Spaces/run pages.
- `lib/cakeView.ts`, `lib/chairView.ts` — measured alignments for the object-locked cuts (the template's `cropCamera.ts` generalises these).
- `SoundTrack.tsx` — the full cue sheet (peak-aligned, labelled) with ducking; `timeline.ts` — VO block and scene table; `assets.ts` — image registry with measured product boxes.

Timeline (frames @30): A 0–54 · B 54–92 · C 92–136 · D 136–176 · E 176–240 · F 240–273 · G 273–330 · HIJ 330–462 · KL 462–550 · M 550–582 · NO 582–750.
