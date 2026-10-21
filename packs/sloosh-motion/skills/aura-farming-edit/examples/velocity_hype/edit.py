"""edit.py: the aura edit's ONE editor script (the Velocity Hype preset). A pure render(t).

  python3 edit.py                          -> out/<NAME>_vN.mp4 (next free version; never overwrites)
  python3 edit.py out/sheet.jpg 0.5,2,6.4  -> stills only (a 16-still sheet covers every section)

Layers, bottom to top:
  1. footage: 30 cut-list rows (14 generated clips + 2 stills), each with its own zoom path, focus and tag,
     the cut grammar on every cut, the beat punch + downbeat split from the drop to the lens look
  2. the face-flicker burst (aurakit.FaceFlicker) replaces the footage for one beat; the psych strobes before the drop
  3. type (frames/type, from ui/type.html), then whole-frame hits that hit the type too, then the finish and flashes
Needs lib/aurakit.py (scripts/new_aura_film.sh copies it into lib/).
Importing this file has no side effects: audio.py imports SHOTS from it. build() sets up the renderer.
"""
import glob, os, sys; sys.path.insert(0, "lib")
import filmkit as fk
import aurakit as au
import tl

B, D = tl.B, tl.DROP
EARLY = 1.0 / tl.FPS                         # cut one frame BEFORE the beat; the flash and hits peak on the beat
def b(n): return max(0.0, n * B - EARLY)     # beat n from the film start
def d(n): return D + n * B - (EARLY if n else 0.0)   # beat n from the drop (the drop itself is exact: the breath ends on it)

def C(n): return "clips/c%02d.mp4" % n       # c01..c14: generated clips, each animated from keyframe still k01..k14
def K(n): return "plates/k%02d.jpg" % n

# (start, end, source, in_point, speed, zoom_from, zoom_to, focus_x, focus_y, tags)
# in_point + used length stays inside each clip's clean window (first ~70%, max 3.5 s of a 5 s clip).
SHOTS = [
    # ---- HOOK + BUILD (cuts every 2 beats -> 1 -> 1/2): calm subject, the world speeding up
    (b(0),     b(2),     C(1),  0.2, 1.0, 1.00, 1.08, 0.50, 0.40, "leak"),            # 01 EYES: ECU, eyes lift to lens. VO "You were never loud."
    (b(2),     b(4),     C(2),  0.3, 1.0, 1.10, 1.00, 0.50, 0.45, ""),                # 02 GARAGE: wide walk-through
    (b(4),     b(5),     C(3),  0.5, 1.0, 1.15, 1.05, 0.50, 0.50, "punch"),           # 03 HELMET macro, light sweep
    (b(5),     b(6),     K(4),  0.0, 1.0, 1.05, 1.12, 0.50, 0.55, "warm"),            # 04 HANDS (still + handheld micro-rotation)
    (b(6),     b(8),     C(5),  0.4, 1.0, 1.00, 1.06, 0.50, 0.35, "ramp leak"),       # 05 POWER WALK low angle. LIGHTS / OUT. + shout
    (b(8),     b(9),     C(6),  0.8, 1.0, 1.06, 1.00, 0.45, 0.40, "teal"),            # 06 PROFILE, lateral slide
    (b(9),     b(10),    C(7),  0.6, 1.0, 1.00, 1.08, 0.50, 0.55, "smear"),           # 07 LAUNCH (machine, no face)
    (b(10),    b(10.5),  C(8),  1.0, 1.0, 1.10, 1.10, 0.50, 0.50, "bwflick"),         # 08 CROWD (world in motion)
    (b(10.5),  b(11),    C(3),  2.2, 1.0, 1.20, 1.10, 0.50, 0.45, "glitch"),          # 09 HELMET again, later window
    (b(11),    b(12),    C(9),  0.5, 1.0, 1.00, 1.10, 0.50, 0.50, "zblur leak"),      # 10 AERIAL corner
    # ---- TEASE + PSYCH + BREATH
    (b(12),    b(15),    C(1),  1.6, 1.0, 1.00, 1.14, 0.50, 0.40, ""),                # 11 EYES OPEN hold: announcer "Aura... farming."
    (b(15),    tl.T_BREATH, C(1), 3.0, 1.0, 1.14, 1.22, 0.50, 0.40, "hard"),          # 12 PSYCH: tape-stop strobe (render adds it)
    (tl.T_BREATH, D,     "black", 0.0, 1.0, 1.00, 1.00, 0.50, 0.50, "hard"),          # 13 the breath
    # ---- DROP: the one gesture, slowest ON the beat, then accelerating out
    (d(0),     d(2),     C(10), 0.6, 1.0, 1.12, 1.00, 0.50, 0.32, "velo punch shake leak"),  # 14 GESTURE: visor snaps down. PURE / AURA echo + shout
    # ---- DROP BODY: a cut on every beat or half-beat, a tag on each
    (d(2),     d(2.5),   C(8),  0.4, 1.0, 1.08, 1.00, 0.50, 0.50, "punch"),           # 15 (rows 15-18 sit under the echo: no faces)
    (d(2.5),   d(3),     C(4),  0.6, 1.0, 1.00, 1.10, 0.50, 0.55, "teal"),            # 16 HANDS clip
    (d(3),     d(3.5),   C(3),  1.4, 1.0, 1.25, 1.10, 0.50, 0.50, "red"),             # 17
    (d(3.5),   d(4),     C(9),  0.9, 1.0, 1.00, 1.10, 0.50, 0.50, "glitch"),          # 18
    (d(4),     d(5),     C(7),  1.6, 1.0, 1.10, 1.00, 0.50, 0.55, "shake"),           # 19 slam FULL + negative hit + shout "Full send!"
    (d(5),     d(6),     C(9),  1.8, 1.0, 1.00, 1.12, 0.50, 0.50, "smear"),           # 20 slam SEND. + red hit
    (d(6),     d(6.5),   C(6),  2.0, 1.0, 1.20, 1.08, 0.45, 0.40, "pink"),            # 21 PROFILE
    (d(6.5),   d(7),     C(11), 0.8, 1.0, 1.10, 1.00, 0.50, 0.35, "punch"),           # 22 PEAK: fist pump
    (d(7),     d(8),     C(2),  2.4, 1.0, 1.00, 1.08, 0.50, 0.45, "bwflick"),         # 23
    (d(8),     d(8.5),   C(12), 1.6, 1.0, 1.15, 1.05, 0.50, 0.40, "warm"),            # 24 threshold hit
    (d(8.5),   d(9),     C(10), 2.4, 1.0, 1.00, 1.12, 0.50, 0.32, "zblur"),           # 25
    (d(9),     d(10),    C(7),  2.8, 1.0, 1.06, 1.00, 0.50, 0.55, "ramp leak"),       # 26
    (d(10),    d(11),    K(1),  0.0, 1.0, 1.00, 1.00, 0.50, 0.40, "hard"),            # 27 FACE FLICKER (render replaces it)
    # ---- the calm-vs-chaos hold, then the lens-look ending
    (d(11),    d(16),    C(13), 0.5, 0.3, 1.00, 1.08, 0.50, 0.33, "leak"),            # 28 CALM-CHAOS at 30%: STAY / QUIET.
    (d(16),    d(17),    C(14), 0.3, 1.0, 1.08, 1.00, 0.50, 0.38, "ramp"),            # 29 LENS: the head turns (cut on action)
    (d(17),    tl.LEN,   C(14), 1.6, 1.0, 1.00, 1.06, 0.50, 0.38, "leak whiteout"),   # 30 LENS: the stare, held. End card.
]

# the face-flicker burst: 12 faces (source, time, zoom, focus_x, focus_y), one per frame, from approved clean windows
FACES = [(C(1), 0.6, 1.0, 0.5, 0.40), (C(14), 2.0, 1.5, 0.5, 0.36), (C(5), 1.0, 1.6, 0.5, 0.30), (C(11), 0.6, 1.3, 0.5, 0.34),
         (C(1), 2.2, 1.2, 0.5, 0.40), (C(6), 1.2, 1.6, 0.45, 0.36), (C(13), 1.0, 1.7, 0.5, 0.32), (C(10), 0.4, 1.4, 0.5, 0.32),
         (K(1), 0.0, 1.1, 0.5, 0.40), (C(14), 0.8, 1.9, 0.5, 0.37), (C(12), 0.8, 1.5, 0.5, 0.36), (C(1), 2.8, 1.35, 0.5, 0.40)]

TYPE_DIR = "frames/type"
TYPE_CMD = "python3 lib/render_html.py ui/type.html --dur %g --out frames/type --jobs 1" % tl.LEN

def type_overlay(sheet):
    """The type frames as an overlay. A sheet may run before the type is rendered (a picture-only structure check);
    the film never does."""
    if glob.glob(os.path.join(TYPE_DIR, "*.png")):
        return fk.Overlay(TYPE_DIR)
    if sheet:
        print("edit.py: no type frames in %s yet, so this sheet shows the picture only. Render the type with: %s"
              % (TYPE_DIR, TYPE_CMD))
        return None
    sys.exit("edit.py: no type frames in %s. Render them first: %s" % (TYPE_DIR, TYPE_CMD))

def build(sheet=False):
    """Set up filmkit and return render(t). Call it once, from the main block. sheet=True allows a sheet without type."""
    fk.setup(tl.W, tl.H, tl.FPS)
    cuts = fk.CutList(au.shots(SHOTS), beats=tl.BEATS, beat_punch=0.07, downbeat_split=14, fx_from=D, fx_to=tl.T_FLICK)  # calm hold + lens look stay calm
    flicker = au.FaceFlicker(FACES, start=d(10), dur=d(11) - d(10))   # exactly row 27
    finish = fk.Finish(vignette=0.6, bloom=0.55, grain=6)
    overlay = type_overlay(sheet)                # TYPE_CMD renders frames/type from ui/type.html

    def render(t):
        img = flicker.frame(t) if flicker.active(t) else cuts.render(t)
        if tl.T_PSYCH <= t < tl.T_BREATH: img = au.psych(img, t, tl.T_PSYCH, tl.T_BREATH)
        if overlay is not None: img = overlay.over(img, t)   # type on top of the picture
        img = au.hits(img, t, tl.HITS)           # whole-frame hits that also hit the type
        img = finish(img, fk.frame_of(t))        # contrast, vignette, bloom, grain
        if cuts.flash_now(t) and not flicker.active(t): img = fk.flash(img)
        return img
    return render

if __name__ == "__main__":
    fk.run(build(sheet=len(sys.argv) > 1 and sys.argv[1].endswith((".jpg", ".png"))), tl.LEN, tl.NAME)
