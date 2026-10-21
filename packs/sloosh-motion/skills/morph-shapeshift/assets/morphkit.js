/* morphkit.js v1.0: twist-free morph helpers for the morph-shapeshift style, as PURE functions of film time t.
 * Load after the core kit:  <script src="/lib/kit.js"></script><script src="/vendor/flubber.min.js"></script>
 *                           <script src="/lib/morphkit.js"></script>
 * Every call inside window.render(t) recomputes the frame from t: no GSAP, no timers, no state that depends on the
 * previous frame (caches only memoise geometry). Same t -> same frame, so render_html.py can render any frame alone.
 * Idea: every shape is the SAME number of points (128), sampled evenly by arc length, clockwise, starting at 12 o'clock.
 * Two such shapes morph point to point with no twist, no inside-out flip, no crossing. Logos are resampled and aligned.
 * flubber (vendored, MIT) is used for one-to-many / many-to-one morphs (shards -> logo) and stubborn silhouettes.
 */
(function () {
  const MK = {}, N0 = 128;
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x)), lerp = (a, b, u) => a + (b - a) * u;
  const seg = (t, a, b) => clamp((t - a) / (b - a));
  MK.seg = seg; MK.lerp = lerp; MK.clamp = clamp;
  // eases used by this style (morphs are expoInOut or p3InOut; entrances expoOut; exits p3In; one elastic for goo)
  MK.E = {
    expoInOut: u => { u = clamp(u); return u === 0 ? 0 : u === 1 ? 1 : u < .5 ? Math.pow(2, 20 * u - 10) / 2 : (2 - Math.pow(2, -20 * u + 10)) / 2; },
    expoOut: u => { u = clamp(u); return u === 1 ? 1 : 1 - Math.pow(2, -10 * u); },
    p3InOut: u => { u = clamp(u); return u < .5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2; },
    p3In: u => Math.pow(clamp(u), 3),
    back: (u, s = 1.6) => { u = clamp(u) - 1; return u * u * ((s + 1) * u + s) + 1; },
    elastic: (u, p = 0.45) => { u = clamp(u); return u === 0 || u === 1 ? u : Math.pow(2, -10 * u) * Math.sin((u - p / 4) * (2 * Math.PI) / p) + 1; },
    sine: u => 0.5 - 0.5 * Math.cos(Math.PI * clamp(u)),
  };
  MK.rng = function (seed) { let a = seed >>> 0; return function () { a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; };

  // ---------------------------------------------------------------- points <-> path
  MK.d = pts => "M" + pts.map(p => p[0].toFixed(2) + " " + p[1].toFixed(2)).join("L") + "Z";
  MK.resample = function (poly, n = N0) {                        // even arc-length resample of a closed polyline
    const sg = []; let L = 0;
    for (let i = 0; i < poly.length; i++) { const a = poly[i], b = poly[(i + 1) % poly.length], l = Math.hypot(b[0] - a[0], b[1] - a[1]); sg.push([a, b, l]); L += l; }
    const out = []; let si = 0, acc = 0;
    for (let k = 0; k < n; k++) { const s = (k / n) * L;
      while (si < sg.length - 1 && acc + sg[si][2] < s) { acc += sg[si][2]; si++; }
      const [a, b, l] = sg[si], u = l ? (s - acc) / l : 0; out.push([a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u]); }
    return out;
  };
  const SAMPLED = new Map();
  MK.sample = function (d, n = N0) {                             // any SVG path string -> n points (browser geometry)
    const key = n + "|" + d; if (SAMPLED.has(key)) return SAMPLED.get(key);
    let svg = document.getElementById("mk-sampler");
    if (!svg) { document.body.insertAdjacentHTML("beforeend", '<svg id="mk-sampler" width="0" height="0" style="position:absolute"><path/></svg>'); svg = document.getElementById("mk-sampler"); }
    const p = svg.querySelector("path"); p.setAttribute("d", d); const L = p.getTotalLength(), out = [];
    for (let k = 0; k < n; k++) { const q = p.getPointAtLength((k / n) * L); out.push([q.x, q.y]); }
    SAMPLED.set(key, out); return out;
  };
  // fit raw logo path(s) from ANY coordinate system: one shared bbox, longer side = size px, centred on (cx, cy)
  MK.fitAll = function (ds, cx, cy, size, n = N0) {
    const P = [].concat(ds).map(d => typeof d === "string" ? MK.sample(d, n) : d); let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
    P.forEach(pts => pts.forEach(([x, y]) => { x0 = Math.min(x0, x); y0 = Math.min(y0, y); x1 = Math.max(x1, x); y1 = Math.max(y1, y); }));
    const k = size / Math.max(x1 - x0, y1 - y0), mx = (x0 + x1) / 2, my = (y0 + y1) / 2;
    return P.map(pts => pts.map(([x, y]) => [cx + (x - mx) * k, cy + (y - my) * k]));
  };
  MK.fit = (d, cx, cy, size, n = N0) => MK.fitAll([d], cx, cy, size, n)[0];
  const area = P => { let s = 0; for (let i = 0; i < P.length; i++) { const a = P[i], b = P[(i + 1) % P.length]; s += a[0] * b[1] - b[0] * a[1]; } return s / 2; };
  MK.area = P => Math.abs(area(P));
  MK.align = function (A, B) {                                  // same winding + best cyclic start offset
    if (Math.sign(area(A)) !== Math.sign(area(B))) B = B.slice().reverse();
    const n = A.length; let best = 0, bestE = Infinity;
    for (let o = 0; o < n; o++) { let e = 0; for (let i = 0; i < n; i += 4) { const b = B[(i + o) % n]; e += (A[i][0] - b[0]) ** 2 + (A[i][1] - b[1]) ** 2; }
      if (e < bestE) { bestE = e; best = o; } }
    return B.slice(best).concat(B.slice(0, best));
  };

  // ---------------------------------------------------------------- shape generators (n points, clockwise, 12 o'clock start)
  MK.roundRect = function (cx, cy, w, h, r, n = N0) {
    r = Math.max(0.01, Math.min(r, w / 2, h / 2)); const x0 = cx - w / 2, y0 = cy - h / 2, x1 = cx + w / 2, y1 = cy + h / 2, poly = [];
    const arc = (ax, ay, a0) => { for (let i = 0; i <= 8; i++) { const a = a0 + (i / 8) * (Math.PI / 2); poly.push([ax + r * Math.cos(a), ay + r * Math.sin(a)]); } };
    poly.push([cx, y0]); arc(x1 - r, y0 + r, -Math.PI / 2); arc(x1 - r, y1 - r, 0); arc(x0 + r, y1 - r, Math.PI / 2); arc(x0 + r, y0 + r, Math.PI);
    return MK.resample(poly, n);
  };
  MK.circle = (cx, cy, r, n = N0) => { const o = []; for (let k = 0; k < n; k++) { const a = -Math.PI / 2 + (k / n) * Math.PI * 2; o.push([cx + r * Math.cos(a), cy + r * Math.sin(a)]); } return o; };
  MK.polygon = function (cx, cy, r, sides, o = {}) {           // regular polygon / star (o.inner 0..1), o.round softens corners
    const rot = ((o.rot || 0) * Math.PI) / 180, k = o.inner ? sides * 2 : sides, poly = [];
    for (let i = 0; i < k; i++) { const rr = o.inner && i % 2 ? r * o.inner : r, a = -Math.PI / 2 + rot + (i / k) * Math.PI * 2; poly.push([cx + rr * Math.cos(a), cy + rr * Math.sin(a)]); }
    return MK.resample(o.round ? MK.roundCorners(poly, o.round) : poly, o.n || N0);
  };
  MK.roundCorners = function (poly, rad, steps = 6) {
    const out = [];
    for (let i = 0; i < poly.length; i++) { const p = poly[(i - 1 + poly.length) % poly.length], c = poly[i], q = poly[(i + 1) % poly.length];
      const v1 = [p[0] - c[0], p[1] - c[1]], v2 = [q[0] - c[0], q[1] - c[1]], l1 = Math.hypot(...v1), l2 = Math.hypot(...v2), t = Math.min(rad, l1 / 2, l2 / 2);
      const a = [c[0] + (v1[0] / l1) * t, c[1] + (v1[1] / l1) * t], b = [c[0] + (v2[0] / l2) * t, c[1] + (v2[1] / l2) * t];
      for (let s = 0; s <= steps; s++) { const u = s / steps; out.push([(1 - u) ** 2 * a[0] + 2 * (1 - u) * u * c[0] + u * u * b[0], (1 - u) ** 2 * a[1] + 2 * (1 - u) * u * c[1] + u * u * b[1]]); } }
    return out;
  };
  // organic blob: 3 seeded sine lobes; phase 0..1 per loop (integer loops are seamless)
  MK.blob = function (cx, cy, r, seed = 1, o = {}) {
    const R = MK.rng(seed), amp = o.amp ?? 0.1, n = o.n || N0, ph = (o.phase || 0) * Math.PI * 2;
    const L = [2, 3, 5].map((k, i) => ({ k, a: amp / (i + 1), p: R() * Math.PI * 2, s: i % 2 ? -1 : 1 })), out = [];
    for (let j = 0; j < n; j++) { const a = -Math.PI / 2 + (j / n) * Math.PI * 2; let m = 1;
      L.forEach(l => { m += l.a * Math.sin(l.k * a + l.p + l.s * ph * (l.k === 5 ? 1 : 2)); }); out.push([cx + r * m * Math.cos(a), cy + r * m * Math.sin(a)]); }
    return out;
  };
  // shards: a seeded triangulated grid covering box {x,y,w,h} -> triangle point lists
  MK.shards = function (box, cols = 4, rows = 3, seed = 9, jitter = 0.4) {
    const R = MK.rng(seed), P = [];
    for (let j = 0; j <= rows; j++) for (let i = 0; i <= cols; i++) { const edge = i === 0 || j === 0 || i === cols || j === rows;
      P.push([box.x + (i / cols) * box.w + (edge ? 0 : (R() - .5) * jitter * box.w / cols), box.y + (j / rows) * box.h + (edge ? 0 : (R() - .5) * jitter * box.h / rows)]); }
    const T = [], id = (i, j) => j * (cols + 1) + i;
    for (let j = 0; j < rows; j++) for (let i = 0; i < cols; i++) { const a = P[id(i, j)], b = P[id(i + 1, j)], c = P[id(i + 1, j + 1)], d = P[id(i, j + 1)];
      if ((i + j) % 2) T.push([a, b, c], [a, c, d]); else T.push([a, b, d], [b, c, d]); }
    return T;
  };
  MK.box = (cx, cy, w, h, r) => ({ cx, cy, w, h, r });
  const isBox = s => s && !Array.isArray(s) && typeof s === "object" && "w" in s;
  const PTS = new WeakMap();
  const toPts = (s, n = N0) => { if (typeof s === "string") return MK.sample(s, n); if (isBox(s)) { if (!PTS.has(s)) PTS.set(s, MK.roundRect(s.cx, s.cy, s.w, s.h, s.r, n)); return PTS.get(s); } return s; };
  MK.pts = toPts;

  // ---------------------------------------------------------------- pure morphs (u = eased progress 0..1)
  // box morph: interpolate the PARAMETERS, so every in-between is a true rounded rect
  MK.boxAt = function (A, B, u, o = {}) {
    const k = Math.sin(Math.PI * u) * (o.squash || 0), w = lerp(A.w, B.w, u), h = lerp(A.h, B.h, u), wide = B.w - A.w >= B.h - A.h;
    const W = w * (wide ? 1 + k : 1 - k * .8), H = h * (wide ? 1 - k * .8 : 1 + k);
    return { cx: lerp(A.cx, B.cx, u), cy: lerp(A.cy, B.cy, u), w: W, h: H, r: lerp(Math.min(A.r, A.w / 2, A.h / 2), Math.min(B.r, B.w / 2, B.h / 2), u) };
  };
  const ALIGNED = new Map();
  MK.alignedPair = function (A, B, n = N0) {                    // memoised: align B to A once per pair
    const a = toPts(A, n); let key = A, m = ALIGNED.get(key); if (!m) { m = new Map(); ALIGNED.set(key, m); }
    if (!m.has(B)) m.set(B, MK.align(a, toPts(B, n))); return [a, m.get(B)];
  };
  // twist-free point morph; o.rotate = degrees of arc that peaks mid-morph and returns to 0 (the end state stays exact)
  MK.ptsAt = function (A, B, u, o = {}) {
    const [a, b] = MK.alignedPair(A, B, o.n || N0), s = o.rotate ? Math.sin(Math.PI * u) * o.rotate * Math.PI / 180 : 0;
    let cx = 0, cy = 0; if (s) { a.forEach((q, i) => { cx += q[0] + b[i][0]; cy += q[1] + b[i][1]; }); cx /= 2 * a.length; cy /= 2 * a.length; }
    const cs = Math.cos(s), sn = Math.sin(s);
    return a.map((q, i) => { let x = lerp(q[0], b[i][0], u), y = lerp(q[1], b[i][1], u);
      if (s) { const dx = x - cx, dy = y - cy; x = cx + dx * cs - dy * sn; y = cy + dx * sn + dy * cs; } return [x, y]; });
  };
  // flubber interpolators, memoised per pair (flubber handles very different silhouettes; MK.ptsAt is the twist-free default)
  const FLUB = new Map();
  MK.flub = function (A, B, o = {}) {
    const key = A, k2 = B; let m = FLUB.get(key); if (!m) { m = new Map(); FLUB.set(key, m); }
    if (!m.has(k2)) { const f = x => typeof x === "string" ? x : toPts(x); m.set(k2, flubber.interpolate(f(A), f(B), { maxSegmentLength: o.seg || 4, string: true })); }
    return m.get(k2);
  };
  const COMB = new Map();
  MK.combine = function (pieces, target, o = {}) {              // many shapes -> one (shards -> logo); returns [interp per piece]
    if (!COMB.has(pieces)) COMB.set(pieces, flubber.combine(pieces.map(p => toPts(p).map(q => [q[0], q[1]])), typeof target === "string" ? target : toPts(target), { single: false, maxSegmentLength: o.seg || 4 }));
    return COMB.get(pieces);
  };
  const SEP = new Map();
  MK.separate = function (source, pieces, o = {}) {             // one shape -> many (logo -> shards)
    if (!SEP.has(pieces)) SEP.set(pieces, flubber.separate(typeof source === "string" ? source : toPts(source), pieces.map(p => toPts(p).map(q => [q[0], q[1]])), { single: false, maxSegmentLength: o.seg || 4 }));
    return SEP.get(pieces);
  };

  // ---------------------------------------------------------------- the chain: one shape through many states, pure in t
  // keys: [[t0, shape0], [t1, shape1, {dur, ease, rotate, squash, via:'flub'}], ...]. Key i morphs from shape i-1
  // starting at t_i over dur (default 0.5 s) and then holds until the next key. Shapes: MK.box objects, point arrays or
  // path strings. Box -> box uses the parameter morph; anything else the aligned point morph (or flubber with via:'flub').
  // Returns {d, i, u, shape}: the path, the index of the current target, eased progress 0..1 of that morph.
  MK.chain = function (t, keys, def = {}) {
    let i = 0; while (i + 1 < keys.length && t >= keys[i + 1][0]) i++;
    if (i === 0) { const s = keys[0][1]; return { d: MK.d(toPts(s)), i: 0, u: 1, shape: s }; }
    const [ti, B, o0] = keys[i], o = Object.assign({}, def, o0 || {}), A = keys[i - 1][1], dur = o.dur ?? 0.5;
    const u = (o.ease || MK.E.expoInOut)(seg(t, ti, ti + dur));
    if (u >= 1) return { d: MK.d(toPts(B)), i, u: 1, shape: B };
    if (isBox(A) && isBox(B)) { const bx = MK.boxAt(A, B, u, o); return { d: MK.d(MK.roundRect(bx.cx, bx.cy, bx.w, bx.h, bx.r)), i, u, shape: bx }; }
    if (o.via === "flub") return { d: MK.flub(A, B, o)(u), i, u };
    return { d: MK.d(MK.ptsAt(A, B, u, o)), i, u };
  };
  // content handoff inside a morphing container: old content out over the first 30%, new content in over the last 40%
  MK.handoff = (t, at, dur = 0.5) => ({ out: 1 - seg(t, at - 0.02, at + 0.3 * dur), in: seg(t, at + 0.6 * dur, at + dur + 0.05) });

  // ---------------------------------------------------------------- life: anticipation, overshoot, colour, rings
  // anticipation squash against the coming change, then a back-ease settle -> {sx, sy}
  MK.anticipate = function (t, at, o = {}) {
    const a = o.amt ?? 0.18, d = o.dur ?? 0.12, s = o.settle ?? 0.45;
    if (t < at - d || t > at + s) return { sx: 1, sy: 1 };
    if (t < at) { const u = MK.E.p3InOut(seg(t, at - d, at)); return { sx: 1 - a * u, sy: 1 + a * u }; }
    const u = MK.E.back(seg(t, at, at + s)); return { sx: lerp(1 - a, 1, u), sy: lerp(1 + a, 1, u) };
  };
  MK.overshoot = (t, land, amt = 0.04) => t < land ? 1 : 1 + amt * Math.sin(Math.PI * Math.min(1, (t - land) / 0.5)) * Math.exp(-(t - land) / 0.25);
  MK.press = (t, at, amt = 0.05) => 1 - amt * Math.exp(-Math.pow((t - at) / 0.05, 2));   // click squash
  // perceptual colour (OKLCH, no muddy midpoint); colour LAGS the shape: from 20% to 90% of the morph
  MK.color = (from, to, u) => u <= 0 ? from : u >= 1 ? to : `color-mix(in oklch, ${to} ${(u * 100).toFixed(2)}%, ${from})`;
  MK.colorLag = (from, to, t, at, dur) => MK.color(from, to, MK.E.sine(seg(t, at + 0.2 * dur, at + 0.9 * dur)));
  // concentric rounded-square rings radiating from a click (the send morph): [{s, o, w}] per ring
  MK.rings = (t, t0, o = {}) => [...Array(o.n || 3)].map((_, k) => { const u = seg(t, t0 + k * (o.stagger ?? 0.08), t0 + k * (o.stagger ?? 0.08) + (o.dur ?? 0.7));
    return { s: lerp(1, o.scale || 3.2, MK.E.expoOut(u)), o: u > 0 && u < 1 ? (o.op ?? 0.9) * (1 - u) : 0, w: lerp(o.w || 6, 1, u) }; });
  // install a goo (metaball) filter once: blur + alpha threshold; std about 0.1-0.2 x blob radius
  MK.goo = function (id = "mk-goo", std = 16, svg = null) {
    if (document.getElementById(id)) return id;
    const host = svg || document.querySelector("svg"); const NS = "http://www.w3.org/2000/svg", f = document.createElementNS(NS, "filter");
    f.setAttribute("id", id); f.setAttribute("x", "-30%"); f.setAttribute("y", "-30%"); f.setAttribute("width", "160%"); f.setAttribute("height", "160%");
    f.innerHTML = `<feGaussianBlur in="SourceGraphic" stdDeviation="${std}" result="b"/><feColorMatrix in="b" mode="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 20 -9"/>`;
    let defs = host.querySelector("defs"); if (!defs) { defs = document.createElementNS(NS, "defs"); host.prepend(defs); } defs.appendChild(f); return id;
  };
  // load a traced logo (scripts/logo_to_path.py -> logo.json) and build it as an <svg> group, one <g> per colour layer
  MK.loadLogo = async function (url = "/ui/logo.json") { const L = await (await fetch(url)).json(); return L; };
  MK.logoSVG = function (L, cls = "mk-logo") {                  // returns inner SVG markup in the logo's own viewBox units
    return L.layers.map((ly, k) => `<g class="${cls}-l${k}" fill="${ly.color}">` + ly.parts.map((p, j) =>
      `<path data-k="${k}" data-j="${j}" d="${p.d}" fill-rule="evenodd"/>`).join("") + "</g>").join("");
  };
  window.MK = MK;
})();
