# mixcli – Local, Key-Aware Auto-Mixtape

## Install

1) Install **FFmpeg** (PATH).  
2) Optionally install **keyfinder-cli** for high-accuracy key detection. :contentReference[oaicite:10]{index=10}  
3) `pip install -e .`

## Use

```bash
# analyze → plan → render
mixcli analyze ./Music ./analysis.json
mixcli plan ./analysis.json ./plan.json
mixcli render ./plan.json ./mix.wav --fade 10

# or one-shot
mixcli auto ./Music ./mix.wav
```

### Video overlay (optional)

```bash
# render audio + a synchronized MP4 overlay
mixcli render ./plan.json ./mix.wav --video --video-out ./mix.mp4 \
  --size 1280x720 --fps 30 --font "Arial"

# Windows: prefer --fontfile for reliability
mixcli render ./plan.json ./mix.wav --video --video-out ./mix.mp4 \
  --fontfile "C:\\Windows\\Fonts\\arial.ttf"

# one-shot with video
mixcli auto ./Music ./mix.wav --video --video-out ./mix.mp4
```

Notes:

- The video draws current/next track, key (incl. Camelot), BPM, stretch ratio, beat pulses, and crossfade progress.
- If your FFmpeg cannot find fonts by name, use `--fontfile` with an absolute path. On Windows, typical paths are in `C:\\Windows\\Fonts\\`.

## Why this works (and what you can tweak)

- Beat tracking & tempo: `librosa.beat.beat_track` uses a dynamic-programming method (onset strength → tempo estimation → beat picking). It’s battle-tested for DJ-friendly BPMs. (librosa.org)
- Key detection: KeyFinder (or keyfinder-cli) is a focused open-source tool for DJs, comparable in accuracy to paid tools; we call it if available, otherwise fall back to chroma-profile matching. (ibrahimshaath.co.uk, GitHub)
- Harmonic rules: we apply Camelot rules (same key, ±1 “hour,” or relative major/minor) to score transitions. (Mixed In Key, DJ.Studio | The Ultimate DAW for DJs)
- Time-stretch: prefer FFmpeg rubberband (if compiled) for hi-fi stretching; else chain atempo filters (0.5–2.0 per stage) to hit the desired BPM. (gensoft.pasteur.fr, Stack Overflow, Ubuntu Manpages)
- Crossfades: `acrossfade` gives clean, equal-power overlaps between tracks. (gensoft.pasteur.fr)

## Optional upgrades (drop-in later)

- Downbeats for cleaner entry/exit points: use madmom RNN downbeat trackers to snap transitions to bar lines. (madmom.readthedocs.io, cp.jku.at)
- Stems-aware transitions: pre-split with Demucs or Spleeter and crossfade vocals/drums selectively for pro-sounding blends. (GitHub)
- Energy modeling: compute RMS or spectral flux to avoid dropping energy mid-set.

If you want, I can tailor the planner (e.g., “always raise energy,” “keep BPM within ±3,” “prefer relative major to same key”) and add a tiny config file, but this will already make a legit, key-aware continuous mix from any folder of music.
