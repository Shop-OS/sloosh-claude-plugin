#!/usr/bin/env python3
"""render_html.py: render an HTML page that exposes window.render(t) frame by frame.

The page builds UI, logos, type and transitions in code. window.render(t) sets every transform, opacity, blur and
colour for time t (no CSS animations, no real time), so any frame can be rendered exactly.

  python3 lib/render_html.py ui/overlay.html --dur 15 --out frames/type             # transparent PNG sequence
  python3 lib/render_html.py ui/walkthrough.html --dur 11 --scale 2 --out frames/ui  # 2x for push-ins (sharp at 2-2.8x)
  python3 lib/render_html.py ui/card.html --dur 4 --opaque --mp4 out/card.mp4        # opaque MP4 instead of PNGs
Options: --fps 30 --w 1080 --h 1920 (default: read from tl.json in the film root) --from 0 --jobs 2
The film folder is served over http://127.0.0.1, so pages can fetch('tl.json') and load fonts/images relatively.
Page contract: define window.render = (t) => {...}; optionally set window.READY = true when assets are decoded.
The server listens on 127.0.0.1 only and serves only the film folder (--root). The page loads nothing from the network.
Old PNG frames in the output folder are removed before a render; nothing else in it is touched.
Needs the playwright Python module and its Chromium browser. If they are missing, ask the user before installing.
"""
import argparse, functools, glob, http.server, json, os, socketserver, subprocess, sys, threading, time
try:
    from playwright.sync_api import sync_playwright
except ImportError:                       # checked when a render starts, so importing this module never exits
    sync_playwright = None
NO_PLAYWRIGHT = ("render_html.py: the playwright module is missing. Ask the user before installing it and its Chromium "
                 "browser, preferably in a virtual environment.")

def serve(root):
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a, **k): pass
    h = functools.partial(Quiet, directory=root)
    srv = socketserver.TCPServer(("127.0.0.1", 0), h); threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv

FAILED = []

def worker(url, frames, a, out_dir, browser_path):
    try:
        _worker(url, frames, a, out_dir, browser_path)
    except BaseException as e:            # a thread cannot exit the process: record the failure for main()
        FAILED.append(str(e) or e.__class__.__name__)

def _worker(url, frames, a, out_dir, browser_path):
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=browser_path or None, args=["--disable-gpu-vsync", "--force-color-profile=srgb"])
        pg = b.new_page(viewport={"width": a.w, "height": a.h}, device_scale_factor=a.scale)
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(url); t0 = time.time()
        while not pg.evaluate("typeof window.render === 'function' && (window.READY === undefined || window.READY === true)"):
            if time.time() - t0 > 120: b.close(); raise RuntimeError(f"page never became ready: {errs[:3]}")
            time.sleep(0.2)
        pg.evaluate("document.fonts.ready.then(()=>true)")
        for k in frames:
            t = a.start + k / a.fps
            pg.evaluate(f"window.render({t:.6f})")
            pg.evaluate("new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")
            pg.screenshot(path=os.path.join(out_dir, f"{k:05d}.png"), omit_background=not a.opaque)
        if errs: print("page errors:", errs[:3])
        b.close()

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("page"); ap.add_argument("--dur", type=float, required=True)
    ap.add_argument("--out", default=None); ap.add_argument("--fps", type=float); ap.add_argument("--w", type=int); ap.add_argument("--h", type=int)
    ap.add_argument("--scale", type=float, default=1.0); ap.add_argument("--from", dest="start", type=float, default=0.0)
    ap.add_argument("--opaque", action="store_true"); ap.add_argument("--mp4"); ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--root", default=".")
    a = ap.parse_args(); root = os.path.abspath(a.root)
    if sync_playwright is None: sys.exit(NO_PLAYWRIGHT)
    tl = {}
    if os.path.exists(os.path.join(root, "tl.json")):
        with open(os.path.join(root, "tl.json"), encoding="utf-8") as f: tl = json.load(f)
    a.fps = a.fps or tl.get("FPS", 30); a.w = a.w or tl.get("W", 1080); a.h = a.h or tl.get("H", 1920)
    out_dir = a.out or os.path.join(root, "frames", os.path.splitext(os.path.basename(a.page))[0])
    os.makedirs(out_dir, exist_ok=True)
    for old in glob.glob(os.path.join(out_dir, "[0-9][0-9][0-9][0-9][0-9].png")): os.remove(old)
    srv = serve(root); url = f"http://127.0.0.1:{srv.server_address[1]}/{os.path.relpath(os.path.abspath(a.page), root)}"
    n = int(round(a.dur * a.fps)); jobs = max(1, min(a.jobs, n))
    bp = os.environ.get("CHROME_PATH")   # optional: a specific Chromium; Playwright uses its own by default
    chunks = [list(range(n))[j::jobs] for j in range(jobs)]
    th = [threading.Thread(target=worker, args=(url, c, a, out_dir, bp)) for c in chunks]
    t0 = time.time(); [x.start() for x in th]; [x.join() for x in th]; srv.shutdown()
    if FAILED: sys.exit("render_html.py failed: " + "; ".join(FAILED[:3]))
    print(f"{n} frames -> {out_dir}  ({time.time() - t0:.0f} s, {a.w * a.scale:.0f}x{a.h * a.scale:.0f})")
    if a.mp4:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(a.fps), "-i", os.path.join(out_dir, "%05d.png"),
                        "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", a.mp4], check=True); print("mp4 ->", a.mp4)

if __name__ == "__main__":
    main()
