#!/usr/bin/env python3
"""Merge whisper.cpp word timestamps with silencedetect boundaries into phrases.

usage: python3 vo_phrases.py <words.json> <silences.txt> <duration hh:mm:ss.xx> <offset_s> <out.json>

Phrase boundaries come from silences (more reliable than whisper token times); words are
assigned to the phrase whose interval contains their midpoint. Prints a timeline.ts block
with film-time values (VO time + offset) and the key word starts.
"""
import json
import re
import sys


def main():
    words_json, sil_txt, dur_s, offset, out = sys.argv[1:6]
    offset = float(offset)
    h, m, s = dur_s.split(":")
    dur = float(h) * 3600 + float(m) * 60 + float(s)
    data = json.load(open(words_json))
    words = []
    for seg in data.get("transcription", []):
        t = seg.get("text", "").strip()
        if not t:
            continue
        a = seg["offsets"]["from"] / 1000.0
        b = seg["offsets"]["to"] / 1000.0
        words.append({"w": t, "start": a, "end": b})
    sil = []
    cur = None
    for line in open(sil_txt):
        k, v = line.strip().split(": ")
        v = float(v)
        if k == "silence_start":
            cur = v
        elif k == "silence_end" and cur is not None:
            sil.append((cur, v))
            cur = None
    # speech intervals = complement of silences
    speech = []
    t = 0.0
    for a, b in sil:
        if a - t > 0.12:
            speech.append([t, a])
        t = b
    if dur - t > 0.12:
        speech.append([t, dur])
    phrases = []
    for a, b in speech:
        ws = [w for w in words if a - 0.05 <= (w["start"] + w["end"]) / 2 <= b + 0.05]
        if not ws:
            continue
        start = max(a, ws[0]["start"] - 0.05) if ws else a
        phrases.append({
            "text": " ".join(w["w"] for w in ws),
            "start": round(start, 3),
            "end": round(b, 3),
            "words": [{"w": w["w"], "start": round(w["start"], 3)} for w in ws],
        })
    json.dump({"duration": dur, "offset": offset, "phrases": phrases}, open(out, "w"), indent=2)
    print("// transcript: " + " ".join(w["w"] for w in words))
    print(f"// {len(phrases)} phrases, VO {dur:.2f}s, offset {offset}s — phrase TIMES come from silences (reliable);")
    print("// per-phrase text is approximate around pauses (whisper smears word times across them).")
    print(f"export const VO_OFFSET = {round(offset * 30)}; // frames at 30 fps")
    print("export const VO = {")
    for i, p in enumerate(phrases):
        key = re.sub(r"[^a-z0-9]+", "_", p["text"].lower()).strip("_")[:28] or f"p{i}"
        key = f"p{i:02d}_{key}"
        print(f"  {key}: {{ start: {p['start'] + offset:.3f}, end: {p['end'] + offset:.3f} }}, // ≈ \"{p['text']}\"")
    print("};")
    print(f"// film end of VO: {dur + offset:.3f}s = frame {round((dur + offset) * 30)}")
    print("// word starts (film s):")
    for p in phrases:
        print("//  " + "  ".join(f"{w['w']}@{w['start'] + offset:.2f}" for w in p["words"]))


if __name__ == "__main__":
    main()
