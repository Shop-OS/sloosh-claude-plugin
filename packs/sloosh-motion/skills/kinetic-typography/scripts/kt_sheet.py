#!/usr/bin/env python3
"""kt_sheet.py: fast QA of a type page BEFORE rendering every frame. Renders the page only at the times you ask for, composites
each still over its coded background exactly like edit.py (fields / plate, type, subject cut-out, punches, hits, grain) and
tiles a labelled contact sheet. Then LOOK at it (Read tool): overlaps, clipping, rail, wrong font, words off-centre.

  python3 <kinetic-typography>/scripts/kt_sheet.py <film> ui/kt_poster.html [t1,t2,...] [--out out/page_sheet.jpg] [--boxes]
Default times: two per scene (just after its last landing, and mid-hold), from tl.TYPE["kt"].
--boxes draws the engine's safe zone (green) on every still, and the vertical-feed rail (red) on 9:16."""
import math, os, sys, time

def main():
    film = os.path.abspath(sys.argv[1]); page = sys.argv[2]; args = sys.argv[3:]
    out = args[args.index("--out") + 1] if "--out" in args else "out/page_sheet.jpg"
    boxes = "--boxes" in args
    times = [float(x) for x in args[0].split(",")] if args and not args[0].startswith("--") else None
    os.chdir(film); sys.path.insert(0, os.path.join(film, "lib")); sys.path.insert(0, film)
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("Playwright is not installed. Ask the user before installing it and its browser (use a virtual environment).")
    import numpy as np, cv2
    import filmkit as fk, ktfield as kf, render_html as rh, tl
    fk.setup(tl.W, tl.H, tl.FPS)
    if times is None:
        times = []
        for s in kf.scenes(tl):
            a, b = s["t"]; last = max(s.get("beats") or [a])
            if s["move"] == "ticker": continue
            times += [round(min(b - 0.05, last + 0.45), 2), round(min(b - 0.02, (last + b) / 2 + 0.3), 2)]
        times = sorted(set(times))[:24]
    srv = rh.serve(film); url = f"http://127.0.0.1:{srv.server_address[1]}/{page}"
    bg = kf.Fields(tl.FIELDS, getattr(tl, "HAZES", None)); plate = kf.Plate(**tl.PLATE) if getattr(tl, "PLATE", None) else None
    finish = fk.Finish(contrast=False, vignette=0.25 if plate else 0, bloom=0, grain=getattr(tl, "GRAIN", 4.0)); Z = kf.zooms(tl)
    tiles = []; t0 = time.time()
    with sync_playwright() as p:
        br = p.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None, args=["--force-color-profile=srgb"]); pg = br.new_page(viewport={"width": tl.W, "height": tl.H})
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e))); pg.goto(url)
        for _ in range(600):
            if pg.evaluate("typeof window.render === 'function' && window.READY === true"): break
            if errs: sys.exit(f"page error: {errs[0]}")
            time.sleep(0.1)
        else: sys.exit("page never became ready")
        sz = pg.evaluate("window.KT && KT.safe") or {"l": 0, "r": tl.W, "top": 0, "bot": tl.H}     # the engine's own safe zone (after the ticker band)
        for t in times:
            pg.evaluate(f"window.render({t:.4f})"); pg.evaluate("new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")
            png = pg.screenshot(omit_background=True); o = cv2.imdecode(np.frombuffer(png, np.uint8), cv2.IMREAD_UNCHANGED)
            if o.shape[2] == 3: o = np.dstack([o, np.full(o.shape[:2], 255, np.uint8)])      # fully opaque frames come back as RGB
            img = plate.under(t) if plate and plate.on(t) else bg.render(t)
            a = o[..., 3:4].astype(np.float32) / 255.0; img = (img * (1 - a) + o[..., :3] * a).astype(np.uint8)
            if plate and plate.on(t): img = plate.front(img, t)
            img = kf.camera_hits(img, t, getattr(tl, "PUNCH", []), Z); img = fk.hits(img, t, tl.HITS); img = finish(img, fk.frame_of(t))
            if boxes:
                cv2.rectangle(img, (int(sz["l"]), int(sz["top"])), (int(sz["r"]), int(sz["bot"])), (0, 200, 0), 3)
                if sz.get("rail"): cv2.line(img, (int(sz["rail"]["x"]), int(sz["rail"]["y"])), (int(sz["rail"]["x"]), int(sz["bot"])), (0, 0, 230), 3)
            tw = int(360 * max(1.0, tl.W / tl.H)); sc = tw / tl.W; im = cv2.resize(img, (tw, int(tl.H * sc)), interpolation=cv2.INTER_AREA)     # wide frames get wider tiles
            cv2.rectangle(im, (0, 0), (92, 26), (0, 0, 0), -1); cv2.putText(im, f"{t:.2f}s", (6, 19), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            tiles.append(im)
        if errs: print("page errors:", errs[:3])
        br.close()
    srv.shutdown()
    if not tiles: sys.exit("kt_sheet.py: no stills to render (no non-ticker scenes and no times given)")
    cols = min(6 if tl.H >= tl.W else 3, len(tiles)); rows = math.ceil(len(tiles) / cols); th, tw = tiles[0].shape[:2]
    sheet = np.full((rows * th, cols * tw, 3), 24, np.uint8)
    for k, im in enumerate(tiles): sheet[(k // cols) * th:(k // cols + 1) * th, (k % cols) * tw:(k % cols + 1) * tw] = im
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True); cv2.imwrite(out, sheet, [cv2.IMWRITE_JPEG_QUALITY, 88])
    print(f"{len(times)} stills -> {out} ({time.time() - t0:.0f} s): {','.join(f'{t:g}' for t in times)}")

if __name__ == "__main__":
    main()
