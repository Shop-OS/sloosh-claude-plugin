/* ktkit.js: the kinetic-typography engine ("typography is a lead actor").
   Load AFTER the director kit.js (copied into lib/ by new_film.sh):  <script src="/lib/kit.js"></script><script src="/lib/ktkit.js"></script>
   A page calls KT.boot(THEME). It reads tl.json, builds every scene in TL.TYPE.kt (with its words from TL.COPY[id]),
   measures everything after the fonts load, and defines window.render(t): a pure function of film time t.
   No CSS animations, no timers, no randomness except seeded hashes. The page is transparent; the background
   (colour fields, hazes, grain, an optional AI plate) is drawn by edit.py (lib/ktfield.py).

   Scene = {id, move, t:[in, out], beats:[...], ...options}. Moves (see references/moves.md):
     stack  lines land one per beat (masked rise or wipe), full-bleed fit, accent/outline lines, per-word inversions
     slam   one word per beat, scale-to-fill, optional inverted box on chosen words
     stretch  variable width axis squeeze-to-fill (wdth min -> max), weight swing, squeeze out
     frame  stretch-to-frame: one word fills the safe height (scaleY from measured cap height) while wdth opens
     echo   hero word + outline copies cascading; the fill walks down the copies on later beats
     flap   split-flap / slot board: every tile rolls seeded glyphs, locks left to right
     count  odometer: digit columns roll to the value (true odometer carry, vertical motion blur)
     list   scroll list through a fixed band, stem above, payoff turns accent
     grid   kinetic grid of one word; inversion waves travel through it on beats; hero cell survives
     ticker running band (x is a pure function of t), spans scenes
     zoom   type-as-camera: the word lands, its letter counter opens on the next field, the camera flies through it
     lyric  word-on-beat phrases: caps slam, *serif italic* rise, ^accent^ (also the CAPTION LAYER over footage)
     lockA  the director two-line stack (K.lockupA), for captions over footage
     rise   editorial masked word rise with swing, strike / marker / variable-axis swell on chosen words
     swap   a line replaced word by word in the same spot
     wave   per-letter variable-axis wave (wght/wdth), skew snaps on beats
     end    end card: K.track (the only allowed letter-spacing move), rules from the centre, sub line
   Copy markup (any move with words): *word* serif italic accent face, ^word^ accent colour, _word_ outline. */
(function () {
  const { clamp, lerp, seg, E, set } = K;
  const KT = {}, M = {};
  const hash = (a, b = 0) => { let h = Math.imul(a + 1, 374761393) ^ Math.imul(b + 7, 668265263); h = Math.imul(h ^ (h >>> 13), 1274126177); return ((h ^ (h >>> 16)) >>> 0) / 4294967296; };
  const div = (cls, parent) => { const d = document.createElement('div'); d.className = cls; if (parent) parent.appendChild(d); return d; };
  const span = (cls, txt) => { const s = document.createElement('span'); s.className = cls; if (txt !== undefined) s.textContent = txt; return s; };

  // ---------------------------------------------------------------- fonts, axes, measuring (measure AFTER fonts load)
  KT.load = async specs => { await Promise.all(specs.map(s => document.fonts.load(s))); await document.fonts.ready; };
  KT.axes = (el, a) => { el.style.fontVariationSettings = Object.entries(a).map(([k, v]) => `"${k}" ${(+v).toFixed(2)}`).join(','); };
  KT.textW = el => { const r = document.createRange(); r.selectNodeContents(el); return r.getBoundingClientRect().width; };
  const fs = el => parseFloat(getComputedStyle(el).fontSize);
  KT.fit = (el, w, max = 1e4) => { for (let i = 0; i < 2; i++) el.style.fontSize = Math.min(max, fs(el) * w / KT.textW(el)) + 'px'; return fs(el); };
  KT.fitDown = (el, w) => { const tw = KT.textW(el); if (tw > w) el.style.fontSize = fs(el) * w / tw + 'px'; return fs(el); };
  const capC = {};
  KT.capRatio = el => { const cs = getComputedStyle(el), key = cs.fontFamily + cs.fontStyle + cs.fontWeight;
    if (!(key in capC)) { const c = document.createElement('canvas').getContext('2d'); c.font = `${cs.fontStyle} ${cs.fontWeight} 200px ${cs.fontFamily}`; capC[key] = c.measureText('H').actualBoundingBoxAscent / 200 || 0.72; }
    return capC[key]; };
  KT.baseline = el => { const i = document.createElement('i'); i.style.cssText = 'display:inline-block;width:0;height:0;vertical-align:baseline'; el.appendChild(i); const y = i.getBoundingClientRect().top; i.remove(); return y; };
  // ink box of an element's text: horizontal from a Range, vertical = cap height above the measured baseline
  KT.ink = el => { const r = document.createRange(); r.selectNodeContents(el); const b = r.getBoundingClientRect(), base = KT.baseline(el), cap = KT.capRatio(el) * fs(el);
    return { l: b.left, r: b.right, w: b.width, top: base - cap, bot: base, h: cap, cx: (b.left + b.right) / 2, cy: base - cap / 2 }; };

  // ---------------------------------------------------------------- copy markup -> word spans
  KT.parse = txt => String(txt).split(/\s+/).filter(Boolean).map(tok => ({ t: tok.replace(/[*^_]/g, ''), it: /^\^?\*.*\*\^?$/.test(tok), acc: tok.includes('^'), ol: /^_.*_$/.test(tok) }));
  KT.line = (txt, cls = '') => { const l = div('kt-line ' + cls), inn = span('kt-in');
    KT.parse(txt).forEach((w, i) => { if (i) inn.appendChild(document.createTextNode(' ')); inn.appendChild(span('w' + (w.it ? ' it' : '') + (w.acc ? ' acc' : '') + (w.ol ? ' ol' : ''), w.t)); });
    l.appendChild(inn); return l; };
  KT.letters = (txt, cls = '') => { const l = div('kt-line ' + cls), inn = span('kt-in'); [...String(txt)].forEach(ch => inn.appendChild(span('ch', ch === ' ' ? ' ' : ch))); l.appendChild(inn); return l; };

  // ---------------------------------------------------------------- placement inside the safe zone (measured, never guessed)
  function place(ctx, block, box, ay = 0.5) {
    block.style.left = box.l + 'px'; block.style.width = box.w + 'px'; block.style.top = '0px';
    const h = block.getBoundingClientRect().height; block.style.top = (box.top + (box.h - h) * ay) + 'px';
  }
  // vertical-feed right action rail (9:16): readable lines whose box reaches below rail.y must end left of rail.x
  function railFix(ctx, block, lines, box, ay, align) {
    if (!ctx.rail || box.noRail) return;
    for (let pass = 0; pass < 3; pass++) {
      let moved = false;
      lines.forEach(l => { const r = l.getBoundingClientRect();
        if (r.bottom > ctx.rail.y && r.right > ctx.rail.x + 1) {
          const allowed = align === 'left' ? ctx.rail.x - r.left : 2 * (ctx.rail.x - (r.left + r.right) / 2);
          l.style.fontSize = fs(l) * Math.max(0.3, allowed / r.width) + 'px'; moved = true; } });
      if (!moved) return; place(ctx, block, box, ay);
    }
  }
  // height fit: a block (fitted to the box WIDTH) must also fit the box HEIGHT (wide formats, many lines)
  function fitH(block, els, box) { for (let i = 0; i < 2; i++) { const h = block.getBoundingClientRect().height; if (h <= box.h) return; const k = box.h / h * 0.98; els.forEach(e => { e.style.fontSize = fs(e) * k + 'px'; }); } }
  function scene(sc, ctx, z = 1) {
    const root = div('kt-sc', ctx.stage); root.style.zIndex = z; root.dataset.id = sc.id;
    const [a, b] = sc.t, pre = sc.pre ?? 0.12, post = sc.post ?? 0.45;
    return { root, a, b, vis: t => { const on = t >= a - pre && t < b + post; root.style.display = on ? 'block' : 'none'; return on; } };
  }
  const beatsOf = (sc, n, ctx) => Array.from({ length: n }, (_, i) => sc.beats?.[i] ?? sc.beats?.[sc.beats.length - 1] ?? sc.t[0] + i * ctx.B);
  // masked rise of an inline-block inner (clip on the line, the inner travels 114% of its own height)
  function riseIn(line, t, b, dur = 0.4) { const u = E.out(seg(t, b - 0.07, b - 0.07 + dur)); line.style.clipPath = 'inset(-40% -12% -16% -12%)'; line.firstChild.style.transform = `translateY(${(1 - u) * 114}%)`; return u; }
  function wipeIn(line, t, b, slide = 44) { const u = E.out(seg(t, b - 0.06, b + 0.12)); line.style.clipPath = `inset(-40% ${100 - u * 100}% -40% -6%)`;
    line.firstChild.style.transform = `translateX(${-slide * (1 - E.out(seg(t, b - 0.06, b + 0.3)))}px)`; return u; }
  // exits: 'wipe' (to the right, 0.2 s), 'up' (rise out), 'squeeze' (clip to centre), 'cut'
  function exitOut(line, t, b, kind = 'wipe', k = 0) {
    if (t < b) return false; const v = E.in(seg(t, b + k * 0.04, b + 0.2 + k * 0.04));
    if (kind === 'cut') { line.style.visibility = 'hidden'; return true; }
    if (kind === 'up') { line.firstChild.style.transform = `translateY(${-114 * v}%)`; line.style.clipPath = 'inset(-40% -12% -16% -12%)'; }
    else if (kind === 'squeeze') line.style.clipPath = `inset(-40% ${v * 50}% -40% ${v * 50}%)`;
    else { line.style.clipPath = `inset(-40% -6% -40% ${v * 106}%)`; line.firstChild.style.transform = `translateX(${v * 50}px)`; }
    return true;
  }
  // per-word colour inversion on beats: inv rows [time, line, word(-1 = all), dur]
  const invOn = (inv, t, li, wi) => (inv || []).some(([ti, l, w, d]) => l === li && (w < 0 || w === wi) && t >= ti && t < ti + (d ?? 0.15));
  function kicker(ctx, block, txt) { if (!txt) return null; const k = KT.line(txt, 's kick'); k.style.fontSize = 32 * ctx.u + 'px'; block.appendChild(k); return k; }

  // ================================================================ MOVES
  M.stack = (sc, C, ctx) => {
    const S = scene(sc, ctx, sc.z), u = ctx.u, block = div('kt-block', S.root), box = ctx.box(sc);
    block.style.alignItems = sc.align === 'left' ? 'flex-start' : 'center';
    const kick = kicker(ctx, block, sc.kicker);
    const lines = C.map((txt, i) => { const l = KT.line(txt, (sc.font || 'd') + ((sc.accent || []).includes(i) ? ' acc' : '') + ((sc.outline || []).includes(i) ? ' ol' : ''));
      l.style.fontSize = (sc.size ?? 200) * u + 'px'; if (sc.axes) KT.axes(l, sc.axes); block.appendChild(l); return l; });
    const invL = lines.filter((l, i) => (sc.inv || []).some(r => r[1] === i));    // an inverted word's box (0.07 em each side) stays inside the safe zone too
    lines.forEach(l => { const w = sc.fill === false ? box.w : box.w * (sc.fillW ?? 1); sc.fill === false ? KT.fitDown(l, w) : KT.fit(l, w, (sc.max ?? 420) * u);
      if (invL.includes(l)) KT.fitDown(l, w - 0.14 * fs(l)); });
    lines.forEach((l, i) => { if (i) l.style.marginTop = (sc.lead ?? -0.02) + 'em'; });
    if (kick) kick.style.marginBottom = 18 * u + 'px';
    const ip = invL.length ? 0.07 * Math.max(...invL.map(fs)) : 0, hb = ip ? Object.assign({}, box, { top: box.top + ip, h: box.h - 2 * ip }) : box;
    fitH(block, lines, hb); place(ctx, block, hb, sc.y ?? 0.5); railFix(ctx, block, lines, hb, sc.y ?? 0.5, sc.align);
    const beats = beatsOf(sc, lines.length, ctx), last = beats[beats.length - 1], words = lines.map(l => [...l.querySelectorAll('.w')]);
    return { render(t) {
      if (!S.vis(t)) return;
      const hold = E.inOut(seg(t, last + 0.3, S.b));
      block.style.transform = `scale(${1 + (sc.push ?? 0.025) * hold})`;
      if (kick) { riseIn(kick, t, S.a); exitOut(kick, t, S.b, sc.exit); }
      lines.forEach((l, i) => { const b = beats[i];
        l.style.visibility = t < b - 0.07 ? 'hidden' : 'visible';
        if (!exitOut(l, t, S.b, sc.exit, i)) { if (sc.enter === 'wipe') wipeIn(l, t, b, 44 * u); else riseIn(l, t, b); }
        l.style.transform = `translateX(${(i % 2 ? 1 : -1) * (sc.drift ?? 10) * u * hold}px)`;
        words[i].forEach((w, k) => { w.classList.toggle('inv', invOn(sc.inv, t, i, k));
          if (sc.flash) w.style.color = t >= b && t < b + 4 / ctx.fps ? sc.flash[(i + k) % sc.flash.length] : ''; });
      });
    } };
  };

  M.slam = (sc, C, ctx) => {
    const S = scene(sc, ctx, sc.z), u = ctx.u, box = ctx.box(sc);
    const items = C.map((txt, i) => { const block = div('kt-block', S.root), l = KT.line(txt, (sc.font || 'd') + ((sc.accent || []).includes(i) ? ' acc' : ''));
      l.style.fontSize = (sc.size ?? 240) * u + 'px'; if (sc.axes) KT.axes(l, sc.axes); block.appendChild(l);
      KT.fit(l, box.w * (sc.fillW ?? 1), (sc.max ?? 460) * u); fitH(block, [l], box); place(ctx, block, box, sc.y ?? 0.5); railFix(ctx, block, [l], box, sc.y ?? 0.5);
      l.style.transformOrigin = '50% 55%'; return { block, l, words: [...l.querySelectorAll('.w')] }; });
    const beats = beatsOf(sc, items.length, ctx);
    return { render(t) {
      if (!S.vis(t)) return;
      let cur = -1; beats.forEach((b, i) => { if (t >= b - 0.001) cur = i; });
      items.forEach(({ block, l, words }, i) => { const on = i === cur && t < S.b + (sc.exit === 'cut' ? 0 : 0.25);
        block.style.display = on ? 'block' : 'none'; if (!on) return;
        K.slam(l, t, beats[i]); if (t >= S.b) exitOut(l, t, S.b, sc.exit || 'squeeze');
        const inv = (sc.inv || []).includes(i) && t < beats[i] + (sc.invDur ?? 0.2); words.forEach(w => w.classList.toggle('inv', inv)); });
    } };
  };

  M.stretch = (sc, C, ctx) => {
    const S = scene(sc, ctx, sc.z), u = ctx.u, box = ctx.box(sc), ax = ctx.th.axes || {};
    const w0 = sc.w0 ?? ax.wdth?.[0] ?? 62, w1 = sc.w1 ?? ax.wdth?.[1] ?? 125, g0 = sc.g0 ?? 900, g1 = sc.g1 ?? 900;
    const block = div('kt-block', S.root); block.style.alignItems = 'center';
    const lines = C.map((txt, i) => { const l = KT.line(txt, 'd' + ((sc.accent || []).includes(i) ? ' acc' : '')); l.style.fontSize = (sc.size ?? 200) * u + 'px';
      KT.axes(l, { wght: Math.max(g0, g1), wdth: w1 }); block.appendChild(l); KT.fit(l, box.w, (sc.max ?? 460) * u); if (i) l.style.marginTop = (sc.lead ?? 0.07) + 'em'; return l; });
    fitH(block, lines, box); place(ctx, block, box, sc.y ?? 0.5); railFix(ctx, block, lines, box, sc.y ?? 0.5);
    const beats = beatsOf(sc, lines.length, ctx);
    return { render(t) {
      if (!S.vis(t)) return;
      lines.forEach((l, i) => { const b = beats[i], k = E.out(seg(t, b, b + (sc.dur ?? 0.9)), 4), v = E.in(seg(t, S.b, S.b + 0.25));
        l.style.visibility = t < b ? 'hidden' : 'visible';
        KT.axes(l, { wght: lerp(lerp(g0, g1, k), g0, v), wdth: lerp(lerp(w0, w1, k), w0, v) });
        l.style.transform = `scaleY(${1 + 0.14 * (1 - k)})`; l.style.clipPath = v > 0 ? `inset(-30% ${v * 50}% -30% ${v * 50}%)` : 'none'; });
    } };
  };

  M.frame = (sc, C, ctx) => {
    const S = scene(sc, ctx, sc.z), u = ctx.u, ax = ctx.th.axes || {}, m = (sc.margin ?? 48) * u;
    const w0 = sc.w0 ?? ax.wdth?.[0] ?? 62, w1 = sc.w1 ?? ax.wdth?.[1] ?? 125, g = sc.wght ?? 900;
    const block = div('kt-block', S.root), l = KT.line(C[0], 'd' + (sc.accent ? ' acc' : '')); block.appendChild(l);
    l.style.fontSize = 300 * u + 'px'; KT.axes(l, { wght: g, wdth: w1 }); KT.fit(l, ctx.W - 2 * m);
    const top = sc.top ?? ctx.SZ.top, bot = sc.bot ?? ctx.SZ.bot;
    place(ctx, block, { l: m, w: ctx.W - 2 * m, top: 0, h: ctx.H }, 0.5);
    const ink = KT.ink(l.firstChild), sy = (bot - top) / ink.h;
    block.style.top = (parseFloat(block.style.top) + (top + bot) / 2 - ink.cy) + 'px';     // cap centre on the band centre
    l.style.transformOrigin = `50% ${ink.cy - l.getBoundingClientRect().top + ((top + bot) / 2 - ink.cy)}px`;
    const b = beatsOf(sc, 1, ctx)[0];
    return { render(t) {
      if (!S.vis(t)) return;
      const k = E.out(seg(t, b, b + (sc.dur ?? 0.55)), 5), v = E.in(seg(t, S.b, S.b + 0.22));
      l.style.visibility = t < b ? 'hidden' : 'visible';
      KT.axes(l, { wght: g, wdth: lerp(w0, w1, E.out(seg(t, b - 0.05, b + 0.7), 3)) });
      l.style.transform = `scaleY(${Math.max(0.001, lerp(1, sy, k) * (1 - v))})`;
    } };
  };

  M.echo = (sc, C, ctx) => {
    const S = scene(sc, ctx, sc.z), u = ctx.u, box = ctx.box(sc), n = sc.n ?? 3, dir = sc.dir ?? 1;
    const block = div('kt-block', S.root); block.style.alignItems = 'center';
    const small = C[0] ? KT.line(C[0], 's kick') : null; if (small) { small.style.fontSize = 44 * u + 'px'; block.appendChild(small); }
    const hero = KT.line(C[1] ?? C[0], 'd acc'); hero.style.fontSize = (sc.size ?? 300) * u + 'px'; if (sc.axes) KT.axes(hero, sc.axes); block.appendChild(hero);
    KT.fit(hero, box.w, (sc.max ?? 320) * u); if (small) small.style.marginBottom = 10 * u + 'px';
    { const capH = KT.ink(hero.firstChild).h, room = box.h * 0.9 - (sc.n ?? 3) * capH * (sc.gap ?? 0.66) - block.getBoundingClientRect().height;   // the copies must fit below
      if (room < 0) hero.style.fontSize = fs(hero) * Math.max(0.4, 1 + room / (block.getBoundingClientRect().height + (sc.n ?? 3) * capH * (sc.gap ?? 0.66))) + 'px'; }
    place(ctx, block, box, sc.y ?? 0.3);
    { const gap = () => n * KT.ink(hero.firstChild).h * (sc.gap ?? 0.66), lim = box.top + box.h;     // the copies stay in the box, and left of the 9:16 rail
      if (ctx.rail && !box.noRail && hero.getBoundingClientRect().bottom + (dir > 0 ? gap() : 0) > ctx.rail.y) { KT.fitDown(hero, 2 * (ctx.rail.x - box.l - box.w / 2)); place(ctx, block, box, sc.y ?? 0.3); }
      const g = gap(), r = block.getBoundingClientRect(), over = dir > 0 ? r.bottom + g - lim : box.top - (r.top - g);
      if (over > 0) block.style.top = (parseFloat(block.style.top) + (dir > 0 ? -1 : 1) * Math.min(over, dir > 0 ? r.top - box.top : lim - r.bottom)) + 'px'; }
    const cap = KT.ink(hero.firstChild).h, ghosts = [];
    for (let k = 0; k < n; k++) { const g = hero.cloneNode(true); g.className = 'kt-line d ol ghost'; g.style.position = 'absolute'; g.style.left = 0; g.style.right = 0; g.style.textAlign = 'center'; g.style.top = hero.offsetTop + 'px'; block.appendChild(g); ghosts.push(g); }
    const beats = beatsOf(sc, 1 + (sc.walk ?? 0), ctx), a = beats[0];
    return { render(t) {
      if (!S.vis(t)) return;
      const k = E.out(seg(t, a, a + 0.35), 5), out = seg(t, S.b, S.b + 0.2);
      let f = 0; beats.slice(1).forEach(b => { if (t >= b) f++; });
      set(hero, { s: lerp(1.25, 1, k) * (1 + out * 0.12), o: (t >= a ? 1 : 0) * (1 - out), blur: (1 - k) * 6 + out * 10 });
      hero.classList.toggle('ol', f > 0); hero.classList.toggle('acc', f === 0);
      ghosts.forEach((g, j) => { const v = E.out(seg(t, a + 0.08 + j * 0.06, a + 0.42 + j * 0.06));
        set(g, { y: dir * (j + 1) * cap * (sc.gap ?? 0.66) * v * (1 - out), o: v * (f === j + 1 ? 1 : 0.8 - j * 0.2) * (1 - out) });
        g.classList.toggle('ol', f !== j + 1); g.classList.toggle('acc', f === j + 1); });
      if (small) set(small, { y: lerp(20 * u, 0, E.out(seg(t, a + 0.1, a + 0.4))), o: seg(t, a + 0.1, a + 0.3) * (1 - out) });
    } };
  };

  const CS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#%&';
  KT.flapLock = (sc, i) => sc.t[0] + (sc.roll ?? 0.45) + i * (sc.step ?? 0.05);      // ktfield.py uses the same formula for the ticks
  M.flap = (sc, C, ctx) => {
    const S = scene(sc, ctx, sc.z), u = ctx.u, box = ctx.box(sc), txt = String(C[0]).toUpperCase(), rate = (sc.rate ?? 2) / ctx.fps;
    const block = div('kt-block', S.root); block.style.alignItems = 'center';
    const kick = kicker(ctx, block, sc.kicker);
    const board = div('kt-line m board', block); board.style.fontSize = (sc.size ?? 150) * u + 'px';
    const tiles = [...txt].map((ch, i) => { const tl = span('tile'); const A = span('fa'), B = span('fb'); tl.append(A, B); board.appendChild(tl); return { tl, A, B, ch, blank: ch === ' ' }; });
    const lab = C[1] ? KT.line(C[1], 's kick') : null; if (lab) { lab.style.fontSize = 34 * u + 'px'; block.appendChild(lab); }
    tiles.forEach(o => { o.A.textContent = 'W'; }); KT.fitDown(board, box.w); if (kick) kick.style.marginBottom = 22 * u + 'px'; if (lab) lab.style.marginTop = 26 * u + 'px';
    place(ctx, block, box, sc.y ?? 0.5); railFix(ctx, block, [board], box, sc.y ?? 0.5);
    const locks = tiles.map((_, i) => KT.flapLock(sc, i)), lastLock = Math.max(...locks);
    return { render(t) {
      if (!S.vis(t)) return;
      if (kick) { riseIn(kick, t, S.a); exitOut(kick, t, S.b, 'wipe'); }
      if (lab) { lab.style.visibility = t < lastLock ? 'hidden' : 'visible'; riseIn(lab, t, lastLock + 0.08); exitOut(lab, t, S.b, 'wipe'); }
      tiles.forEach((o, i) => {
        const appear = E.out(seg(t, S.a + i * 0.02, S.a + 0.12 + i * 0.02)), gone = E.in(seg(t, S.b + i * 0.01, S.b + 0.1 + i * 0.01));
        o.tl.style.transform = `scaleY(${appear * (1 - gone)})`; o.tl.style.visibility = appear > 0 ? 'visible' : 'hidden';
        if (o.blank) { o.tl.classList.add('blank'); o.A.textContent = ' '; o.B.textContent = ''; return; }
        if (t >= locks[i]) { o.A.textContent = o.ch; o.B.textContent = ''; o.A.style.transform = o.B.style.transform = ''; return; }
        const x = Math.max(0, t - S.a) / rate, k = Math.floor(x), ph = x - k, nextLocked = S.a + (k + 1) * rate >= locks[i];
        o.A.textContent = CS[Math.floor(hash(i, k) * CS.length)]; o.B.textContent = nextLocked ? o.ch : CS[Math.floor(hash(i, k + 1) * CS.length)];
        const s = E.inOut(clamp((ph - 0.45) / 0.55)); o.A.style.transform = `translateY(${-100 * s}%)`; o.B.style.transform = `translateY(${100 - 100 * s}%)`;
      });
    } };
  };

  M.count = (sc, C, ctx) => {
    const S = scene(sc, ctx, sc.z), u = ctx.u, box = ctx.box(sc), str = String(C[0]);
    const block = div('kt-block', S.root); block.style.alignItems = 'center';
    const kick = kicker(ctx, block, sc.kicker);
    const line = div('kt-line d num', block), inn = span('kt-in'); line.appendChild(inn); line.style.fontSize = (sc.size ?? 300) * u + 'px'; if (sc.axes) KT.axes(line, sc.axes);
    const digits = [...str].filter(c => /\d/.test(c)).length, N = parseInt(str.replace(/\D/g, ''), 10) || 0; let p = digits;
    const cols = [...str].map(ch => { if (!/\d/.test(ch)) { inn.appendChild(span('st', ch)); return null; }
      p--; const col = span('col'), strip = span('strip'); for (let d = 0; d <= 10; d++) strip.appendChild(span('dg', String(d % 10))); col.appendChild(strip); inn.appendChild(col); return { col, strip, place: p }; }).filter(Boolean);
    const lab = C[1] ? KT.line(C[1], 's kick') : null; if (lab) { lab.style.fontSize = 40 * u + 'px'; lab.style.marginTop = 18 * u + 'px'; block.appendChild(lab); }
    KT.fit(line, box.w * (sc.fillW ?? 0.92), (sc.max ?? 520) * u); fitH(block, [line], box);
    place(ctx, block, box, sc.y ?? 0.5); railFix(ctx, block, [line], box, sc.y ?? 0.5);
    const b = beatsOf(sc, 1, ctx)[0], dur = sc.dur ?? 0.9, from = sc.start ?? 0;
    const val = t => lerp(from, N, E.out(seg(t, b, b + dur), 3));
    const pos = (v, pl) => { const q = Math.pow(10, pl), base = Math.floor(v / q) % 10; return pl === 0 ? base + (v % 1) : base + Math.max(0, (v % q) - (q - 1)); };
    return { render(t) {
      if (!S.vis(t)) return;
      if (kick) { riseIn(kick, t, S.a); exitOut(kick, t, S.b, 'wipe'); }
      const v = val(t), v2 = val(t + 1 / 60), vin = riseIn(line, t, b - 0.05, 0.3);
      if (!exitOut(line, t, S.b, sc.exit || 'wipe')) line.firstChild.style.transform += ` scale(${lerp(1.12, 1, E.out(seg(t, b, b + dur), 3))})`;
      cols.forEach(c => { const y = pos(v, c.place), y2 = pos(v2, c.place); c.strip.style.transform = `translateY(${-y / 11 * 100}%)`;
        c.col.style.opacity = c.place === 0 || v >= Math.pow(10, c.place) * 0.6 || v >= N ? 1 : 0.15;
        K.mblur(c.strip, 0, Math.min(18, Math.abs(y2 - y) * 60 * fs(line) * 0.02)); });
      if (lab) { lab.style.visibility = t < b + dur * 0.6 ? 'hidden' : 'visible'; riseIn(lab, t, b + dur * 0.6); exitOut(lab, t, S.b, 'wipe'); }
    } };
  };

  M.list = (sc, C, ctx) => {
    const S = scene(sc, ctx, sc.z), u = ctx.u, box = ctx.box(sc), H = ctx.H, band = H * (sc.band ?? 0.47);
    const stem = KT.line(C[0], (sc.stemFont || 'd') + ' stem'); stem.style.fontSize = (sc.stemSize ?? 96) * u + 'px'; S.root.appendChild(stem);
    const wrap = div('kt-listwrap', S.root), list = div('kt-list', wrap), bar = div('kt-bar', S.root);
    const rows = C.slice(1).map((txt, i, arr) => { const r = KT.line(txt, 'd row' + (i === arr.length - 1 ? ' pay' : '')); r.style.fontSize = (sc.size ?? 132) * u + 'px'; list.appendChild(r); return r; });
    const barW = (sc.bar ?? 14) * u, gapX = 28 * u; rows.forEach(r => KT.fitDown(r, box.w - barW - gapX)); KT.fitDown(stem, box.w);
    Object.assign(wrap.style, { position: 'absolute', left: (box.l + barW + gapX) + 'px', top: 0, width: (box.w - barW - gapX) + 'px', height: H + 'px' });
    const cy = rows.map(r => r.offsetTop + r.offsetHeight / 2), lh = rows[0].offsetHeight;
    Object.assign(stem.style, { position: 'absolute', left: box.l + 'px' }); stem.style.top = (band - lh / 2 - 14 * u - stem.getBoundingClientRect().height) + 'px';
    const clipTop = band - lh * 0.42;                                        // rows vanish as they leave the band: never beside the stem
    wrap.style.clipPath = `inset(${clipTop}px -10% 0px -10%)`;
    const fade = `linear-gradient(to bottom, #000 0, #000 ${box.bot - 220 * u}px, transparent ${box.bot}px)`;   // rows below fade out by the safe bottom
    wrap.style.webkitMaskImage = fade; wrap.style.maskImage = fade;
    Object.assign(bar.style, { position: 'absolute', left: box.l + 'px', top: (band - lh * 0.36) + 'px', width: barW + 'px', height: lh * 0.72 + 'px' });
    const Y = k => band - cy[k], beats = beatsOf(sc, rows.length, ctx);
    const yAt = t => { let y = H - cy[0] + lh; for (let j = 0; j < beats.length; j++) { const d = j === beats.length - 1 ? (sc.lastDur ?? 0.75) : (j === 0 ? 0.6 : 0.36), s = beats[j] - (j === beats.length - 1 ? 0.1 : 0.18);
      if (t >= s + d) { y = Y(j); continue; } if (t > s) y = lerp(y, Y(j), (j === 0 || j === beats.length - 1 ? E.out : E.inOut)((t - s) / d)); break; } return y; };
    return { render(t) {
      if (!S.vis(t)) return;
      riseIn(stem, t, S.a); exitOut(stem, t, S.b, 'wipe');
      const y = yAt(t); list.style.transform = `translateY(${y}px)`;
      rows.forEach((r, i) => { const v = Math.max(0, 1 - Math.abs(cy[i] + y - band) / lh); r.style.opacity = 0.2 + 0.8 * v * v;
        r.classList.toggle('acc', r.classList.contains('pay') && t >= beats[beats.length - 1]); });
      bar.style.transform = `scaleY(${E.out(seg(t, beats[0], beats[0] + 0.4)) * (1 - seg(t, S.b, S.b + 0.2))})`;
      wrap.style.opacity = 1 - seg(t, S.b, S.b + 0.2);
    } };
  };

  M.grid = (sc, C, ctx) => {
    const S = scene({ ...sc, post: sc.post ?? 0 }, ctx, sc.z), u = ctx.u, R = sc.rows ?? 9, Cn = sc.cols ?? 3;
    const area = sc.full === false ? ctx.box(sc) : { l: 0, top: 0, w: ctx.W, h: ctx.H };
    const cw = area.w / Cn, ch = area.h / R, hero = sc.hero ?? Math.floor(R / 2) * Cn + Math.floor(Cn / 2), o0 = sc.origin ?? hero;
    const cells = []; for (let r = 0; r < R; r++) for (let c = 0; c < Cn; c++) {
      const cell = div('kt-cell', S.root); Object.assign(cell.style, { left: area.l + c * cw + 'px', top: area.top + r * ch + 'px', width: cw + 'px', height: ch + 'px' });
      const k = cells.length, l = KT.line(C[0], (sc.font || 'd') + ((r + c) % 2 && sc.checker !== false ? ' ol' : '')); l.style.fontSize = ch * 0.62 + 'px'; cell.appendChild(l); KT.fitDown(l, cw * 0.84);
      cells.push({ cell, l, r, c, d: Math.abs(r - Math.floor(o0 / Cn)) + Math.abs(c - o0 % Cn), k }); }
    const beats = sc.beats || [], lag = sc.lag ?? 0.035, last = beats[beats.length - 1] ?? S.b;
    return { render(t) {
      if (!S.vis(t)) return;
      cells.forEach(({ cell, l, d, k }) => {
        const inU = E.out(seg(t, S.a + d * 0.03, S.a + 0.3 + d * 0.03)), isHero = k === hero && sc.keepHero !== false;
        const outU = isHero ? 0 : E.in(seg(t, last + 0.25 + d * 0.025, last + 0.45 + d * 0.025));
        let inv = beats.some(b => t - b - d * lag >= 0 && t - b - d * lag < (sc.hold ?? 0.1));
        if (isHero && t >= last) inv = true;
        cell.classList.toggle('inv', inv);
        const g = isHero && t >= last ? E.out(seg(t, last + 0.5, last + 0.9)) : 0, c = cells[k];       // hero travels to frame centre as it grows, after its neighbours leave
        set(cell, { o: inU * (1 - outU), s: isHero ? 1 + 0.5 * g : 1 - 0.3 * outU,
          x: g * (ctx.W / 2 - (area.l + (c.c + 0.5) * cw)), y: (1 - inU) * 30 * u + g * (ctx.H / 2 - (area.top + (c.r + 0.5) * ch)) });
        cell.style.zIndex = isHero ? 2 : 1; });
    } };
  };

  M.ticker = (sc, C, ctx) => {
    const S = scene(sc, ctx, sc.z ?? 0), u = ctx.u, band = div('kt-ticker', S.root), sep = sc.sep ?? '  —  ';
    band.style.top = ctx.H * (sc.y ?? ctx.tickerY) + 'px'; const row = KT.line(String(C[0]) + sep, (sc.font || 'd') + ' tick'); row.style.fontSize = (sc.size ?? 64) * u + 'px'; band.appendChild(row);
    const unit = KT.textW(row), reps = Math.ceil(ctx.W / unit) + 2; row.firstChild.textContent = (String(C[0]) + sep).repeat(reps);
    return { render(t) {
      if (!S.vis(t)) return;
      const gap = (sc.gaps || []).reduce((m, [g0, g1]) => Math.max(m, Math.min(E.inOut(seg(t, g0 - 0.2, g0)), 1 - E.inOut(seg(t, g1, g1 + 0.3)))), 0);
      S.root.style.display = gap >= 0.999 ? 'none' : 'block';                  // gaps: [[a, b]] windows where the band steps aside (grids, full-bleed words)
      const x = -(((sc.speed ?? 140) * u * Math.max(0, t - S.a)) % unit);
      row.style.transform = `translateX(${(sc.dir ?? 1) > 0 ? x : x - unit}px)`;
      band.style.clipPath = `inset(0 ${100 - 100 * E.out(seg(t, S.a, S.a + 0.4)) * (1 - gap)}% 0 0)`; band.style.opacity = 1 - seg(t, S.b, S.b + 0.2);
    } };
  };

  M.zoom = (sc, C, ctx) => {
    const S = scene(sc, ctx, sc.z ?? 20), u = ctx.u, box = ctx.box(sc), W = ctx.W, H = ctx.H;
    S.root.style.transformOrigin = `${W / 2}px ${H / 2}px`;
    const f0 = ctx.F(sc.t[0]), plate = div('kt-plate', S.root); plate.style.background = f0.bg;   // colours frozen at the scene's own field:
    S.root.style.setProperty('--ink', f0.ink); S.root.style.setProperty('--acc', f0.acc); S.root.style.color = f0.ink;   // the next field is already cut in under the counter
    const block = div('kt-block', S.root); block.style.alignItems = 'center';
    const l = KT.letters(String(C[0]), 'd' + (sc.accent ? ' acc' : '')); l.style.fontSize = (sc.size ?? 300) * u + 'px'; if (sc.axes) KT.axes(l, sc.axes); block.appendChild(l);
    KT.fit(l, box.w, (sc.max ?? 420) * u); place(ctx, block, box, 0.5);
    const chars = [...l.querySelectorAll('.ch')], txt = String(C[0]).toUpperCase();
    let li = sc.letter ?? -1; if (li < 0) for (const c of 'O0QDBP96A8R') { li = txt.indexOf(c); if (li >= 0) break; } if (li < 0) li = Math.floor(chars.length / 2);
    let ink = KT.ink(chars[li]), wr = l.getBoundingClientRect();
    // the counter centre goes to the frame centre; shrink if that pushes the word out of the safe box
    const right = ctx.rail && wr.bottom > ctx.rail.y ? Math.min(box.l + box.w, ctx.rail.x) : box.l + box.w;      // respect the vertical-feed rail
    const k = Math.min(1, (W / 2 - box.l) / Math.max(1, ink.cx - wr.left), (right - W / 2) / Math.max(1, wr.right - ink.cx));
    if (k < 1) { l.style.fontSize = fs(l) * k + 'px'; place(ctx, block, box, 0.5); ink = KT.ink(chars[li]); }
    block.style.left = (parseFloat(block.style.left) + W / 2 - ink.cx) + 'px'; block.style.top = (parseFloat(block.style.top) + H / 2 - ink.cy) + 'px';
    const rx = (sc.hole?.[0] ?? 0.2) * ink.w, ry = (sc.hole?.[1] ?? 0.3) * ink.h, b = beatsOf(sc, 1, ctx)[0], dur = sc.dur ?? 0.55, z0 = S.b - dur;
    return { render(t) {
      if (!(t >= b - 0.02 && t < S.b)) { S.root.style.display = 'none'; return; } S.root.style.display = 'block';   // the plate exists only from the landing
      K.slam(l, t, b); l.style.visibility = t < b ? 'hidden' : 'visible';
      const h = E.out(seg(t, z0, z0 + 0.12)), zu = seg(t, z0, S.b);
      const m = h > 0 ? `radial-gradient(ellipse ${rx * h}px ${ry * h}px at ${W / 2}px ${H / 2}px, transparent 96%, #000 100%)` : 'none';
      plate.style.webkitMaskImage = m; plate.style.maskImage = m;
      S.root.style.transform = `scale(${Math.exp(Math.log(sc.S ?? 40) * E.in(zu, 2.4))})`;
    } };
  };

  M.lyric = (sc, C, ctx) => {
    const S = scene(sc, ctx, sc.z), u = ctx.u, box = ctx.box(sc), cap = (sc.size ?? 200) * u;
    const block = div('kt-block', S.root); block.style.alignItems = sc.align === 'left' ? 'flex-start' : 'center';
    const rows = C.map(txt => { const r = KT.line(txt, 'lyr'); r.style.fontSize = cap + 'px'; block.appendChild(r);     // words sized in em of the row, so fitting the row fits them
      r.querySelectorAll('.w').forEach(w => { w.classList.add(w.classList.contains('it') ? 'serif' : 'd'); w.style.fontSize = (w.classList.contains('it') ? (sc.serif ?? 1.0) : 1) + 'em'; }); KT.fitDown(r, box.w); return r; });
    rows.forEach((r, i) => { if (i) r.style.marginTop = (sc.lead ?? 0.02) + 'em'; });
    fitH(block, rows, box); place(ctx, block, box, sc.y ?? 0.5); railFix(ctx, block, rows, box, sc.y ?? 0.5, sc.align);
    const words = rows.flatMap(r => [...r.querySelectorAll('.w')]), beats = beatsOf(sc, words.length, ctx);
    words.forEach(w => { if (w.classList.contains('serif')) { const i = span('wi', w.textContent); w.textContent = ''; w.appendChild(i); } });
    return { render(t) {
      if (!(t >= S.a - 0.06 && t < S.b)) { S.root.style.display = 'none'; return; } S.root.style.display = 'block';    // phrases hard-cut on the beat
      words.forEach((w, k) => { const b = beats[k];
        if (w.classList.contains('serif')) { const v = E.out(seg(t, b - 0.07, b + 0.35)); w.style.clipPath = 'inset(-30% -10% -22% -10%)'; w.firstChild.style.transform = `translateY(${(1 - v) * 112}%)`; w.style.visibility = t < b - 0.07 ? 'hidden' : 'visible'; }
        else { const v = E.out(seg(t, b - 0.03, b + 0.2), 5); set(w, { s: lerp(sc.slamFrom ?? 1.35, 1, v), o: t >= b - 0.03 ? 1 : 0 }); }
        w.classList.toggle('inv', (sc.inv || []).includes(k) && t >= b && t < b + (sc.invDur ?? 0.18)); });
      block.style.transform = `scale(${1 + 0.03 * Math.exp(-Math.max(0, t - beats[0]) / 0.25) * (t >= beats[0] ? 1 : 0)})`;
    } };
  };

  M.lockA = (sc, C, ctx) => {
    const S = scene(sc, ctx, sc.z), u = ctx.u, box = ctx.box(sc);
    const d = div('lockA', S.root), l0 = span('l d', C[0]), l1 = span('l d acc', C[1] ?? '');   // textContent: copy is never parsed as HTML
    l0.style.fontSize = 118 * u + 'px'; l1.style.fontSize = 168 * u + 'px'; l1.style.marginTop = '-0.13em'; d.append(l0, l1);
    const ls = [...d.querySelectorAll('.l')], widest = Math.max(...ls.map(l => KT.textW(l))), maxW = box.w * 0.96;
    if (widest > maxW) ls.forEach(l => { l.style.fontSize = fs(l) * maxW / widest + 'px'; });
    d.style.left = box.l + 'px'; d.style.top = (box.top + box.h - d.getBoundingClientRect().height) + 'px';
    return { render(t) { if (!S.vis(t)) return; K.lockupA(d, t, S.a, S.b); } };
  };

  M.rise = (sc, C, ctx) => {
    const S = scene(sc, ctx, sc.z), u = ctx.u, box = ctx.box(sc);
    const block = div('kt-block', S.root); block.style.alignItems = sc.align === 'center' ? 'center' : 'flex-start';
    const kick = kicker(ctx, block, sc.kicker); if (kick) kick.style.marginBottom = 26 * u + 'px';
    const lines = C.map(txt => { const l = KT.line(txt, (sc.font || 'd') + ' ed'); l.style.fontSize = (sc.size ?? 170) * u + 'px'; block.appendChild(l); return l; });
    const bw = box.w / 1.02;     // the hold push scales the block 2% from its left edge: fit to the box before that push
    const sizeAll = Math.min(...lines.map(l => { const s0 = fs(l); KT.fitDown(l, bw); const s = fs(l); l.style.fontSize = s0 + 'px'; return s; }));
    let size = sizeAll; lines.forEach(l => { l.style.fontSize = size + 'px'; });     // one size for the whole statement
    if (sc.fill) { size = Math.min((sc.max ?? 600) * u, size * bw / Math.max(...lines.map(l => KT.textW(l)))); lines.forEach(l => { l.style.fontSize = size + 'px'; }); }   // masthead: widest line spans the box
    { const h = block.getBoundingClientRect().height; if (h > box.h) { size *= box.h / h * 0.98; lines.forEach(l => { l.style.fontSize = size + 'px'; }); } }   // never taller than its box
    place(ctx, block, box, sc.y ?? 0.5); railFix(ctx, block, lines, box, sc.y ?? 0.5, sc.align || 'left');
    const words = lines.map(l => [...l.querySelectorAll('.w')].map(w => { const m = span('wm'); w.parentNode.insertBefore(m, w); m.appendChild(w); return w; }));
    const beats = beatsOf(sc, lines.length, ctx), br = block.getBoundingClientRect(), deco = [];
    const wordBox = (li, wi) => { const r = words[li][wi].getBoundingClientRect(); return { l: r.left - br.left, top: r.top - br.top, w: r.width, h: r.height }; };
    (sc.strike || []).forEach(([li, wi, at]) => { const r = wordBox(li, wi), bar = div('kt-strike', block); Object.assign(bar.style, { left: r.l - 4 * u + 'px', width: r.w + 8 * u + 'px', top: r.top + r.h * 0.55 + 'px', height: Math.max(4, r.h * 0.06) + 'px' }); deco.push({ kind: 's', el: bar, at, li, wi }); });
    (sc.marker || []).forEach(([li, wi, at]) => { const r = wordBox(li, wi), mk = div('kt-marker', block); Object.assign(mk.style, { left: r.l - 6 * u + 'px', width: r.w + 12 * u + 'px', top: r.top + r.h * 0.3 + 'px', height: r.h * 0.62 + 'px' }); deco.push({ kind: 'm', el: mk, at }); });
    return { render(t) {
      if (!S.vis(t)) return;
      if (kick) { riseIn(kick, t, S.a); exitOut(kick, t, S.b, 'up'); }
      block.style.transform = `scale(${1 + 0.02 * E.inOut(seg(t, beats[0], S.b))})`; block.style.transformOrigin = sc.align === 'center' ? '50% 50%' : '0% 50%';
      lines.forEach((l, i) => words[i].forEach((w, k) => { const b = beats[i] + k * (sc.stagger ?? 0.06), v = E.out(seg(t, b - 0.07, b + (sc.dur ?? 0.9)), 5), x = E.in(seg(t, S.b + k * 0.02, S.b + 0.3 + k * 0.02));
        w.parentNode.style.clipPath = 'inset(-30% -8% -24% -8%)'; w.style.transform = `translateY(${(1 - v) * 130 - x * 135}%) rotate(${(1 - v) * (sc.swing ?? 3)}deg)`;
        w.style.visibility = t < b - 0.07 || x >= 1 ? 'hidden' : 'visible'; w.classList.toggle('inv', invOn(sc.inv, t, i, k));
        if (sc.flash) w.style.color = t >= b && t < b + 4 / ctx.fps ? sc.flash[(i * 3 + k) % sc.flash.length] : ''; }));     // 4-frame landing accent
      (sc.swell || []).forEach(([li, wi, at, a0, a1, d]) => { const w = words[li][wi], v = E.inOut(seg(t, at, at + (d ?? 1.2))); const ax = {}; Object.keys(a1).forEach(key => { ax[key] = lerp(a0[key], a1[key], v); }); KT.axes(w, ax); });
      deco.forEach(o => { const v = E.out(seg(t, o.at, o.at + (o.kind === 's' ? 0.35 : 0.55)), o.kind === 's' ? 3 : 2), gone = seg(t, S.b, S.b + 0.2);
        o.el.style.transform = `scaleX(${v}) skewX(${o.kind === 'm' ? -2 : 0}deg)`; o.el.style.opacity = 1 - gone;
        if (o.kind === 's') words[o.li][o.wi].style.opacity = lerp(1, 0.35, seg(t, o.at + 0.3, o.at + 0.6)); });
    } };
  };

  M.swap = (sc, C, ctx) => {
    const S = scene(sc, ctx, sc.z), u = ctx.u, box = ctx.box(sc);
    const block = div('kt-block', S.root); block.style.alignItems = 'center';
    const cell = div('kt-swap', block), A = KT.line(C[0], (sc.font || 'd') + ' ed'), B = KT.line(C[1], (sc.font || 'd') + ' ed' + (sc.accentNew ? ' acc' : ''));
    cell.append(A, B); [A, B].forEach(l => { l.style.fontSize = (sc.size ?? 150) * u + 'px'; });
    const s = Math.min(KT.fitDown(A, box.w), KT.fitDown(B, box.w)); A.style.fontSize = B.style.fontSize = s + 'px';
    place(ctx, block, box, sc.y ?? 0.5); railFix(ctx, block, [A, B], box, sc.y ?? 0.5);
    const wrapW = l => [...l.querySelectorAll('.w')].map(w => { const m = span('wm'); w.parentNode.insertBefore(m, w); m.appendChild(w); return w; });
    const wa = wrapW(A), wb = wrapW(B), [b0, b1] = beatsOf(sc, 2, ctx);
    return { render(t) {
      if (!S.vis(t)) return;
      wa.forEach((w, k) => { const v = E.out(seg(t, b0 + k * 0.05 - 0.07, b0 + k * 0.05 + 0.45)), x = E.in(seg(t, b1 + k * 0.05, b1 + k * 0.05 + 0.22));
        w.parentNode.style.clipPath = 'inset(-4% -8% -18% -8%)'; if (x >= 1) { w.style.visibility = 'hidden'; return; } w.style.transform = `translateY(${(1 - v) * 110 - x * 110}%)`; w.style.visibility = t < b0 - 0.07 ? 'hidden' : 'visible'; });
      wb.forEach((w, k) => { const s0 = b1 + 0.24 + k * 0.05, v = E.out(seg(t, s0, s0 + 0.45)), x = E.in(seg(t, S.b + k * 0.03, S.b + 0.25 + k * 0.03));
        w.parentNode.style.clipPath = 'inset(-4% -8% -18% -8%)'; w.style.transform = `translateY(${(1 - v) * 120 - x * 120}%)`; w.style.visibility = t < s0 || x >= 1 ? 'hidden' : 'visible';
        w.style.color = sc.flash && t >= s0 + 0.1 && t < s0 + 0.1 + 4 / ctx.fps ? sc.flash : ''; });
    } };
  };

  M.wave = (sc, C, ctx) => {
    const S = scene(sc, ctx, sc.z), u = ctx.u, box = ctx.box(sc), ax = sc.ax || { wght: [200, 900], wdth: [125, 62] };   // Archivo ranges
    const block = div('kt-block', S.root); block.style.alignItems = 'center';
    const l = KT.letters(String(C[0]), 'd' + (sc.accent ? ' acc' : '')); l.style.fontSize = (sc.size ?? 260) * u + 'px'; block.appendChild(l);
    const chars = [...l.querySelectorAll('.ch')];
    // fit to the WIDEST state the wave can reach (sampled), so it fills the box without ever overflowing it
    const at = s0 => { const a = {}; Object.entries(ax).forEach(([k, [lo, hi]]) => { a[k] = lerp(lo, hi, s0); }); return a; };
    const widest = () => Math.max(...[0, 0.25, 0.5, 0.75, 1].map(s0 => { chars.forEach((c, i) => KT.axes(c, at(i % 2 ? 1 - s0 : s0))); const w1 = KT.textW(l); chars.forEach(c => KT.axes(c, at(s0))); return Math.max(w1, KT.textW(l)); }));
    l.style.fontSize = Math.min((sc.max ?? 520) * u, fs(l) * box.w / widest()) + 'px'; place(ctx, block, box, sc.y ?? 0.5); railFix(ctx, block, [l], box, sc.y ?? 0.5);
    const beats = sc.beats || [];
    return { render(t) {
      if (!S.vis(t)) return;
      const ph = t - S.a, amp = E.out(seg(t, S.a, S.a + 0.6)) * (1 - E.in(seg(t, S.b - 0.4, S.b)));
      let snap = 0; beats.forEach(b => { if (t >= b) snap = Math.exp(-(t - b) / (sc.snapT ?? 0.14)); });
      chars.forEach((c, i) => { const s = 0.5 + 0.5 * Math.sin(2 * Math.PI * (sc.freq ?? 0.7) * ph - i * (sc.spread ?? 0.75)), a = {};
        Object.entries(ax).forEach(([k, [lo, hi]]) => { a[k] = lerp(lo, lerp(lo, hi, s), amp) ; });
        KT.axes(c, a); c.style.transform = ctx.th.slnt ? `skewX(${ctx.th.slnt * snap}deg)` : ''; });   // no slant axis in the vendored faces: skew snap
      l.style.clipPath = `inset(-30% ${100 - 100 * E.out(seg(t, S.a, S.a + 0.3))}% -30% -5%)`;
      if (t >= S.b) exitOut(l, t, S.b, 'squeeze');
    } };
  };

  M.end = (sc, C, ctx) => {
    const S = scene(sc, ctx, sc.z), u = ctx.u, box = ctx.box(sc);
    const block = div('kt-block kt-end', S.root); block.style.alignItems = 'center';
    const tt = span(sc.font || 'd', C[0]); tt.style.fontSize = (sc.size ?? 96) * u + 'px'; tt.style.display = 'inline-block'; tt.style.whiteSpace = 'nowrap'; block.appendChild(tt);
    const rules = div('kt-rules', block), rl = div('kt-rule', rules), rr = div('kt-rule', rules);
    const sub = C[1] ? KT.line(C[1], 's kick') : null; if (sub) { sub.style.fontSize = 30 * u + 'px'; block.appendChild(sub); }
    const [tr0, tr1] = sc.track || [0.62, 0.40];
    K.track(tt, 1e6, 0, tr0, tr1, 1.2); KT.fitDown(tt, box.w * 0.94);   // fit at the FINAL tracking
    Object.assign(rules.style, { position: 'relative', width: '100%', height: 4 * u + 'px', margin: 22 * u + 'px 0' });
    place(ctx, block, box, sc.y ?? 0.45);
    return { render(t) {
      if (!S.vis(t)) return;
      K.track(tt, t, S.a, tr0, tr1, sc.dur ?? 1.2);
      const g = E.out(seg(t, S.a + 0.3, S.a + 1.1)), half = (sc.rule ?? 140) * u * g, W2 = box.w / 2;
      Object.assign(rl.style, { left: (W2 - half) + 'px', width: half + 'px' }); Object.assign(rr.style, { left: W2 + 'px', width: half + 'px' });
      if (sub) set(sub, { o: seg(t, S.a + 0.6, S.a + 1.0), y: (1 - E.out(seg(t, S.a + 0.6, S.a + 1.1))) * 14 * u });
    } };
  };

  KT.moves = M;

  // ================================================================ page boot
  // THEME = {fonts:[load specs], axes:{wdth:[min,max]}, slnt:-10|0 (skew degrees for wave snaps), safe:'reels'|'poster'|{l,r,top,bot}, caption:false}
  KT.boot = async (THEME = {}) => {
    const TL = await loadTL(), W = TL.W, H = TL.H, u = Math.min(W, H) / 1080, ar = W / H;
    const tall = ar < 0.7, shape = tall ? 'tall' : ar < 0.85 ? 'portrait' : ar > 1.2 ? 'landscape' : 'square';   // 9:16 is tall, 4:5 portrait feed (no platform rail)
    await KT.load(THEME.fonts || []);
    const stage = document.getElementById('stage'); Object.assign(stage.style, { width: W + 'px', height: H + 'px' }); stage.style.setProperty('--u', u);
    const safe = THEME.safe || TL.SAFE || 'reels';
    const SZ = typeof safe === 'object' ? Object.assign({}, safe) : tall ? (safe === 'poster' ? { l: 64 * u, r: W - 64 * u, top: 200 * u, bot: H - 420 * u } : { l: 120 * u, r: W - 120 * u, top: 240 * u, bot: H - 660 * u })
      : shape === 'landscape' ? { l: W * 0.06, r: W * 0.94, top: H * 0.08, bot: H * 0.92 } : { l: 90 * u, r: W - 90 * u, top: 90 * u, bot: H - 90 * u };
    const tickerY = tall ? 0.74 : 0.885;
    ((TL.TYPE || {}).kt || []).filter(s => s.move === 'ticker').forEach(s => { const y = H * (s.y ?? tickerY);   // a ticker reserves its band:
      if (y > H / 2 && y < SZ.bot + 10 * u) SZ.bot = y - 24 * u; if (y <= H / 2 && y + 110 * u > SZ.top) SZ.top = y + 110 * u; });     // content never runs under it
    SZ.w = SZ.r - SZ.l; SZ.h = SZ.bot - SZ.top;
    const fields = (TL.FIELDS || []).slice().sort((a, b) => a[0] - b[0]);
    const F = t => { let f = fields[0] || [0, '#000000', TL.INK || '#FFFFFF', TL.ACCENT || '#F6C945']; for (const r of fields) if (r[0] <= t + 1e-6) f = r; return { bg: f[1], ink: f[2], acc: f[3] || TL.ACCENT }; };
    const ctx = { TL, W, H, u, SZ, stage, F, th: THEME, tickerY, B: TL.B || 0.5, fps: TL.FPS || 30,
      rail: tall && safe === 'reels' ? { x: W - 180 * u, y: 840 * u } : null, shape,
      box: sc => { if (!sc.box) return sc.noRail ? Object.assign({}, SZ, { noRail: true }) : SZ; const [l, top, r, bot] = sc.box; return { l: l * W, r: r * W, top: top * H, bot: bot * H, w: (r - l) * W, h: (bot - top) * H, noRail: sc.noRail }; } };
    if (THEME.caption || TL.CAPTION) stage.classList.add('over-footage');
    const scenes = ((TL.TYPE || {}).kt || []).map(sc => { const mk = M[sc.move]; if (!mk) throw new Error('ktkit: unknown move ' + sc.move);
      const C = (TL.COPY || {})[sc.id]; if (!C) throw new Error('ktkit: no COPY for ' + sc.id); return mk(sc, Array.isArray(C) ? C : [C], ctx); });
    window.render = t => { const f = F(t); stage.style.setProperty('--bg', f.bg); stage.style.setProperty('--ink', f.ink); stage.style.setProperty('--acc', f.acc); stage.style.color = f.ink;
      scenes.forEach(s => s.render(t)); };
    KT.safe = { l: SZ.l, r: SZ.r, top: SZ.top, bot: SZ.bot, rail: ctx.rail, shape };     // kt_sheet.py --boxes draws exactly this
    window.render(0); window.READY = true;
  };
  window.KT = KT;
})();
