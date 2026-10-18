#!/usr/bin/env python3
"""
Synthesize speech from a text file using the Chatterbox wrapper.

Usage examples:
  python scripts/synthesize_text_file.py \
    --text-file alice_page.txt \
    --conds "custom_output/chatterbox_voices/KpuEkonkuiU_2025 06 03 21 19 15.conds.pt" \
    --out custom_output/alice_page.wav

  python scripts/synthesize_text_file.py \
    --text-file alice_page.txt \
    --audio-prompt processed_segments/KpuEkonkuiU_2025 06 03 21 19 15_segment_0.wav \
    --out custom_output/alice_page.wav
"""

import argparse
import os
import re
from typing import List

import numpy as np
import soundfile as sf

from models.model_wrappers import ModelFactory


def chunk_text(text: str, max_len: int = 350) -> List[str]:
    """Split text into sentence groups, each no longer than max_len chars."""
    # Split on sentence boundaries
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    chunks, buf = [], ""
    for s in sentences:
        if len(buf) + len(s) + 1 <= max_len:
            buf = (buf + " " + s).strip()
        else:
            if buf:
                chunks.append(buf)
            buf = s
    if buf:
        chunks.append(buf)
    return [c for c in chunks if c]


def synthesize_chunks(chunks: List[str], conds_path: str = None, audio_prompt_path: str = None) -> np.ndarray:
    """Synthesize each chunk and concatenate to one waveform (22.05 kHz)."""
    w = ModelFactory.create_wrapper("chatterbox")
    w.load_model()

    audio_parts = []
    for i, chunk in enumerate(chunks, 1):
        y = w.synthesize(chunk, conds_path=conds_path, audio_prompt_path=audio_prompt_path)
        audio_parts.append(y)
        print(f"[chunk {i}/{len(chunks)}] len={len(y)/22050:.2f}s")

    if not audio_parts:
        return np.zeros(0, dtype=np.float32)
    return np.concatenate(audio_parts)


def main():
    p = argparse.ArgumentParser(description="Synthesize speech from a text file using Chatterbox")
    g_text = p.add_mutually_exclusive_group(required=True)
    g_text.add_argument("--text-file", type=str, help="Path to input UTF-8 text file")
    g_text.add_argument("--text", type=str, help="Raw text to synthesize")

    g_voice = p.add_mutually_exclusive_group()
    g_voice.add_argument("--conds", type=str, help="Path to a .conds.pt custom voice profile")
    g_voice.add_argument("--audio-prompt", type=str, help="Path to a reference WAV for one-off cloning")

    p.add_argument("--out", type=str, required=True, help="Output WAV path (will be 22.05 kHz)")
    p.add_argument("--max-len", type=int, default=350, help="Max characters per chunk (default: 350)")

    args = p.parse_args()

    if args.text_file:
        if not os.path.exists(args.text_file):
            raise FileNotFoundError(f"Text file not found: {args.text_file}")
        with open(args.text_file, "r", encoding="utf-8") as f:
            text = f.read().strip()
    else:
        text = (args.text or "").strip()
        if not text:
            raise ValueError("--text is empty")

    if not args.conds and not args.audio_prompt:
        print("[info] No conds or audio prompt provided -> using default voice.")

    chunks = chunk_text(text, max_len=args.max_len)
    print(f"Total chunks: {len(chunks)} | Estimated text chars: {len(text)}")

    y_all = synthesize_chunks(chunks, conds_path=args.conds, audio_prompt_path=args.audio_prompt)

    out_dir = os.path.dirname(args.out)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    sf.write(args.out, y_all, 22050)
    print(f"Saved {args.out} | seconds={len(y_all)/22050:.1f} | chunks={len(chunks)}")


if __name__ == "__main__":
    main()
