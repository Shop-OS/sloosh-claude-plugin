#!/usr/bin/env python3
"""clipfx.py — deterministic footage treatments with ffmpeg (for Sloosh-generated clips before they go into the edit).

Why: pixel effects on real footage (threshold flash, duotone, RGB split, grain, grade, speed ramp, freeze) are more
reliable as ffmpeg passes than as browser filters on <video>. Optional pre-treatment for a source clip (datamosh, pixel sort) before it goes into the edit.py cut list; most looks are filmkit tags.

Usage:
  python3 <director>/scripts/clipfx.py list
  python3 clipfx.py <treatment> in.mp4 out.mp4 [key=value ...]
  python3 clipfx.py hits in.mp4 out.mp4 times=1.2,2.4,3.0 kind=threshold frames=3   # flash a treatment on beat times
  python3 clipfx.py ramp in.mp4 out.mp4 at=1.0 slow=0.35 len=0.8                  # speed ramp: normal -> slow-mo -> normal (fps=30 default)
  python3 clipfx.py freeze in.mp4 out.mp4 at=1.5 hold=0.6                         # freeze-frame hit (fps=30 default)
  python3 clipfx.py conform in.mp4 out.mp4 w=1080 h=1920 fps=30                    # crop-fill + fps conform (do this first)
  python3 clipfx.py glitch in.mp4 out.mp4 mode=slices+rgb times=0.5,1.2 frames=4 amp=0.08 seed=3   # numpy glitch engine
  python3 clipfx.py datamosh a.mp4 b.mp4 out.mp4 len=0.6                          # real datamosh A->B (I-frame drop)

Glitch engine (glitch-fx skill): mode = one or more of  rgb slices blocks sort wave static scan tear  joined with '+'.
  times=… frames=N  -> only those windows (intensity decays across the N frames); omit times -> whole clip, constant.
  amp (0..1, fraction of width, default per mode), seed (int), px (rgb offset px), n (slice count), bs (block px),
  thr (sort luma threshold 0..255), cols (sort column fraction), wl (wave wavelength px), hz (wave phase speed),
  tint=RRGGBB (blocks/tear accent colour). Every frame is seeded from (seed, frame index): re-renders are identical.

All outputs: H.264, yuv420p, BT.709 tv range, CRF 16, no audio unless keep_audio=1.
"""
import shutil, subprocess, sys

FF = shutil.which("ffmpeg") or "ffmpeg"

# Each treatment returns an ffmpeg -vf filter string. Values tuned on 1080p; all are deterministic (seeded noise).
def _p(kv, k, d): return type(d)(kv.get(k, d))

TREATMENTS = {
    # 1-bit black/white (aura hit frame). t = cut level 0..255
    "threshold": lambda kv: f"format=gray,lutyuv=y='if(gt(val,{_p(kv,'t',128)}),255,0)',format=yuv420p",
    # Two-colour posterised duotone. dark/light as 0xRRGGBB
    "duotone": lambda kv: _duotone(kv.get("dark", "0b1bd6"), kv.get("light", "ffffff")),
    "invert": lambda kv: "negate",
    # Cool x-ray: invert of mono pushed to blue
    "xray": lambda kv: "format=gray,negate,format=yuv420p,colorchannelmixer=rr=0.15:gg=0.45:bb=0.95",
    # RGB split (chromatic). px = offset in pixels
    "rgbsplit": lambda kv: f"rgbashift=rh=-{_p(kv,'px',12)}:bh={_p(kv,'px',12)}:edge=smear",
    # Cinematic B/W with crushed blacks + grain
    "noir": lambda kv: f"format=gray,eq=contrast={_p(kv,'contrast',1.35)}:brightness=-0.03,noise=alls={_p(kv,'grain',14)}:allf=t,format=yuv420p,vignette=PI/4",
    # Teal/amber blockbuster-lite grade
    "tealamber": lambda kv: "colorbalance=rs=-0.06:gs=-0.01:bs=0.08:rh=0.08:gh=0.02:bh=-0.08,eq=contrast=1.12:saturation=1.05,vignette=PI/5",
    # Desaturated night green-teal
    "nightteal": lambda kv: "eq=saturation=0.55:contrast=1.15:brightness=-0.02,colorbalance=rs=-0.05:gs=0.03:bs=0.04,vignette=PI/4",
    # Film grain only (strength 6-20)
    "grain": lambda kv: f"noise=alls={_p(kv,'s',10)}:allf=t",
    # Posterise to few levels (pop/comic)
    "posterize": lambda kv: "lutrgb=r='floor(val/64)*64':g='floor(val/64)*64':b='floor(val/64)*64'",
    # VHS-ish: soft, chroma bleed, scanline darkening, grain
    "vhs": lambda kv: "scale=iw/2:ih/2,scale=iw*2:ih*2:flags=neighbor,chromashift=cbh=6:crh=-6,eq=saturation=1.3,noise=alls=12:allf=t,"
                      "geq=lum='lum(X,Y)*(0.85+0.15*mod(Y,3))':cb='cb(X,Y)':cr='cr(X,Y)'",
    # Selective colour: keep one hue, rest mono (hue in degrees, e.g. green 120, red 0)
    "selective": lambda kv: f"hue=s=1,colorhold=color=0x{kv.get('color','2fa84f')}:similarity={_p(kv,'sim',0.25)}:blend=0.1",
    # Light leak / bloom-ish glow for highlights
    "glow": lambda kv: "split[a][b];[b]gblur=sigma=18,eq=brightness=0.05[g];[a][g]blend=all_mode=screen:all_opacity=0.35",
    # Motion-smear (frame blend) for dreamy aura transitions
    "smear": lambda kv: f"tmix=frames={_p(kv,'n',4)}:weights='{' '.join(['1'] * _p(kv,'n',4))}'",
    # --- glitch-fx additions (fast ffmpeg filters) ---
    # CRT scanlines: dark 1-px line every `gap` px at `op` opacity (no geq: fast at 1080x1920)
    "scanlines": lambda kv: f"drawgrid=w=iw+10:h={_p(kv,'gap',4)}:t=1:c=black@{_p(kv,'op',0.35)}",
    # Thermal / false colour: turbo palette on luma
    "thermal": lambda kv: f"format=gray,format=yuv444p,pseudocolor=preset={kv.get('preset','turbo')},format=yuv420p",
    # Subtle permanent chromatic aberration (lens CA, not a hit): px <= 6 at 1080 wide
    "ca": lambda kv: f"rgbashift=rh=-{_p(kv,'px',4)}:bh={_p(kv,'px',4)}:rv={_p(kv,'v',0)}:edge=smear",
    # Mosaic / pixel block (pixel-mosaic transition): s = block size px
    "pixelate": lambda kv: f"pixelize=w={_p(kv,'s',32)}:h={_p(kv,'s',32)}",
    # Echo ghosting (flash-photo smear): blends n frames, last one strongest
    "echo": lambda kv: f"tmix=frames={_p(kv,'n',8)}:weights='{' '.join(str(i+1) for i in range(_p(kv,'n',8)))}'",
    # Fast VHS (no geq): half-res chroma blur + chroma shift + soft + noise + scanlines. Use for long clips.
    "vhslite": lambda kv: "scale=iw/2:ih:flags=bilinear,scale=iw*2:ih:flags=bilinear,chromashift=cbh=8:crh=-8,"
                          "eq=saturation=1.25:contrast=1.08:gamma=1.04,noise=c0s=10:c0f=t,"
                          "drawgrid=w=iw+10:h=3:t=1:c=black@0.22",
}

def _duotone(dark, light):
    d = [int(dark[i:i+2], 16) for i in (0, 2, 4)]; l = [int(light[i:i+2], 16) for i in (0, 2, 4)]
    expr = lambda c: f"{d[c]}+({l[c]}-{d[c]})*val/255"
    return f"format=gray,format=rgb24,lutrgb=r='{expr(0)}':g='{expr(1)}':b='{expr(2)}'"


# ---------------- glitch engine (numpy, deterministic per frame) ----------------
def _probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate",
                          "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip().split(",")
    n, d = out[2].split("/"); return int(out[0]), int(out[1]), float(n) / float(d)

def _hexrgb(h): h = h.lstrip("#"); return [int(h[i:i + 2], 16) for i in (0, 2, 4)]

def _glitch_frame(img, modes, k, rng, f, kv):
    """img uint8 HxWx3, k = intensity 0..1, rng = numpy Generator seeded per frame."""
    import numpy as np
    H, W, _ = img.shape; out = img.copy()
    for m in modes:
        if m == "rgb":
            px = int(round(float(kv.get("px", W * 0.012)) * k)) or 1
            dy = int(rng.integers(-2, 3)) if k > 0.5 else 0
            out[..., 0] = np.roll(np.roll(out[..., 0], -px, axis=1), dy, axis=0)
            out[..., 2] = np.roll(out[..., 2], px, axis=1)
        elif m == "slices":
            n = int(kv.get("n", 12)); amp = float(kv.get("amp", 0.08)) * W * k
            cuts = np.sort(rng.integers(0, H, n - 1)); edges = [0, *cuts.tolist(), H]
            for a, b in zip(edges[:-1], edges[1:]):
                if b - a < 2 or rng.random() > 0.42: continue
                sh = int(rng.uniform(-1, 1) * amp)
                band = np.roll(out[a:b], sh, axis=1)
                if rng.random() < 0.5:  # channel tear on some bands
                    band[..., 0] = np.roll(band[..., 0], int(sh * 0.15) + 3, axis=1)
                out[a:b] = band
        elif m == "blocks":
            bs = int(kv.get("bs", 48)); cover = float(kv.get("amp", 0.18)) * k
            nb = int((H // bs) * (W // bs) * cover); tint = _hexrgb(kv["tint"]) if "tint" in kv else None
            for _ in range(nb):
                by, bx = int(rng.integers(0, H // bs)) * bs, int(rng.integers(0, W // bs)) * bs
                w = bs * int(rng.integers(1, 5)); h = bs
                sy = int(np.clip(by + rng.integers(-3, 4) * bs, 0, H - h)); sx = int(np.clip(bx + rng.integers(-6, 7) * bs, 0, W - w))
                w = min(w, W - bx); src = img[sy:sy + h, sx:sx + w].copy()
                r = rng.random()
                if r < 0.25: src = src[..., ::-1]                      # channel swap
                elif r < 0.35 and tint is not None: src = (src * 0.35 + np.array(tint) * 0.65).astype(np.uint8)
                elif r < 0.45: src = (src // 64) * 64                  # posterised block
                out[by:by + h, bx:bx + w] = src[:, :w]
        elif m == "sort":  # pixel-sort-ish vertical drips of bright pixels
            thr = float(kv.get("thr", 150)); fr = float(kv.get("cols", 0.35)) * k
            lum = out @ np.array([0.2126, 0.7152, 0.0722])
            cols = rng.random(W) < fr
            decay = 1.0 - 1.0 / max(8.0, float(kv.get("len", 220)) * k)
            acc = np.zeros((W, 3)); accl = np.zeros(W); res = out.astype(np.float32)
            for y in range(H):
                bright = (lum[y] > thr) & cols
                accl = np.where(bright, np.maximum(accl * decay, lum[y]), accl * decay)
                acc = np.where(bright[:, None], np.maximum(acc * decay, res[y]), acc * decay)
                take = cols & (accl > lum[y] + 8)
                res[y][take] = acc[take]
            out = res.clip(0, 255).astype(np.uint8)
        elif m == "wave":  # sine row displacement
            amp = float(kv.get("amp", 0.04)) * W * k; wl = float(kv.get("wl", H / 6)); hz = float(kv.get("hz", 1.0))
            fps = float(kv.get("_fps", 30)); ph = 2 * np.pi * hz * f / fps
            shift = (amp * np.sin(2 * np.pi * np.arange(H) / wl + ph)).astype(int)
            xi = (np.arange(W)[None, :] - shift[:, None]) % W
            out = out[np.arange(H)[:, None], xi]
        elif m == "static":
            noise = rng.integers(0, 256, ((H + 1) // 2, (W + 1) // 2), dtype=np.uint8).repeat(2, 0).repeat(2, 1)[:H, :W, None]
            a = 0.75 * k; out = (out * (1 - a) + noise * a).astype(np.uint8)
            y0 = int(rng.integers(0, H)); out[y0:y0 + H // 12] = np.clip(out[y0:y0 + H // 12].astype(int) + 60, 0, 255)
        elif m == "scan":
            out[::3] = (out[::3] * (1 - 0.35 * max(k, 0.6))).astype(np.uint8)
        elif m == "tear":  # white/pink dash streaks + thin slice shifts
            tint = _hexrgb(kv.get("tint", "ffd6e6"))
            for _ in range(int(40 * k) + 4):
                y = int(rng.integers(0, H)); x = int(rng.integers(0, W)); ln = int(rng.integers(W // 30, W // 6)); t = int(rng.integers(2, 6))
                out[y:y + t, x:x + ln] = tint if rng.random() < 0.5 else (255, 255, 255)
            for _ in range(int(6 * k) + 1):
                y = int(rng.integers(0, H - 40)); h = int(rng.integers(6, 40))
                out[y:y + h] = np.roll(out[y:y + h], int(rng.integers(-W // 8, W // 8)), axis=1)
    return out

def glitch(src, dst, kv):
    import numpy as np
    W, H, fps = _probe(src); kv["_fps"] = fps
    modes = kv.get("mode", "slices+rgb").split("+"); seed = int(kv.get("seed", 7)); nfr = int(kv.get("frames", 4))
    wins = [int(round(float(t) * fps)) for t in kv["times"].split(",")] if kv.get("times") else None
    rd = subprocess.Popen([FF, "-v", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    wr = subprocess.Popen([FF, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", f"{fps}", "-i", "-",
                           *ENC, "-an", dst], stdin=subprocess.PIPE)
    f, size = 0, W * H * 3
    while True:
        buf = rd.stdout.read(size)
        if len(buf) < size: break
        img = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        k = 1.0 if wins is None else 0.0
        if wins is not None:
            for w0 in wins:
                if w0 <= f < w0 + nfr: k = max(k, 1.0 - 0.55 * (f - w0) / max(1, nfr - 1))  # decaying burst
        if k > 0: img = _glitch_frame(img, modes, k, np.random.default_rng([seed, f]), f, kv)
        wr.stdin.write(np.ascontiguousarray(img).tobytes()); f += 1
    wr.stdin.close(); wr.wait(); rd.wait()
    print(f"glitch: {f} frames, modes={modes}, windows={wins}")

def datamosh(a, b, dst, kv):
    """Real datamosh: encode A+B as one MPEG-4 Part 2 stream with no keyframes except at 0 and at the A/B cut,
    then drop the cut keyframe so B's motion vectors push A's pixels. len = seconds of mosh before snapping clean
    to B (0 = never snap)."""
    import os, tempfile
    tmp = tempfile.mkdtemp()
    try:
        _datamosh(a, b, dst, kv, tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def _datamosh(a, b, dst, kv, tmp):
    import os
    W, H, fps = _probe(a); da = probe_dur(a); ln = float(kv.get("len", 0.6))
    cat, mosh = os.path.join(tmp, "ab.avi"), os.path.join(tmp, "m.avi")
    run([FF, "-y", "-v", "error", "-i", a, "-i", b, "-filter_complex",
         f"[1:v]scale={W}:{H},fps={fps},setsar=1[bb];[0:v]fps={fps},setsar=1[aa];[aa][bb]concat=n=2:v=1:a=0[v]", "-map", "[v]",
         "-c:v", "mpeg4", "-q:v", str(kv.get("q", 2)), "-g", "100000", "-bf", "0", "-sc_threshold", "1000000000",
         "-force_key_frames", f"0,{da:.3f}", "-f", "avi", cat])
    run([FF, "-y", "-v", "error", "-i", cat, "-c", "copy", "-bsf:v", "noise=drop='key*gt(pts\\,0)'", mosh])
    if ln > 0:
        g = (f"[0:v]trim=0:{da + ln:.3f},setpts=PTS-STARTPTS,fps={fps}[m];[1:v]scale={W}:{H},fps={fps},setsar=1,trim={ln:.3f},"
             f"setpts=PTS-STARTPTS[c];[m][c]concat=n=2:v=1:a=0,format=yuv420p[v]")
        run([FF, "-y", "-v", "error", "-i", mosh, "-i", b, "-filter_complex", g, "-map", "[v]", *ENC, "-an", dst])
    else:
        run([FF, "-y", "-v", "error", "-i", mosh, "-vf", "format=yuv420p", *ENC, "-an", dst])

ENC = ["-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p",
       "-color_range", "tv", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-movflags", "+faststart"]

def run(args):
    print(" ".join(args)); subprocess.run(args, check=True)

def probe_dur(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path], capture_output=True, text=True).stdout
    return float(out.strip())

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"): print(__doc__); return
    cmd = sys.argv[1]
    if cmd == "list":
        for k in TREATMENTS: print(k)
        print("hits, ramp, freeze, conform, glitch (modes: rgb slices blocks sort wave static scan tear), datamosh a b out"); return
    if cmd == "datamosh":
        datamosh(sys.argv[2], sys.argv[3], sys.argv[4], dict(a.split("=", 1) for a in sys.argv[5:])); return
    src, dst = sys.argv[2], sys.argv[3]
    kv = dict(a.split("=", 1) for a in sys.argv[4:])
    audio = [] if kv.get("keep_audio") == "1" else ["-an"]
    if cmd in TREATMENTS:
        run([FF, "-y", "-v", "error", "-i", src, "-vf", TREATMENTS[cmd](kv), *ENC, *audio, dst])
    elif cmd == "glitch":
        glitch(src, dst, kv)
    elif cmd == "hits":
        # Apply a treatment only on short windows starting at each beat time.
        fps = float(kv.get("fps", 30)); n = int(kv.get("frames", 3)); kind = kv.get("kind", "threshold")
        times = [float(t) for t in kv["times"].split(",")]
        enable = "+".join(f"between(t,{t:.3f},{t + n / fps - 0.001:.3f})" for t in times)
        fx = TREATMENTS[kind](kv)
        graph = f"[0:v]split[a][b];[b]{fx},format=yuv420p[t];[a][t]overlay=enable='{enable}',format=yuv420p[v]"
        run([FF, "-y", "-v", "error", "-i", src, "-filter_complex", graph, "-map", "[v]", *ENC, *audio, dst])
    elif cmd == "ramp":
        at, slow, ln = float(kv.get("at", 1)), float(kv.get("slow", 0.35)), float(kv.get("len", 0.8))
        # three segments: normal, slowed (setpts stretch + frame interpolation), normal
        graph = (f"[0:v]trim=0:{at},setpts=PTS-STARTPTS[a];"
                 f"[0:v]trim={at}:{at + ln},setpts=(PTS-STARTPTS)/{slow},minterpolate=fps=60:mi_mode=blend[b];"
                 f"[0:v]trim={at + ln},setpts=PTS-STARTPTS[c];[a][b][c]concat=n=3:v=1:a=0,fps={int(kv.get('fps', 30))}[v]")
        run([FF, "-y", "-v", "error", "-i", src, "-filter_complex", graph, "-map", "[v]", *ENC, "-an", dst])
    elif cmd == "freeze":
        at, hold, r = float(kv.get("at", 1)), float(kv.get("hold", 0.5)), int(kv.get("fps", 30))   # fps: the clip's frame rate
        graph = f"[0:v]tpad=stop_mode=clone:stop_duration=0,loop=loop={int(hold * r)}:size=1:start={int(at * r)},setpts=N/{r}/TB[v]"
        run([FF, "-y", "-v", "error", "-r", str(r), "-i", src, "-filter_complex", graph, "-map", "[v]", *ENC, "-an", dst])
    elif cmd == "conform":
        w, h, fps = int(kv.get("w", 1080)), int(kv.get("h", 1920)), int(kv.get("fps", 30))
        vf = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps={fps},setsar=1"
        run([FF, "-y", "-v", "error", "-i", src, "-vf", vf, *ENC, *audio, dst])
    else:
        sys.exit(f"unknown treatment {cmd}; run: python3 <director>/scripts/clipfx.py list")

if __name__ == "__main__":
    main()
