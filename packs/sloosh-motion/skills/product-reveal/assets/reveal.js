/* reveal.js: product-reveal helpers for HTML pages rendered frame by frame by lib/render_html.py.
 * Load AFTER the director's kit:  <script src="/lib/kit.js"></script><script src="/lib/reveal.js"></script>
 * (copy this file into the film's lib/ folder). Every helper is a pure function of film time t, called from
 * window.render(t). No GSAP, no CSS animations, no timers, no Math.random: any frame renders from t alone.
 *
 *   RV.sweep(el, t, t0, dur, o)      specular band clipped to the product alpha (mask = the real cutout PNG)
 *   RV.lightUp(el, t, t0, dur, o)    rim plate -> lit plate through a moving soft mask
 *   RV.float(t, t0, o)               levitation bob -> {y, r}
 *   RV.shadow(el, t, t0, o)          contact shadow that breathes against the float
 *   RV.focus(t, t0, dur, from)       rack-focus blur value (px)
 *   RV.bgLift(el, t, t0, dur, o)     black -> soft radial glow (end-card background lift)
 *   RV.wipe(el, t, t0, dur, dir)     clip-path reveal (up | down | left | right | iris)
 *   RV.turn(t, t0, dur, from, to)    +-8 deg fake turntable for a flat cutout -> deg
 *   RV.counter(el, t, t0, dur, to, o) spec counter: tabular digits count up, zero-padded
 *   RV.narrowBand(img, a, b)         MEASURED y (0..1 of image height) where the silhouette is narrowest
 *   RV.pass(el, t, t0, t1, o)        a line that slides in fast, settles, then slides out (type passing behind)
 *   RV.callout(el, t, t0, hold)      dot + leader + value + label, pinned to a real part
 */
(function () {
  const { clamp, lerp, seg, E, set } = window.K;
  const $ = s => (typeof s === 'string' ? document.querySelector(s) : s);
  const RV = {};

  // 1. Specular sweep. el sits exactly over the product. o.mask = the cutout PNG, so the band only lights product
  // pixels (reads as a real highlight on glass/metal, never a rectangle). width = band % (8-12 product-sized,
  // 3-5 on a full frame whose product fills half the frame). peak <= 0.25 on a dark-plate glint.
  RV.sweep = function (el, t, t0, dur = 1.1, o = {}) {
    el = $(el);
    if (el._rvo !== o) {                         // (re)style when a different sweep becomes active
      const w = o.width ?? 11, a = o.angle ?? 100, p = o.peak ?? 0.8, c = o.color || '255,255,255';
      el.style.backgroundImage = `linear-gradient(${a}deg, rgba(${c},0) ${50 - w}%, rgba(${c},${p * .35}) ${50 - w / 3}%,` +
        ` rgba(${c},${p}) 50%, rgba(${c},${p * .35}) ${50 + w / 3}%, rgba(${c},0) ${50 + w}%)`;
      el.style.backgroundSize = '300% 100%'; el.style.backgroundRepeat = 'no-repeat';
      el.style.mixBlendMode = o.blend || 'screen'; el.style.pointerEvents = 'none';
      if (o.mask) for (const k of ['webkitMask', 'mask']) {
        el.style[k + 'Image'] = `url(${o.mask})`; el.style[k + 'Size'] = '100% 100%'; el.style[k + 'Repeat'] = 'no-repeat'; }
      el._rvo = o;
    }
    const u = E.inOut(seg(t, t0, t0 + dur)), v = o.reverse ? u : 1 - u;
    el.style.backgroundPosition = `${v * 100}% 0%`;
    el.style.opacity = (t >= t0 && t <= t0 + dur) ? 1 : 0;
  };
  // several sweeps on one element: call with the active one only
  RV.sweeps = (el, t, list) => { const s = list.find(([a, d]) => t >= a && t <= a + d) || list[0]; RV.sweep(el, t, ...s); };

  // 2. Light-up: the lit plate stacked over the rim plate; a soft-edged mask travels across it.
  RV.lightUp = function (el, t, t0, dur = 1.6, o = {}) {
    el = $(el); const soft = o.soft ?? 24, dir = { left: '90deg', right: '270deg', top: '180deg', bottom: '0deg' }[o.from || 'left'];
    const e = -soft + E.inOut(seg(t, t0, t0 + dur)) * (100 + 2 * soft);
    const g = `linear-gradient(${dir}, #000 ${e - soft}%, rgba(0,0,0,0) ${e + soft}%)`;
    el.style.webkitMaskImage = g; el.style.maskImage = g;
  };

  // 3. Levitation: slow sine bob + micro tilt. amp 6-10 px, period 2.8-3.2 s. Heavy objects: amp 0.
  RV.float = (t, t0, o = {}) => { const ph = 2 * Math.PI * Math.max(0, t - t0) / (o.period ?? 3.0);
    return { y: -(o.amp ?? 8) * Math.sin(ph), r: (o.rot ?? 0.6) * Math.sin(ph + 0.6) }; };
  RV.shadow = function (el, t, t0, o = {}) {
    const ph = 2 * Math.PI * Math.max(0, t - t0) / (o.period ?? 3.0), k = 0.5 + 0.5 * Math.sin(ph);   // 1 = product highest
    set(el, { sx: lerp(1, 0.86, k), o: lerp(o.max ?? 0.55, o.min ?? 0.32, k) * (o.fade ?? 1) });
  };

  // 4. Rack focus: blur from `from` px to 0 over dur.
  RV.focus = (t, t0, dur = 0.7, from = 10) => from * (1 - E.out(seg(t, t0, t0 + dur), 3));

  // 5. Background lift: radial glow from base to lit. el is full-frame.
  RV.bgLift = function (el, t, t0, dur = 1.4, o = {}) {
    el = $(el); const hex = h => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16));
    const A = hex(o.base || '#050505'), B = hex(o.lit || '#2A241D'), u = E.inOut(seg(t, t0, t0 + dur));
    const m = A.map((x, i) => Math.round(x + (B[i] - x) * u));
    el.style.background = `radial-gradient(${o.shape || '85% 55% at 50% 42%'}, rgb(${m}) 0%, ${o.edge || o.base || '#050505'} 100%)`;
    el.style.opacity = o.cover ? E.out(seg(t, t0, t0 + (o.coverDur ?? 0.5)), 2) : 1;
  };

  // 6. Mask wipe reveal.
  RV.wipe = function (el, t, t0, dur = 0.8, dir = 'up') {
    const u = E.out(seg(t, t0, t0 + dur), 4) * 100, r = 100 - u;
    $(el).style.clipPath = { up: `inset(${r}% 0 0 0)`, down: `inset(0 0 ${r}% 0)`, left: `inset(0 0 0 ${r}%)`,
      right: `inset(0 ${r}% 0 0)`, iris: `circle(${u * 0.75}% at 50% 50%)` }[dir];
  };

  // 7. Fake turntable for a flat cutout: keep within +-8 deg or the flatness shows.
  RV.turn = (t, t0, dur, from = -7, to = 7) => lerp(from, to, E.inOut(seg(t, t0, t0 + dur)));

  // 8. Spec counter: digits count up with a cubic ease-out, tabular and zero-padded to the final width.
  // The number is a TRUE value from the pack or the brief. audio.py places a tick on every integer step.
  RV.counter = function (el, t, t0, dur, to, o = {}) {
    el = $(el); const dec = o.dec ?? 0, from = o.from ?? 0;
    const v = lerp(from, to, E.out(seg(t, t0, t0 + dur), 3)), s = v.toFixed(dec), pad = to.toFixed(dec).length;
    el.textContent = (o.pad === false ? s : s.padStart(pad, '0'));
  };

  // 9. Measured narrow band: scan the cutout's alpha and return the y (fraction of its height) where the
  // silhouette is narrowest between fractions a..b. The name lockup that passes BEHIND the product sits there, so the
  // product hides the fewest letters. Must be called after the image is decoded.
  RV.narrowBand = function (img, a = 0.08, b = 0.6) {
    const c = document.createElement('canvas'), w = 200, h = Math.round(200 * img.naturalHeight / img.naturalWidth);
    c.width = w; c.height = h; const g = c.getContext('2d'); g.drawImage(img, 0, 0, w, h);
    const d = g.getImageData(0, 0, w, h).data, rows = [];
    for (let y = 0; y < h; y++) {
      let l = -1, r = -1;
      for (let x = 0; x < w; x++) if (d[(y * w + x) * 4 + 3] > 40) { if (l < 0) l = x; r = x; }
      rows.push(l < 0 ? 0 : (r - l) / w);
    }
    let i0 = Math.round(a * h), bi = i0;
    for (let y = i0; y < Math.round(b * h); y++) if (rows[y] > 0 && (rows[bi] === 0 || rows[y] < rows[bi])) bi = y;
    let lo = bi, hi = bi;                                   // the whole narrow run (within 15%), then its centre
    while (lo > 0 && rows[lo - 1] > 0 && rows[lo - 1] <= rows[bi] * 1.15) lo--;
    while (hi < h - 1 && rows[hi + 1] > 0 && rows[hi + 1] <= rows[bi] * 1.15) hi++;
    const best = { y: (lo + hi + 1) / 2 / h, wd: rows[bi], from: lo / h, to: (hi + 1) / h, rows };
    return best;   // {y, wd}: band centre and silhouette width, both as fractions
  };

  // mean silhouette width (fraction of the image width) between heights a..b (fractions): how much of a line the
  // product hides when the line spans that height
  RV.meanWidth = (band, a, b) => { const r = band.rows, i = Math.max(0, Math.floor(a * r.length)), j = Math.min(r.length, Math.ceil(b * r.length));
    let s = 0; for (let y = i; y < j; y++) s += r[y]; return j > i ? s / (j - i) : 0; };

  // 10. Pass: a line enters from o.from (px offset, sign = side) with motion blur, settles by t0 + inDur, drifts
  // o.drift px while held, and leaves to o.to after t1. Used for the name passing BEHIND the product.
  RV.pass = function (el, t, t0, t1, o = {}) {
    el = $(el); const inD = o.inDur ?? 0.55, outD = o.outDur ?? 0.3, from = o.from ?? 900, to = o.to ?? -900;
    const ui = E.out(seg(t, t0, t0 + inD), 5), uo = E.in(seg(t, t1, t1 + outD), 3);
    const x = from * (1 - ui) + (o.drift ?? -40) * seg(t, t0, t1) + to * uo;
    const v = from * 5 / inD * Math.pow(1 - seg(t, t0, t0 + inD), 4) / 30 + Math.abs(to) * 3 / outD * uo * uo / 30;   // px per frame
    set(el, { x, o: t >= t0 && t < t1 + outD ? 1 : 0 });
    if (o.blur !== false) K.mblur(el, Math.min(60, v * 0.35), 0);
  };

  // 11. Callout: dot pops on the real part, leader draws, value rises, label fades; one on screen at a time.
  RV.callout = function (el, t, t0, hold = 1.0) {
    el = $(el); const ln = el.querySelector('.rv-lead'), dot = el.querySelector('.rv-dot'),
      val = el.querySelector('.rv-val'), lab = el.querySelector('.rv-lab'), out = t0 + 0.4 + hold;
    if (ln) { const L = ln._len || (ln._len = Math.ceil(ln.getTotalLength())); ln.style.strokeDasharray = L;
      ln.style.strokeDashoffset = L * (1 - E.out(seg(t, t0 + 0.08, t0 + 0.43), 3)); }
    if (dot) set(dot, { s: E.back(seg(t, t0, t0 + 0.25)) });
    if (val) set(val, { y: 30 * (1 - E.out(seg(t, t0 + 0.25, t0 + 0.8))), o: seg(t, t0 + 0.25, t0 + 0.5) });
    if (lab) set(lab, { y: 12 * (1 - E.out(seg(t, t0 + 0.4, t0 + 0.85))), o: seg(t, t0 + 0.4, t0 + 0.7) });
    el.style.opacity = (t >= t0 ? 1 : 0) * (1 - seg(t, out, out + 0.2));
  };

  window.RV = RV;
})();
