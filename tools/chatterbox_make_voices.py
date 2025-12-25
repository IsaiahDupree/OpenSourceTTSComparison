#!/usr/bin/env python3
"""
Build Chatterbox voice conditionals (conds.pt) from reference audio files.

- Loads Chatterbox via from_pretrained(device)
- For each audio file in input_dir, prepares conditionals and saves as <stem>.conds.pt
- Output directory defaults to custom_output/chatterbox_voices/

Usage:
  python tools/chatterbox_make_voices.py \
      --input-dir audio_samples \
      --output-dir custom_output/chatterbox_voices \
      --device auto \
      --exaggeration 0.5

After generating, you can synthesize with a voice by passing conds_path to ChatterboxWrapper.synthesize().
"""

import argparse
import logging
from pathlib import Path
from typing import List

import torch


def find_audio_files(root: Path, exts: List[str]) -> List[Path]:
    files = []
    for ext in exts:
        files.extend(root.rglob(f"*.{ext}"))
    return sorted(files)


def main():
    parser = argparse.ArgumentParser(description="Create Chatterbox voice conditionals from audio files")
    parser.add_argument("--input-dir", type=str, default="audio_samples", help="Directory of reference audio files")
    parser.add_argument("--output-dir", type=str, default="custom_output/chatterbox_voices", help="Directory to save *.conds.pt files")
    parser.add_argument("--device", type=str, default="auto", choices=["auto", "cuda", "cpu", "mps"], help="Device to run Chatterbox on")
    parser.add_argument("--exaggeration", type=float, default=0.5, help="Emotion/exaggeration level [0,1]")
    parser.add_argument("--extensions", type=str, default="wav,m4a,mp3,flac", help="Comma-separated audio extensions to include")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger("chatterbox_make_voices")

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.device == "auto":
        device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
    else:
        device = args.device

    exts = [e.strip().lstrip(".") for e in args.extensions.split(",") if e.strip()]
    audio_files = find_audio_files(input_dir, exts)
    if not audio_files:
        log.warning(f"No audio files with extensions {exts} found under {input_dir}")
        return

    try:
        import chatterbox
    except ImportError as e:
        log.error(f"Failed to import chatterbox: {e}")
        return

    log.info(f"Loading Chatterbox on device={device} ...")
    tts = chatterbox.ChatterboxTTS.from_pretrained(device)
    log.info("Chatterbox loaded.")

    for fpath in audio_files:
        try:
            log.info(f"Preparing conditionals from: {fpath}")
            # Let chatterbox handle audio loading/resampling internally
            tts.prepare_conditionals(str(fpath), exaggeration=args.exaggeration)

            stem = fpath.stem
            out_path = output_dir / f"{stem}.conds.pt"
            tts.conds.save(out_path)
            log.info(f"Saved: {out_path}")
        except Exception as e:
            log.error(f"Failed for {fpath}: {e}")
            continue

    log.info("Done.")


if __name__ == "__main__":
    main()
