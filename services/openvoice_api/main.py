#!/usr/bin/env python3
"""
OpenVoice FastAPI service (GPU-enabled if available)

Endpoints:
- GET /health -> simple health and device info
- GET /languages -> supported language keys
- POST /clone (multipart/form-data)
    - fields: text, language (default EN_NEWEST), speed (float, default 1.0), reference_audio (file)
    - returns: audio/wav

Requires OpenVoice V2 checkpoints at OPENVOICE_CKPT_DIR (default: ./checkpoints_v2)
Directory layout must contain:
  - converter/config.json
  - converter/checkpoint.pth
  - base_speakers/ses/<speaker_key>.pth

Example run (after Docker build):
  curl -X POST \
    -F "text=Hello from OpenVoice" \
    -F "language=EN_NEWEST" \
    -F "speed=1.0" \
    -F "reference_audio=@resources/example_reference.mp3" \
    http://localhost:8811/clone --output output.wav
"""

import io
import os
import tempfile
from typing import Dict, Optional

import torch
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

# OpenVoice / Melo imports
from openvoice import se_extractor
from openvoice.api import ToneColorConverter
from melo.api import TTS

# Ensure soundfile is available for any potential reading/writing (converter writes files)
import soundfile as sf  # noqa: F401

app = FastAPI(title="OpenVoice API", version="0.1.0")

# Configuration via env
CKPT_DIR = os.getenv("OPENVOICE_CKPT_DIR", "checkpoints_v2")
ENCODE_MESSAGE = os.getenv("OPENVOICE_ENCODE_MESSAGE", "@MyShell")

# Limited known language keys per MeloTTS demo
SUPPORTED_LANGS = [
    "EN_NEWEST",  # newest English base model
    "EN",
    "ES",
    "FR",
    "ZH",
    "JP",
    "KR",
]

# Global state (initialized at startup)
DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"
CONVERTER: Optional[ToneColorConverter] = None


def _ckpt_path(*parts: str) -> str:
    return os.path.join(CKPT_DIR, *parts)


def _require_ckpts() -> None:
    if not os.path.exists(_ckpt_path("converter", "config.json")):
        raise FileNotFoundError(
            f"Missing {_ckpt_path('converter', 'config.json')}. Mount or download checkpoints_v2."
        )
    if not os.path.exists(_ckpt_path("converter", "checkpoint.pth")):
        raise FileNotFoundError(
            f"Missing {_ckpt_path('converter', 'checkpoint.pth')}. Mount or download checkpoints_v2."
        )
    if not os.path.isdir(_ckpt_path("base_speakers", "ses")):
        raise FileNotFoundError(
            f"Missing directory {_ckpt_path('base_speakers', 'ses')}. Mount or download checkpoints_v2."
        )


def _extract_se_with_fallback(audio_path: str, prefer_vad: bool = True):
    """Extract speaker embedding with VAD fallback for short clips."""
    if CONVERTER is None:
        raise HTTPException(status_code=503, detail="Converter not initialized")
    try:
        se, _ = se_extractor.get_se(audio_path, CONVERTER, vad=prefer_vad)
        return se
    except AssertionError as e:
        msg = str(e).lower()
        if "too short" in msg or "num_splits" in msg:
            se, _ = se_extractor.get_se(audio_path, CONVERTER, vad=False)
            return se
        raise HTTPException(status_code=400, detail=f"SE extraction failed: {e}")
    except Exception:
        se, _ = se_extractor.get_se(audio_path, CONVERTER, vad=False)
        return se


@app.on_event("startup")
def _startup() -> None:
    global CONVERTER
    _require_ckpts()
    # Initialize tone color converter
    cfg = _ckpt_path("converter", "config.json")
    ckpt = _ckpt_path("converter", "checkpoint.pth")
    conv = ToneColorConverter(cfg, device=DEVICE)
    conv.load_ckpt(ckpt)
    CONVERTER = conv


@app.get("/")
def root() -> Dict[str, str]:
    return {"name": "OpenVoice API", "status": "ok"}


@app.get("/health")
def health() -> Dict[str, object]:
    exists = {
        "config": os.path.exists(_ckpt_path("converter", "config.json")),
        "checkpoint": os.path.exists(_ckpt_path("converter", "checkpoint.pth")),
        "ses_dir": os.path.isdir(_ckpt_path("base_speakers", "ses")),
    }
    return {
        "cuda": torch.cuda.is_available(),
        "device": DEVICE,
        "checkpoints": exists,
        "ckpt_dir": os.path.abspath(CKPT_DIR),
        "converter_loaded": CONVERTER is not None,
    }


@app.get("/languages")
def languages() -> Dict[str, object]:
    return {"languages": SUPPORTED_LANGS}


@app.get("/voices")
def voices() -> Dict[str, object]:
    """List available base speaker SE files (from checkpoints).

    Returns lowercase hyphenated keys matching expected SES filenames.
    """
    ses_dir = _ckpt_path("base_speakers", "ses")
    voices = []
    if os.path.isdir(ses_dir):
        for name in os.listdir(ses_dir):
            if name.endswith(".pth"):
                voices.append(os.path.splitext(name)[0])
    return {"ses_dir": os.path.abspath(ses_dir), "voices": sorted(voices)}


@app.get("/speakers")
def speakers(language: str = "EN_NEWEST") -> Dict[str, object]:
    """List available MeloTTS speaker keys for a given language model."""
    if language not in SUPPORTED_LANGS:
        raise HTTPException(status_code=400, detail=f"Unsupported language '{language}'. Use one of {SUPPORTED_LANGS}")
    # Lightweight model init just to inspect spk2id
    model = TTS(language=language, device=DEVICE)
    speaker_ids: Dict[str, int] = model.hps.data.spk2id
    return {"language": language, "speakers": list(speaker_ids.keys())}


@app.post("/clone")
async def clone_voice(
    reference_audio: UploadFile = File(..., description="Reference voice sample (e.g., .wav/.mp3)"),
    text: str = Form(...),
    language: str = Form("EN_NEWEST"),
    speed: float = Form(1.0),
    speaker: Optional[str] = Form(None, description="Optional base speaker key (from Melo model)")
) -> StreamingResponse:
    if CONVERTER is None:
        raise HTTPException(status_code=503, detail="Converter not initialized")

    if language not in SUPPORTED_LANGS:
        raise HTTPException(status_code=400, detail=f"Unsupported language '{language}'. Use one of {SUPPORTED_LANGS}")

    # Persist uploaded reference to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(reference_audio.filename or "ref")[1]) as tmp_ref:
        ref_path = tmp_ref.name
        content = await reference_audio.read()
        tmp_ref.write(content)

    try:
        # Extract target speaker embedding (VAD fallback inside)
        tgt_se = _extract_se_with_fallback(ref_path)

        # Prepare Melo TTS model for the requested language
        model = TTS(language=language, device=DEVICE)
        speaker_ids: Dict[str, int] = model.hps.data.spk2id

        # Select speaker id and speaker key
        if speaker is not None and speaker in speaker_ids:
            spk_key = speaker
            spk_id = speaker_ids[spk_key]
        else:
            # default: first speaker
            spk_key = next(iter(speaker_ids.keys()))
            spk_id = speaker_ids[spk_key]

        # Generate base audio with Melo (first)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_base:
            base_wav = tmp_base.name
        model.tts_to_file(text, spk_id, base_wav, speed=speed)

        # Select src_se: prefer precomputed SES file; if missing, derive from base_wav
        ses_key = spk_key.lower().replace("_", "-")
        ses_dir = _ckpt_path("base_speakers", "ses")
        ses_path = _ckpt_path("base_speakers", "ses", f"{ses_key}.pth")
        if os.path.exists(ses_path):
            src_se = torch.load(ses_path, map_location=DEVICE)
        else:
            candidates = []
            if os.path.isdir(ses_dir):
                for name in os.listdir(ses_dir):
                    if name.endswith(".pth"):
                        candidates.append(name)
            if candidates:
                ses_path = os.path.join(ses_dir, sorted(candidates)[0])
                src_se = torch.load(ses_path, map_location=DEVICE)
            else:
                # No SES available; extract from base signal
                src_se = _extract_se_with_fallback(base_wav)

        # Run tone color conversion
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_out:
            out_wav = tmp_out.name

        CONVERTER.convert(
            audio_src_path=base_wav,
            src_se=src_se,
            tgt_se=tgt_se,
            output_path=out_wav,
            message=ENCODE_MESSAGE,
        )

        # Stream result
        audio_bytes = b""
        with open(out_wav, "rb") as f:
            audio_bytes = f.read()

        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/wav",
            headers={
                "Content-Disposition": "attachment; filename=output.wav"
            },
        )
    finally:
        # Best effort cleanup
        try:
            os.unlink(ref_path)
        except Exception:
            pass
        for p in [locals().get("base_wav"), locals().get("out_wav")]:
            if p and os.path.exists(p):
                try:
                    os.unlink(p)
                except Exception:
                    pass


@app.post("/convert")
async def convert_audio(
    reference_audio: UploadFile = File(..., description="Target voice reference (e.g., .wav/.mp3)"),
    audio_src: UploadFile = File(..., description="Source audio to convert (wav/mp3)"),
) -> StreamingResponse:
    if CONVERTER is None:
        raise HTTPException(status_code=503, detail="Converter not initialized")

    # Persist uploads
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(reference_audio.filename or "ref")[1]) as tmp_ref:
        ref_path = tmp_ref.name
        content = await reference_audio.read()
        tmp_ref.write(content)

    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_src.filename or "src")[1]) as tmp_src:
        src_path = tmp_src.name
        content2 = await audio_src.read()
        tmp_src.write(content2)

    try:
        # Embeddings with fallback
        tgt_se = _extract_se_with_fallback(ref_path)
        src_se = _extract_se_with_fallback(src_path)

        # Convert
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_out:
            out_wav = tmp_out.name

        CONVERTER.convert(
            audio_src_path=src_path,
            src_se=src_se,
            tgt_se=tgt_se,
            output_path=out_wav,
            message=ENCODE_MESSAGE,
        )

        # Stream
        with open(out_wav, "rb") as f:
            audio_bytes = f.read()
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=converted.wav"},
        )
    finally:
        # Cleanup
        for p in [locals().get("ref_path"), locals().get("src_path"), locals().get("out_wav")]:
            if p and os.path.exists(p):
                try:
                    os.unlink(p)
                except Exception:
                    pass
