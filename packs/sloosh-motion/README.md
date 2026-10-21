# Sloosh motion films

![Sloosh](assets/sloosh.png)

Sloosh motion films makes stylised short films on your computer: product reveals, beat-synced edits, software walkthroughs and feature announcements, kinetic typography, glitch, dot-matrix and morph films. Claude plans the film on a beat grid, builds the type and interface layers as HTML, composites the frames in Python, adds synthesised sound and checks the result with ffmpeg. When a shot is missing, Claude can make stills and clips with Sloosh. Claude shows you the quoted credits for each round of Sloosh work and asks for your approval before it spends.

## What you need

- A coding agent that runs commands on your own computer, such as Claude Code. The films render locally. In the Claude app, use the core Sloosh plugin's video skills instead.
- Python 3.9 or later with numpy, OpenCV and SciPy, and ffmpeg.
- Playwright with its Chromium browser, to render the HTML type layers.
- Optional: rembg for product cutouts, and Kokoro or Piper for a voice-over.
- For Sloosh shots: the core Sloosh plugin, installed and connected, and a Sloosh workspace with spending enabled.

Claude asks you before it installs anything, and it suggests a virtual environment. The pack's scripts never download or install anything by themselves.

## Install in Claude Code

Run this in Claude Code:

```
/plugin marketplace add Shop-OS/sloosh-claude-plugin
/plugin install sloosh@sloosh
/plugin install sloosh-motion@sloosh
```

Then run `/mcp`, select sloosh and sign in to Sloosh to authorize the workspace you want to use.

## Install in Codex

```
codex plugin marketplace add Shop-OS/sloosh-claude-plugin
codex plugin add sloosh@sloosh
codex plugin add sloosh-motion@sloosh
codex mcp login sloosh
```

## Skills

| Skill | What it makes |
|---|---|
| sloosh-motion-director | The entry point. It picks a style, sets up the film folder and runs the shared engine. |
| product-reveal | A cinematic reveal of one product: light sweeps, macro details and a packshot end card. |
| aura-farming-edit | A fast, beat-synced hype edit with speed ramps, flashes and bold type. |
| saas-product-video | A software walkthrough built from rebuilt interface screens, or a short feature announcement. |
| kinetic-typography | A words-only film: posters, editorial serif, lists, captions, lyric beats and variable-width type. |
| glitch-fx | A glitch film with signal loss, RGB splits, scan lines and HUD type. |
| morph-shapeshift | Shape and logo morphs, liquid transitions and shard breaks. |
| dot-matrix-particles | A film where dots and particles form a product, a logo or data. |

## How a film is made

1. Claude asks for the brief: the product, the words, the format (9:16, 16:9, 1:1 or 4:5), the length and any music you have.
2. Claude sets up a film folder in your project. It holds the timeline, the type layers, the fonts, the shots and the output.
3. Claude writes the timeline on the beat grid and makes placeholder shots, so you can see the cut before any spending.
4. If shots are missing, Claude plans Sloosh stills or clips in rounds of up to eight, quotes each round and waits for your approval.
5. Claude renders, mixes the sound and runs a quality check on the final file.

## What the pack sends and reads

The film work runs on your computer and stays in your project folder. Claude calls the Sloosh server at https://mcp.sloosh.ai/mcp only for Sloosh stills and clips, with the prompts and images you approve, using the access you grant when you connect. Sloosh stores the images and videos it makes in your workspace, and Claude downloads the ones the film uses into the film folder.

## Spending

Sloosh uses the credits and the daily spending allowance of the workspace you connect. Claude gets a quote for each item before it makes anything. For each round, Claude shows each item with its quoted credits and the round total, and asks for one approval. If the round total is more than the allowance left today, Claude gives you the Sloosh settings link and does not run the round. Claude cannot raise the allowance, buy credits or change your plan. A film made only from your own photos and footage costs nothing in Sloosh.

## Fonts and third-party code

The pack ships six open font families under the SIL Open Font License 1.1: Archivo, Inter Tight, Instrument Serif, Bodoni Moda, Fraunces and JetBrains Mono. Each licence text is beside its fonts. The morph skill ships flubber under the MIT License, with a notices file for the code it bundles.

## Example prompts

- "Make a 12-second dark luxury product reveal of our perfume bottle, 9:16."
- "Cut a 20-second hype edit of our new trainer to this track."
- "Make a 30-second walkthrough video of our dashboard app, 16:9."
- "Make a feature announcement film for our new auto-resize feature."
- "Make a kinetic typography video with these four lines, on the beat."

## Support

- Documentation: https://sloosh.ai/docs/mcp
- Support: https://sloosh.ai/docs/support
- Privacy policy: https://sloosh.ai/privacy-policy
- Terms of use: https://sloosh.ai/terms-of-use
