/* kit.js: helpers for code-built UI, type and logos.
   Pages expose window.render(t): a pure function of film time t. No CSS animations, no timers, no real time.
   Load with <script src="/lib/kit.js"></script>: render_html.py serves the film folder as the site root.
   Everything lives on window.K. */
(function () {
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const lerp = (a, b, u) => a + (b - a) * u;
  const seg = (t, a, b) => clamp((t - a) / (b - a));                       // 0..1 progress of t through [a, b]
  const E = {
    lin: u => clamp(u),
    out: (u, p = 4) => 1 - Math.pow(1 - clamp(u), p),                       // quartic ease-out (default for entrances)
    in: (u, p = 3) => Math.pow(clamp(u), p),                                // exits accelerate
    inOut: u => { u = clamp(u); return u < .5 ? 8 * u ** 4 : 1 - Math.pow(-2 * u + 2, 4) / 2; },
    back: (u, s = 1.7) => { u = clamp(u) - 1; return u * u * ((s + 1) * u + s) + 1; },   // overshoot pops
    spring: (u, z = 0.55, w = 14) => { u = clamp(u); return 1 - Math.exp(-z * w * u) * Math.cos(w * Math.sqrt(1 - z * z) * u); },
  };
  // keyframes: kf(t, [[t0, v0], [t1, v1, ease?], ...]); numbers or arrays of numbers
  function kf(t, keys) {
    if (t <= keys[0][0]) return keys[0][1];
    for (let i = 1; i < keys.length; i++) {
      const [ta, va] = keys[i - 1], [tb, vb, ez] = keys[i];
      if (t <= tb) { const u = (ez || E.inOut)((t - ta) / (tb - ta));
        return Array.isArray(va) ? va.map((x, k) => lerp(x, vb[k], u)) : lerp(va, vb, u); }
    }
    return keys[keys.length - 1][1];
  }
  const $ = s => document.querySelector(s);
  // set(el, {x, y, s, sx, sy, r, rx, ry, skx, o, blur, clip, origin, persp}): one place that writes every transform
  function set(el, p) {
    if (typeof el === 'string') el = $(el);
    if (!el) return;
    const tr = [];
    if (p.persp) tr.push(`perspective(${p.persp}px)`);
    tr.push(`translate(${p.x || 0}px, ${p.y || 0}px)`);
    if (p.rx) tr.push(`rotateX(${p.rx}deg)`); if (p.ry) tr.push(`rotateY(${p.ry}deg)`);
    if (p.r) tr.push(`rotate(${p.r}deg)`); if (p.skx) tr.push(`skewX(${p.skx}deg)`);
    const s = p.s ?? 1; tr.push(`scale(${(p.sx ?? 1) * s}, ${(p.sy ?? 1) * s})`);
    el.style.transform = tr.join(' ');
    if (p.origin) el.style.transformOrigin = p.origin;
    if (p.o !== undefined) el.style.opacity = p.o;
    if (p.blur !== undefined) el.style.filter = p.blur > 0.05 ? `blur(${p.blur}px)` : 'none';
    if (p.clip !== undefined) el.style.clipPath = p.clip;
  }
  const measure = el => (typeof el === 'string' ? $(el) : el).getBoundingClientRect();

  // directional motion blur through an SVG feGaussianBlur whose stdDeviation (x, y) is set per frame (whip pans)
  let _mbN = 0;
  function mblur(el, dx, dy) {
    if (typeof el === 'string') el = $(el);
    const id = 'mb_' + (el.id || (el.id = 'k' + (++_mbN)));   // a counter, not a random id: renders stay repeatable
    let f = document.getElementById(id);
    if (!f) {
      const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg'); svg.setAttribute('width', 0); svg.setAttribute('height', 0);
      svg.style.position = 'absolute';
      svg.innerHTML = `<filter id="${id}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="0 0"/></filter>`;
      document.body.appendChild(svg); f = document.getElementById(id);
    }
    f.firstChild.setAttribute('stdDeviation', `${Math.abs(dx).toFixed(2)} ${Math.abs(dy).toFixed(2)}`);
    el.style.filter = (Math.abs(dx) + Math.abs(dy) > 0.1) ? `url(#${id})` : 'none';
  }

  // ---------- typography ----------
  // Lockup A: two-line stack. Line 1 white, line 2 accent and larger, tucked up into line 1.
  // In: left-to-right mask wipe over 0.16 s (line 2 starts 0.07 s later) + a 36–50 px slide with quartic ease-out.
  // Out: wipe and slide to the right over 0.2 s.
  function lockupA(el, t, tIn, tOut, o = {}) {
    if (typeof el === 'string') el = $(el);
    const lines = el.querySelectorAll('.l');
    lines.forEach((ln, k) => {
      const a = tIn + k * 0.07, u = E.out(seg(t, a, a + 0.16)), slide = (o.slide || 44) * (1 - E.out(seg(t, a, a + 0.32)));
      let clip = `inset(-20% ${100 - u * 100}% -20% -2%)`, x = -slide;
      if (t >= tOut) { const v = E.in(seg(t, tOut + k * 0.04, tOut + 0.2 + k * 0.04)); clip = `inset(-20% -2% -20% ${v * 100}%)`; x = v * 50; }
      set(ln, { x, clip, o: t < a ? 0 : 1 });
    });
  }
  // Lockup B: echo stack. A huge accent word scales 1.25 -> 1.0 as it lands; outlined copies cascade below it with
  // falling opacity; a small tracked word sits above.
  function echo(el, t, tIn, tOut, o = {}) {
    if (typeof el === 'string') el = $(el);
    const hero = el.querySelector('.hero'), copies = el.querySelectorAll('.ghost'), small = el.querySelector('.small');
    const u = E.out(seg(t, tIn, tIn + 0.35), 5), out = seg(t, tOut, tOut + 0.2);
    set(hero, { s: lerp(1.25, 1, u) * (1 + out * 0.15), o: (t >= tIn ? 1 : 0) * (1 - out), blur: (1 - u) * 6 + out * 10 });
    copies.forEach((c, k) => { const v = E.out(seg(t, tIn + 0.08 + k * 0.06, tIn + 0.4 + k * 0.06));
      set(c, { y: lerp(-40, 0, v), o: v * (0.75 - k * 0.2) * (1 - out) }); });
    if (small) set(small, { y: lerp(20, 0, E.out(seg(t, tIn + 0.1, tIn + 0.4))), o: seg(t, tIn + 0.1, tIn + 0.3) * (1 - out) });
  }
  // Word slam: in on a beat, scale 1.35 -> 1 with blur 12 -> 0 in 4 frames, a 1-frame overshoot
  function slam(el, t, tIn, tOut = 1e9) {
    const u = seg(t, tIn, tIn + 0.13), out = seg(t, tOut, tOut + 0.12);
    set(el, { s: lerp(1.35, 1, E.out(u, 5)) + (u >= 1 ? 0.02 * Math.exp(-(t - tIn - 0.13) / 0.05) : 0), o: (t >= tIn ? 1 : 0) * (1 - out), blur: (1 - u) * 12 });
  }
  // End card: letter spacing tightens 0.62 -> 0.40 em (on a wrapper, using word-spacing-free per-letter offsets)
  function track(el, t, tIn, from = 0.62, to = 0.40, dur = 1.2) {
    if (typeof el === 'string') el = $(el);
    if (!el._spans) { const txt = el.textContent; el.textContent = ''; el._spans = [...txt].map(ch => { const s = document.createElement('span'); s.textContent = ch === ' ' ? '\u00A0' : ch;   /* a span holding only a space collapses */ s.style.display = 'inline-block'; el.appendChild(s); return s; }); }
    const u = E.out(seg(t, tIn, tIn + dur), 3), ls = lerp(from, to, u), n = el._spans.length;
    el._spans.forEach((s, k) => { s.style.marginRight = (k < n - 1 ? ls : 0) + 'em'; });
    set(el, { o: seg(t, tIn, tIn + 0.3), blur: (1 - u) * 6 });
  }
  // Typing with the newest letters in a gradient (accent -> ink) and a blinking caret (blink from film time, not a timer)
  function typeOn(el, text, t, t0, cps = 22, o = {}) {
    if (typeof el === 'string') el = $(el);
    const n = clamp(Math.floor((t - t0) * cps), 0, text.length), fade = o.fade || 4;
    const esc = c => c === '&' ? '&amp;' : c === '<' ? '&lt;' : c === '>' ? '&gt;' : c;   // the text is shown as text, never parsed as HTML
    let html = '';
    for (let i = 0; i < n; i++) { const age = n - 1 - i, ch = esc(text[i]); html += age < fade ? `<span style="color:${o.hot || '#F6C945'};opacity:${0.55 + 0.45 * (age / fade)}">${ch}</span>` : ch; }
    const caret = (Math.floor(t * 2.4) % 2 === 0 || n < text.length) ? `<span style="opacity:.9">|</span>` : '';
    el.innerHTML = html + caret;
  }
  function counter(el, t, t0, t1, from, to, fmt = v => Math.round(v).toLocaleString()) {
    if (typeof el === 'string') el = $(el); el.textContent = fmt(lerp(from, to, E.out(seg(t, t0, t1), 3)));
  }
  // Cursor placed from MEASURED element boxes (never hand-typed coordinates). Curved path, click squash at tClick.
  function cursor(cur, fromEl, toEl, t, t0, t1, tClick) {
    if (typeof cur === 'string') cur = $(cur);
    const a = fromEl && typeof fromEl === 'object' && !(fromEl instanceof Element) ? fromEl : center(fromEl), b = center(toEl), u = E.inOut(seg(t, t0, t1));
    const bend = Math.sin(Math.PI * u) * 60, x = lerp(a.x, b.x, u) + bend * 0.3, y = lerp(a.y, b.y, u) - bend;
    const sq = tClick !== undefined ? 1 - 0.18 * Math.exp(-Math.pow((t - tClick) / 0.06, 2)) : 1;
    set(cur, { x, y, s: sq });
  }
  const center = el => { const r = measure(el); return { x: r.left + r.width / 2, y: r.top + r.height / 2 }; };
  // Place a line by measured width: returns the x that centres (or right-aligns) it inside a box
  function placeX(el, box = { left: 0, width: innerWidth }, align = 'center') {
    const w = measure(el).width; return align === 'center' ? box.left + (box.width - w) / 2 : align === 'right' ? box.left + box.width - w : box.left;
  }
  // Shine bar wiping across an element (chip shine / text shimmer); the element needs position:relative; overflow:hidden
  function shine(el, t, t0, dur = 0.5) {
    if (typeof el === 'string') el = $(el);
    let s = el.querySelector(':scope > .k-shine');
    if (!s) { s = document.createElement('i'); s.className = 'k-shine'; Object.assign(s.style, { position: 'absolute', top: '-20%', bottom: '-20%', width: '35%', left: '0', background: 'linear-gradient(100deg,transparent,rgba(255,255,255,.75),transparent)', pointerEvents: 'none', mixBlendMode: 'screen' }); el.appendChild(s); }
    const u = seg(t, t0, t0 + dur); s.style.transform = `translateX(${lerp(-120, 320, E.inOut(u))}%)`; s.style.opacity = u > 0 && u < 1 ? 1 : 0;
  }
  window.K = { clamp, lerp, seg, E, kf, $, set, measure, mblur, lockupA, echo, slam, track, typeOn, counter, cursor, center, placeX, shine };
  // timeline: pages read the same numbers as edit.py and audio.py
  window.loadTL = async () => { try { window.TL = await (await fetch('/tl.json')).json(); } catch (e) { window.TL = {}; } return window.TL; };
})();
