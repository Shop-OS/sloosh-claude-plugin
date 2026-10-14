# Brand capture from a website

## 1. Open the site
Use the host's browser tool if it has one: open the URL, set a 1440×900 desktop viewport
for layout reading, read the page text for copy and take a few screenshots for layout
reference. Without a browser tool, fetch the page HTML and its stylesheets and read the
tokens from them, or ask the user for the brand fonts and colours.
The user may be signed in: read only what the task needs, never change account state,
and never put their credits, avatar, names or private items in the film.

## 2. Extract tokens (run in the page with the browser tool's script runner)

```js
const css = (el) => getComputedStyle(el);
const heads = [...document.querySelectorAll('h1,h2,h3')].slice(0, 12).map(e => {
  const s = css(e); return { t: e.textContent.trim().slice(0, 50), f: s.fontFamily, w: s.fontWeight, s: s.fontSize, c: s.color, ls: s.letterSpacing };
});
const fontFaces = [...document.fonts].map(f => `${f.family} ${f.weight} ${f.status}`).filter((v, i, a) => a.indexOf(v) === i).slice(0, 30);
const body = css(document.body);
const ctas = [...document.querySelectorAll('a,button')].filter(b => b.offsetWidth > 60 && b.offsetHeight > 28).slice(0, 40).map(b => {
  const s = css(b); return { t: b.textContent.trim().slice(0, 30), bg: s.backgroundColor, c: s.color, r: s.borderRadius, sh: s.boxShadow.slice(0, 80), f: s.fontFamily.slice(0, 40), w: s.fontWeight, s: s.fontSize };
}).filter(b => b.bg !== 'rgba(0, 0, 0, 0)').slice(0, 8);
const vars = {}; for (const ss of document.styleSheets) { try { for (const r of ss.cssRules) { if (r.selectorText && /:root|\.dark|html/.test(r.selectorText)) for (const p of r.style) if (p.startsWith('--')) vars[p] = r.style.getPropertyValue(p).trim(); } } catch (e) {} }
({ body: { bg: body.backgroundColor, color: body.color, font: body.fontFamily }, heads, fontFaces, ctas, vars: Object.fromEntries(Object.entries(vars).slice(0, 160)) })
```

Record in `src/theme.ts`: display/script/UI fonts (load from Google Fonts when available),
background and layer colours, accent and its pressed/edge shadow (e.g. a `0 3px 0` key
shadow), text colours, radii, line colours.

## 3. Collect real copy and structure
- Hero headline + sub, section headings, nav items, button labels.
- Feature/workflow/template names and one-line descriptions (use them verbatim on cards).
- Page section order and approximate pixel layout at 1440 width.
- Any mascot/logo behaviour worth animating (e.g. eyes in a wordmark).

## 4. Rebuild, don't screenshot
Recreate the pages as React components sized for a 1440-wide page (`ui/Pages.tsx`), using
the tokens above and the project's images (pack images or mocks) for thumbnails. Rebuilt
UI is crisp at any camera distance, lets cards animate (highlight, lift, stagger) and lets
you replace third-party content with the user's own imagery. See
`examples/ui/Kit.tsx` and `examples/ui/Pages.tsx` for a full rebuild (nav, buttons with key
shadows, prompt bar, tool/model/workflow cards, upload slots, node labels, run page).

## 5. Logos
Inline the SVG paths in a TS module (extract with a small Python regex script) so each
letter can rise from its own mask and inner parts (eyes, dots) can animate. Keep the
geometry verbatim; animate only transforms and fills. See `examples/brand/Logo.tsx`
(per-letter reveal masks, blinking eyes, pupils that look anywhere and follow a cursor).
