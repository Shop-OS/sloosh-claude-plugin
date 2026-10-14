#!/usr/bin/env python3
"""Summarise a launch-film project folder (and optionally an SFX library).

usage: python3 inventory.py <project_folder> [<sfx_folder>]

Prints audio durations, video codec/pixel-format/fps (flags clips that should be
transcoded with prep_video.sh), image sizes, documents and SVG logos.
"""
import json
import os
import subprocess
import sys

AUDIO = {".mp3", ".wav", ".m4a", ".aac", ".aif", ".aiff", ".flac", ".ogg"}
VIDEO = {".mp4", ".mov", ".m4v", ".webm", ".mkv"}
IMAGE = {".png", ".jpg", ".jpeg", ".webp"}
DOCS = {".pdf", ".md", ".txt", ".docx", ".csv"}


def probe(path):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", path], capture_output=True, text=True).stderr
    dur, streams = None, []
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("Duration:"):
            dur = line.split(",")[0].replace("Duration:", "").strip()
        if line.startswith("Stream #"):
            streams.append(line.split(": ", 1)[-1][:150])
    return dur, streams


def image_size(path):
    try:
        from PIL import Image
        with Image.open(path) as im:
            return f"{im.size[0]}x{im.size[1]}"
    except Exception:
        return "?"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    root = sys.argv[1]
    rows = {"audio": [], "video": [], "image": [], "docs": [], "svg": []}
    for dirpath, dirnames, files in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in {"node_modules", ".git", "out", "public", "src"}]
        for fn in sorted(files):
            p = os.path.join(dirpath, fn)
            rel = os.path.relpath(p, root)
            ext = os.path.splitext(fn)[1].lower()
            if ext in AUDIO:
                d, s = probe(p)
                rows["audio"].append((rel, d, s[0] if s else ""))
            elif ext in VIDEO:
                d, s = probe(p)
                v = next((x for x in s if x.startswith("Video")), "")
                flag = " ⚠ transcode (prep_video.sh)" if ("hevc" in v or "10le" in v or "prores" in v) else ""
                rows["video"].append((rel, d, v + flag))
            elif ext in IMAGE:
                rows["image"].append((rel, image_size(p)))
            elif ext == ".svg":
                rows["svg"].append((rel,))
            elif ext in DOCS:
                rows["docs"].append((rel,))
    for k, v in rows.items():
        print(f"\n## {k} ({len(v)})")
        for r in v:
            print("  " + " | ".join(str(x) for x in r if x))
    if len(sys.argv) > 2:
        sfx = sys.argv[2]
        cats = {}
        for dirpath, _, files in os.walk(sfx):
            n = sum(1 for f in files if os.path.splitext(f)[1].lower() in AUDIO)
            if n:
                cats[os.path.relpath(dirpath, sfx)] = n
        print("\n## sfx library")
        print(json.dumps(cats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
