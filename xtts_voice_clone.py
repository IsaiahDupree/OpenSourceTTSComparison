#!/usr/bin/env python3
"""
XTTS Voice Cloning - Local Installation
========================================
Installs and runs XTTS-v2 for high-quality voice cloning locally.

This script:
1. Installs TTS package (if needed)
2. Accepts XTTS model license automatically
3. Downloads the model
4. Runs voice cloning with your sample

Usage:
    python xtts_voice_clone.py "Your text" --voice sample.wav
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

# Ensure proper encoding
if sys.platform == "win32":
    os.system("")  # Enable ANSI
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

OUTPUT_DIR = Path("voice_clone_output")
OUTPUT_DIR.mkdir(exist_ok=True)

def log(msg: str, level: str = "INFO"):
    """Simple logging with timestamp."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    symbols = {"INFO": "[INFO]", "OK": "[OK]", "WARN": "[WARN]", "ERROR": "[ERROR]"}
    symbol = symbols.get(level, "[*]")
    print(f"[{timestamp}] {symbol} {msg}")

def install_tts():
    """Install TTS package if not already installed."""
    try:
        import TTS
        log("TTS package already installed", "OK")
        return True
    except ImportError:
        log("Installing TTS package...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "TTS", "--upgrade"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            log(f"Installation failed: {result.stderr[:200]}", "ERROR")
            return False
        log("TTS package installed", "OK")
        return True

def accept_xtts_tos():
    """Pre-accept XTTS TOS to avoid interactive prompt."""
    tos_marker = Path.home() / ".local" / "share" / "tts" / "xtts_v2_tos_accepted"
    tos_marker.parent.mkdir(parents=True, exist_ok=True)
    
    # Also set environment variable
    os.environ["COQUI_TOS_AGREED"] = "1"
    
    log("XTTS license accepted", "OK")

def clone_voice(text: str, speaker_wav: str, output_file: str, language: str = "en"):
    """Clone voice using XTTS-v2."""
    from TTS.api import TTS
    import torch
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    log(f"Using device: {device}")
    
    if device == "cuda":
        gpu_name = torch.cuda.get_device_name(0)
        gpu_mem = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        log(f"GPU: {gpu_name} ({gpu_mem:.1f} GB)")
    
    # Accept TOS
    accept_xtts_tos()
    
    log("Loading XTTS-v2 model (first run downloads ~2GB)...")
    log("This may take several minutes on first run...")
    
    try:
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        log("Model loaded", "OK")
    except Exception as e:
        log(f"Model loading failed: {e}", "ERROR")
        # Try fallback approach
        log("Trying alternative approach...")
        tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=True).to(device)
    
    log(f"Cloning voice from: {speaker_wav}")
    log(f"Generating: {text[:50]}..." if len(text) > 50 else f"Generating: {text}")
    
    tts.tts_to_file(
        text=text,
        file_path=output_file,
        speaker_wav=speaker_wav,
        language=language
    )
    
    if Path(output_file).exists():
        size_kb = Path(output_file).stat().st_size / 1024
        log(f"Audio saved: {output_file} ({size_kb:.1f} KB)", "OK")
        return True
    else:
        log("Output file not created", "ERROR")
        return False

def basic_tts(text: str, output_file: str, model: str = "tts_models/en/ljspeech/vits"):
    """Basic TTS without voice cloning."""
    from TTS.api import TTS
    import torch
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    log(f"Using device: {device}")
    
    log(f"Loading model: {model.split('/')[-1]}")
    tts = TTS(model).to(device)
    
    log(f"Generating: {text[:50]}..." if len(text) > 50 else f"Generating: {text}")
    
    tts.tts_to_file(text=text, file_path=output_file)
    
    if Path(output_file).exists():
        size_kb = Path(output_file).stat().st_size / 1024
        log(f"Audio saved: {output_file} ({size_kb:.1f} KB)", "OK")
        return True
    else:
        log("Output file not created", "ERROR")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="XTTS Voice Cloning - High Quality Neural TTS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Basic TTS (no cloning)
    python xtts_voice_clone.py "Hello world" --output hello.wav
    
    # Voice cloning (requires 6+ second WAV sample)
    python xtts_voice_clone.py "Hello in my voice" --voice sample.wav
    
    # Different language
    python xtts_voice_clone.py "Bonjour le monde" --voice sample.wav --language fr
        """
    )
    
    parser.add_argument("text", help="Text to synthesize")
    parser.add_argument("--voice", "-v", help="Voice sample WAV for cloning")
    parser.add_argument("--output", "-o", help="Output WAV file")
    parser.add_argument("--language", "-l", default="en", help="Language (default: en)")
    parser.add_argument("--model", "-m", default="vits", 
                        choices=["vits", "tacotron2", "glow-tts"],
                        help="TTS model for basic synthesis")
    
    args = parser.parse_args()
    
    # Install TTS if needed
    if not install_tts():
        log("Failed to install TTS package", "ERROR")
        sys.exit(1)
    
    # Set default output
    if not args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if args.voice:
            args.output = str(OUTPUT_DIR / f"cloned_{timestamp}.wav")
        else:
            args.output = str(OUTPUT_DIR / f"tts_{timestamp}.wav")
    
    log("=" * 50)
    log("XTTS VOICE CLONING")
    log("=" * 50)
    
    try:
        if args.voice:
            if not Path(args.voice).exists():
                log(f"Voice sample not found: {args.voice}", "ERROR")
                sys.exit(1)
            
            success = clone_voice(
                args.text,
                args.voice,
                args.output,
                args.language
            )
        else:
            # Map model names
            model_map = {
                "vits": "tts_models/en/ljspeech/vits",
                "tacotron2": "tts_models/en/ljspeech/tacotron2-DDC",
                "glow-tts": "tts_models/en/ljspeech/glow-tts",
            }
            success = basic_tts(args.text, args.output, model_map[args.model])
        
        if success:
            log("=" * 50)
            log("COMPLETE!", "OK")
            log(f"Play with: start {args.output}")
            log("=" * 50)
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        log("Cancelled by user", "WARN")
        sys.exit(130)
    except Exception as e:
        log(f"Error: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
