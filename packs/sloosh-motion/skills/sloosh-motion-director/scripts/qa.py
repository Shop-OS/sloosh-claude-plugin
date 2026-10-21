#!/usr/bin/env python3
"""qa.py — watch the film before anyone else does. Writes into a qa/ folder next to the film (out/qa/ for out/<name>_final.mp4).

  python3 qa.py final.mp4                 -> contact.png (2 fps, time labels), phone360.png (1 fps @ 360 px), report.json:
                                             res / fps / duration / LUFS / true peak, cuts, flash frames, audio clicks, frozen spans
  python3 qa.py final.mp4 strip 6.2       -> 12 consecutive frames from t=6.0 s, labelled (check a fast move / transition seam)
  python3 qa.py final.mp4 at 1.0 4.5 9.8  -> full-res stills at those times (check text, logo, product fidelity)
Then open each image, look at it, and score it with the QA checklist in the director SKILL.md.
Sheets are tiled and labelled with OpenCV, so an ffmpeg build without the drawtext filter works too.
"""
import json, math, os, re, shutil, subprocess, sys
import cv2, numpy as np

FF = shutil.which("ffmpeg") or "ffmpeg"
FONT = cv2.FONT_HERSHEY_SIMPLEX

def sh(args, **kw):
    r = subprocess.run(args, capture_output=True, text=True, **kw)
    if r.returncode != 0 and args and args[0] == FF:            # say so: a missing sheet must never pass silently
        print("qa.py: ffmpeg failed:", (r.stderr.strip().splitlines() or ["(no message)"])[-1])
    return r

def probe(path):
    p = json.loads(sh(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path]).stdout or "{}")
    v = next((s for s in p.get("streams", []) if s["codec_type"] == "video"), None)
    if v is None: sys.exit(f"qa.py: no video stream in {path}")
    return p, v

def frames(path, w, h, vf="", ss=None, n=None):
    """yield w x h BGR frames decoded by ffmpeg (no drawtext or tile filter needed)"""
    cmd = [FF, "-v", "error"] + (["-ss", str(ss)] if ss is not None else []) + ["-i", path, "-vf", f"{vf}scale={w}:{h}:flags=area"]
    p = subprocess.Popen(cmd + (["-frames:v", str(n)] if n else []) + ["-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
    try:
        while True:
            b = p.stdout.read(w * h * 3)
            if len(b) < w * h * 3: break
            yield np.frombuffer(b, np.uint8).reshape(h, w, 3).copy()
    finally: p.stdout.close(); p.wait()

def tag(img, text):
    (tw, th), _ = cv2.getTextSize(text, FONT, 0.4, 1)
    cv2.rectangle(img, (0, 0), (tw + 8, th + 8), (0, 0, 0), -1); cv2.putText(img, text, (4, th + 4), FONT, 0.4, (0, 255, 255), 1, cv2.LINE_AA)

def tile(tiles, cols, out):
    if not tiles: print("qa.py: no frames decoded for", out); return False
    h, w = tiles[0].shape[:2]; rows = math.ceil(len(tiles) / cols); img = np.zeros((rows * h, cols * w, 3), np.uint8)
    for k, t in enumerate(tiles): r, c = divmod(k, cols); img[r * h:(r + 1) * h, c * w:(c + 1) * w] = t
    cv2.imwrite(out, img); return True

def size(v, w):
    return w, 2 * max(1, round(v["height"] * w / v["width"] / 2))

def sheet(path, v, out, fps, width, cols, label):
    """one image tiling the WHOLE film: the row count follows the duration, so nothing is cut off"""
    w, h = size(v, width); tiles = []
    for k, f in enumerate(frames(path, w, h, f"fps={fps},")):
        if label: tag(f, f"{k / fps:.1f}s")
        tiles.append(f)
    if tile(tiles, cols, out): print(f"sheet -> {out} ({cols}x{math.ceil(len(tiles) / cols)}, {fps} fps)")

def specs(path, p, v):
    a = [s for s in p["streams"] if s["codec_type"] == "audio"]
    num, den = map(int, v["r_frame_rate"].split("/"))
    rep = {"width": v["width"], "height": v["height"], "fps": round(num / den, 3), "duration": round(float(p["format"]["duration"]), 3),
           "pix_fmt": v.get("pix_fmt"), "audio": bool(a), "size_mb": round(os.path.getsize(path) / 1e6, 2)}
    if a:
        e = sh([FF, "-hide_banner", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"]).stderr
        summ = e[e.rfind("Summary:"):]
        m = re.search(r"I:\s+(-?[\d.]+) LUFS", summ); pk = re.search(r"Peak:\s+(-?[\d.]+) dBFS", summ)
        if m: rep["integrated_lufs"] = float(m.group(1))
        if pk: rep["true_peak_dbfs"] = float(pk.group(1))
    return rep

def frames_gray(path, size=160):
    raw = subprocess.run([FF, "-v", "quiet", "-i", path, "-vf", f"scale={size}:{size}:flags=area,format=gray", "-f", "rawvideo", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, size, size)    # area scaling averages film grain away

def motion(path, fps):
    """cuts (info), flashes (1-2 frames that jump away and back or between shots) and frozen spans"""
    fr = frames_gray(path).astype(np.float32); N = len(fr); D = np.abs(np.diff(fr, axis=0)); d = D.mean(axis=(1, 2)); h = max(2, int(fps // 2))
    noise = 1.4826 * np.median(D.reshape(len(D), -1), axis=1); del D                 # per-step grain level (robust MAD)
    big = [i for i in range(len(d)) if d[i] > max(2.0, 4 * np.median(d[max(0, i - h):i + h + 1]))]   # a jump far above the local motion
    groups = []
    for i in big:
        if groups and i - groups[-1][-1] <= 2: groups[-1].append(i)
        else: groups.append([i])
    cuts, flashes = [], []
    for g in groups:
        a, b = g[0], g[-1]
        if a == b: cuts.append(round((a + 1) / fps, 3)); continue
        back = np.abs(fr[b + 1] - fr[a]).mean() < 0.35 * min(d[a], d[b])          # the shot after looks like the shot before
        flashes.append({"t": round((a + 1) / fps, 3), "frames": b - a, "kind": "flash frame" if back else "flash cut", "diff": round(float(max(d[g])), 1)})
    n = max(3, int(round(fps))); k = max(1, int(round(fps / 8))); w = n - k + 1; m = max(2, w // 7); still = []
    for i in range(0, N - w + 1, k):                     # still = 3 averaged frame groups across ~1 s match (grain averages out, slow drift adds up)
        g0, g1, g2 = fr[i:i + m].mean(0), fr[i + (w - m) // 2:i + (w + m) // 2].mean(0), fr[i + w - m:i + w].mean(0)
        thr = max(4.0, 6 * float(np.median(noise[i:i + w - 1])) / math.sqrt(m))   # median over the window: one flash frame cannot inflate it
        if max((np.abs(g0 - g1) > thr).sum(), (np.abs(g0 - g2) > thr).sum()) <= 25: still.append(i)
    frozen = []
    for i in still:
        if frozen and i <= frozen[-1][1]: frozen[-1][1] = i + w
        else: frozen.append([i, i + w])
    frozen = [{"t": round(s / fps, 2), "len": round((e - s) / fps, 2), "end_hold": e >= N - k} for s, e in frozen]
    return cuts, flashes, frozen

def clicks(path, sr=48000):
    """audio clicks: a sample-level spike far above its own 10 ms surround (a hard splice, a missing fade). Drum hits, ticks and glitches pass."""
    raw = subprocess.run([FF, "-v", "quiet", "-i", path, "-vn", "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32).astype(np.float64)
    if len(x) < sr // 10: return []
    e = np.diff(x, 2) ** 2; n = len(e); C = np.r_[0, np.cumsum(e)]; i = np.arange(n)
    win = lambda r: C[np.clip(i + r + 1, 0, n)] - C[np.clip(i - r, 0, n)]
    ec = win(24) / 49; es = (win(480) - win(48)) / 864 + 1e-12          # +-0.5 ms core vs the 1-10 ms ring around it
    hit = np.nonzero((ec > 1e-5) & (ec > 100 * es))[0]; out = []
    for j in hit:
        if out and j - out[-1][0] < sr // 20:
            if ec[j] / es[j] > out[-1][1]: out[-1] = (out[-1][0], ec[j] / es[j])
        else: out.append((j, ec[j] / es[j]))
    return [{"t": round(float(j) / sr, 3), "ratio": int(r)} for j, r in out]

def main():
    if len(sys.argv) < 2 or not os.path.isfile(sys.argv[1]): sys.exit(__doc__)
    path = sys.argv[1]; q = os.path.join(os.path.dirname(os.path.abspath(path)), "qa"); os.makedirs(q, exist_ok=True)
    p, v = probe(path)
    if len(sys.argv) > 2 and sys.argv[2] == "strip":
        t = float(sys.argv[3]); ss = max(0.0, t - 0.2); o = os.path.join(q, f"strip_{t:.2f}.png"); w, h = size(v, 320); num, den = map(int, v["r_frame_rate"].split("/")); fps = num / den; tiles = []
        f0 = math.ceil(ss * fps - 1e-6)                  # -ss before -i lands on the first frame at or after ss
        for k, f in enumerate(frames(path, w, h, ss=ss, n=12)): tag(f, f"{(f0 + k) / fps:.2f}s f{f0 + k}"); tiles.append(f)
        if tile(tiles, 6, o): print(o)
        return
    if len(sys.argv) > 2 and sys.argv[2] == "at":
        for t in sys.argv[3:]:
            o = os.path.join(q, f"still_{float(t):.2f}.png"); sh([FF, "-v", "error", "-y", "-ss", t, "-i", path, "-frames:v", "1", o]); print(o)
        return
    rep = specs(path, p, v)
    portrait = rep["height"] > rep["width"]
    for f in ("contact.png", "phone360.png"):
        if os.path.exists(os.path.join(q, f)): os.remove(os.path.join(q, f))
    sheet(path, v, os.path.join(q, "contact.png"), 2, 180 if portrait else 320, 10 if portrait else 6, True)
    sheet(path, v, os.path.join(q, "phone360.png"), 1, 360, 6 if portrait else 4, False)
    cuts, flashes, frozen = motion(path, rep["fps"]); rep["cuts"] = cuts; rep["flashes"] = flashes; rep["frozen"] = frozen
    rep["clicks"] = clicks(path) if rep["audio"] else []
    checks = []
    if rep.get("audio") and "integrated_lufs" in rep and abs(rep["integrated_lufs"] + 14) > 1.5: checks.append("loudness off -14 LUFS")
    if rep.get("true_peak_dbfs", -9) > -1.0: checks.append("true peak above -1 dBTP (re-run audio.py on the edit)")
    bad = [z["t"] for z in frozen if not z["end_hold"]]
    if bad: checks.append(f"frozen ~1 s or more at {bad} s (only the final hold may freeze)")
    if rep["clicks"]: checks.append(f"audio clicks at {[c['t'] for c in rep['clicks'][:12]]} s (a splice or a sound with no fade)")
    rep["flags"] = checks
    with open(os.path.join(q, "report.json"), "w", encoding="utf-8") as f: json.dump(rep, f, indent=1)
    print(json.dumps({key: val for key, val in rep.items() if key not in ("cuts", "flashes")}, indent=1))
    print(f"cuts ({len(cuts)}):", cuts[:60]); print("flashes (look at each with strip):", flashes[:20]); print("->", q)

if __name__ == "__main__":
    main()
