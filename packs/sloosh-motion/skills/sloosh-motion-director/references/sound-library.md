# Sound: the original score, the SFX, and a track the user supplies

**The default for every film is original audio made to the picture.** audio.py builds the music with ak.score and every sound effect with the synths in lib/audiokit.py. It places them from the same tl.py cues as the picture, then masters with ak.master to -14 LUFS and -2 dBTP. ak.mux keeps the final file at or under -1 dBTP. Nothing is downloaded and nothing is copied from a reference. This is the final sound, not a draft.

A music or SFX file from elsewhere enters a film **only when the user supplies it** and confirms that they have the rights to use it. Then follow section 3.

---

## 1. The score: ak.score(GENRE, BPM, LEN, DROP, KEY, breath=...)

Genres: phonk, trap, techno, house, luxury, cinematic and ambient. The score is arranged around tl.DROP: a sparse intro, a riser and a snare roll, silence in the breath, the full groove from the drop, and a tail.

Arrangement edits that follow the picture:

- ak.tape_stop: the slow-down before a drop
- ak.lowpass_region: under a UI section, so the clicks read
- ak.gap: the breath
- ak.duck: under every voice line

| Style | GENRE | BPM | KEY | Notes |
|---|---|---|---|---|
| Software walkthrough or feature | house or techno | 118-124 | C or Am | low-pass the bed under UI sections; keep it flat at 500 Hz under a BEFORE section |
| Product reveal | luxury (dark), house (clean), ambient into luxury (splash), techno or trap (tech) | 92-130 | Dm or F#m | restrained; an impact and a sub drop on the hero |
| Aura or velocity edit | phonk (cowbell lead, 808 glides) or trap | 130-150 | F#m | a tape stop before the drop |
| Glitch | techno | 120-130 | Am | an audio stutter on slams (repeat 60 ms slices of the bus) |
| Kinetic type | house, trap or cinematic | 95-128 | per brief | one impact per slam word |
| Morph | ambient into techno | 120-135 | per brief | a swell on each transition |
| Dot matrix | minimal techno | 125-135 | Am | a tick per row, one crisp click on the resolve |

---

## 2. SFX from lib/audiokit.py

Place every sound from the shared cue list with ak.place(bus, t, sig, gain_db). A whoosh starts 0.2-0.3 s before its cut, so that its peak lands on the cut. Impacts and clicks start on their frame.

| Sound | Call | Typical gain (dB) | Where |
|---|---|---|---|
| Whoosh | ak.whoosh(0.3 to 0.6) | -16 to -10 | every pre-drop cut, whips, a name passing |
| Riser | ak.riser(1.5 to 2.5) | -10 | ends exactly on DROP |
| Impact | ak.impact(0.9 to 2.2) | -9 to -4 | the drop, every slam word |
| Sub drop | ak.subdrop() | -6 | the drop (layer an impact so phone speakers carry it) |
| UI click | ak.click() | -14 | every cursor click (convert UI time with ui2t) |
| Pop | ak.pop(f) | -14 | tile and card drops, a spec ping (ak.pop(1300)) |
| Tick | ak.tick() | -20 to -16 | typed letters, counter steps, LED rows |
| Sparkle | ak.sparkle() | -12 | connect, logo and end-card moments |
| Shutter | ak.shutter() | -12 | duotone frames, freezes, the echo stack |
| Glitch | ak.glitch_sfx(0.12 to 0.25) | -12 | negative frames, glitch hits |
| Heartbeat | ak.heartbeat() | -10 | slow-motion beats in an aura edit |
| Swell | ak.swell(chord) | -15 | morph transitions, product actions |
| Tape stop | ak.tape_stop(bus, t, 0.32) | none | the slow-down before a drop |

**Level rules:**

- Hero hits sit level with the music peak. One hit may go 2 dB above it.
- Transition SFX sit 6-10 dB under the music. Micro SFX sit 12-18 dB under it.
- At most 2 sounds play at once.
- The voice sits 6-8 dB above the ducked bed (ak.duck with to=0.45).

---

## 3. Only when the user supplies a track

**Get the file in.** Never download a track. The user puts the file in the film's audio/ folder. Check the file size before you use it.

**Lock it to the grid:**

```bash
python3 <director>/scripts/beatmap.py audio/track.mp3 --film <LEN> --drop-at <DROP>
# prints the BPM, the drop time (drop_s) and the start offset; writes audio/track.beatmap.json
```

Then set USER_TRACK = "audio/track.mp3" and USER_DROP = <drop_s> in audio.py. audio.py trims the track so that its drop lands on tl.DROP. Set tl.BPM to the track's BPM (or re-time the cuts to its beats), so that the cuts stay on its beats. The SFX, the voice, the ducking and the master stay as in section 2.

**An SFX file from the user:** load it at ak.SR (ffmpeg -i in.mp3 -ar 48000 -ac 2 x.wav, then scipy.io.wavfile), and place it on its cue with ak.place like a synth.

**Rights:** the user confirms the licence of any track or SFX file that they supply, and that it covers the use (for example a paid ad). Do not judge a licence yourself. Log each supplied file in out/audio_credits.json (title, source, licence as the user states it, date). Never ship the raw file on its own, and never use a reference video's audio.

---

## 4. Checks

```bash
ffmpeg -i out/<name>_vN_final.mp4 -af ebur128=peak=true -f null - 2>&1 | tail -12   # -14 LUFS (plus or minus 1), true peak at or below -1
python3 <director>/scripts/qa.py out/<name>_vN_final.mp4                              # specs, loudness, clicks, frozen spans
```

Read the RMS report that ak.master prints. Look for silent gaps and for a bed that is too loud under UI. You cannot hear the mix: read the RMS report, then ask the user to listen.
