#!C:\Users\Isaia\AppData\Local\Programs\Python\Python310\python.exe
"""
XTTS Voice Cloning - Based on Official Coqui Documentation
============================================================

Official installation and usage based on: https://docs.coqui.ai/en/dev/models/xtts.html

Features (XTTS-v2):
- Voice cloning from single audio file
- Cross-language voice cloning
- 16 languages: en, es, fr, de, it, pt, pl, tr, ru, nl, cs, ar, zh-cn, ja, hu, ko
- 24khz sampling rate
- Streaming inference with <200ms latency
- Fine-tuning support

Usage:
    # Install first
    pip install TTS
    
    # Then run this script
    python xtts_official_install.py --demo
    python xtts_official_install.py "Your text" --voice sample.wav
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Fix Windows encoding
if sys.platform == "win32":
    os.system("")
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

OUTPUT_DIR = Path("xtts_output")
OUTPUT_DIR.mkdir(exist_ok=True)

def log(msg: str, level: str = "INFO"):
    """Logging with timestamp."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    symbols = {"INFO": "[INFO]", "OK": "[OK]", "WARN": "[WARN]", "ERROR": "[ERROR]", "STEP": "[>>>]"}
    print(f"[{timestamp}] {symbols.get(level, '[*]')} {msg}")

def check_and_install_tts():
    """Check and install TTS package."""
    log("Checking TTS installation...")
    
    try:
        import TTS
        log(f"TTS version: {TTS.__version__}", "OK")
        return True
    except ImportError:
        log("TTS not installed. Installing now...")
        log("This may take 5-10 minutes on first install...", "WARN")
        
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "TTS"],
            capture_output=False  # Show real-time output
        )
        
        if result.returncode != 0:
            log("TTS installation failed", "ERROR")
            log("Try manually: pip install TTS", "WARN")
            return False
        
        log("TTS installed successfully", "OK")
        return True

def list_available_speakers():
    """List pre-trained Coqui speakers."""
    from TTS.api import TTS
    
    log("Loading XTTS-v2 to list speakers...")
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    
    if hasattr(tts, 'speakers') and tts.speakers:
        log(f"Available speakers: {len(tts.speakers)}")
        for speaker in tts.speakers[:10]:
            print(f"  - {speaker}")
        if len(tts.speakers) > 10:
            print(f"  ... and {len(tts.speakers) - 10} more")
    else:
        log("No pre-trained speakers found in this model")

def clone_voice(
    text: str,
    speaker_wav,  # str or list of str
    output_file: str,
    language: str = "en",
    use_gpu: bool = True,
    split_sentences: bool = True
):
    """
    Clone a voice using XTTS-v2.
    
    Based on official docs: https://docs.coqui.ai/en/dev/models/xtts.html#tts-api
    
    Args:
        text: Text to synthesize
        speaker_wav: Single path or list of paths to reference audio files
        output_file: Output WAV file path
        language: Language code (en, es, fr, de, it, pt, pl, tr, ru, nl, cs, ar, zh-cn, ja, hu, ko)
        use_gpu: Whether to use GPU acceleration
        split_sentences: Split text into sentences (better for long text)
    """
    from TTS.api import TTS
    import torch
    
    # Check device
    device = "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
    log(f"Using device: {device}")
    
    if device == "cuda":
        gpu_name = torch.cuda.get_device_name(0)
        vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        log(f"GPU: {gpu_name} ({vram:.1f} GB VRAM)")
    
    # Normalize speaker_wav to list
    if isinstance(speaker_wav, str):
        speaker_wav = [speaker_wav]
    
    # Validate speaker files
    for wav in speaker_wav:
        if not Path(wav).exists():
            log(f"Speaker file not found: {wav}", "ERROR")
            return False
    
    log(f"Reference audio files: {len(speaker_wav)}")
    for wav in speaker_wav:
        log(f"  - {Path(wav).name}")
    
    # Load model
    log("Loading XTTS-v2 model...")
    log("First run downloads ~2GB model - please wait...", "WARN")
    
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=use_gpu)
    log("Model loaded", "OK")
    
    # Generate speech
    log(f"Generating speech (language={language}, split={split_sentences})...")
    log(f"Text: \"{text[:80]}{'...' if len(text) > 80 else ''}\"")
    
    tts.tts_to_file(
        text=text,
        file_path=output_file,
        speaker_wav=speaker_wav,
        language=language,
        split_sentences=split_sentences
    )
    
    if Path(output_file).exists():
        size_kb = Path(output_file).stat().st_size / 1024
        log(f"Audio saved: {output_file} ({size_kb:.1f} KB)", "OK")
        return True
    else:
        log("Output file not created", "ERROR")
        return False

def use_builtin_speaker(
    text: str,
    speaker: str,
    output_file: str,
    language: str = "en",
    use_gpu: bool = True
):
    """
    Use a built-in Coqui speaker (no voice sample needed).
    
    Available speakers: Ana Florence, Claribel Dervla, Daisy Studious, etc.
    """
    from TTS.api import TTS
    
    log(f"Using built-in speaker: {speaker}")
    
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=use_gpu)
    
    tts.tts_to_file(
        text=text,
        file_path=output_file,
        speaker=speaker,
        language=language,
        split_sentences=True
    )
    
    if Path(output_file).exists():
        size_kb = Path(output_file).stat().st_size / 1024
        log(f"Audio saved: {output_file} ({size_kb:.1f} KB)", "OK")
        return True
    return False

def run_demo():
    """Run a demonstration of XTTS capabilities."""
    log("=" * 60)
    log("XTTS-v2 VOICE CLONING DEMO")
    log("=" * 60)
    
    if not check_and_install_tts():
        return False
    
    # Demo with built-in speaker
    log("\n--- Demo 1: Built-in Speaker ---")
    demo_text = "Hello! This is a demonstration of the XTTS voice synthesis system. The voice should sound natural and expressive."
    output_file = OUTPUT_DIR / "demo_builtin_speaker.wav"
    
    try:
        success = use_builtin_speaker(
            text=demo_text,
            speaker="Ana Florence",
            output_file=str(output_file),
            language="en"
        )
        if success:
            log(f"Demo 1 complete! Listen to: {output_file}", "OK")
    except Exception as e:
        log(f"Demo 1 failed: {e}", "WARN")
    
    # Demo multilingual
    log("\n--- Demo 2: Multilingual ---")
    demos = [
        ("en", "Hello, this is English."),
        ("es", "Hola, esto es español."),
        ("fr", "Bonjour, c'est français."),
        ("de", "Hallo, das ist Deutsch."),
    ]
    
    for lang, text in demos:
        output_file = OUTPUT_DIR / f"demo_{lang}.wav"
        try:
            use_builtin_speaker(text, "Ana Florence", str(output_file), lang)
        except Exception as e:
            log(f"{lang} failed: {e}", "WARN")
    
    log("\n" + "=" * 60)
    log("DEMO COMPLETE", "OK")
    log(f"Output files in: {OUTPUT_DIR.absolute()}")
    log("=" * 60)
    
    return True

def main():
    parser = argparse.ArgumentParser(
        description="XTTS Voice Cloning - Official Coqui Implementation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Run demo (uses built-in speaker, no sample needed)
    python xtts_official_install.py --demo
    
    # Clone your voice (needs 6+ second WAV sample)
    python xtts_official_install.py "Hello in my voice" --voice my_sample.wav
    
    # Multiple reference files for better cloning
    python xtts_official_install.py "Hello" --voice sample1.wav --voice sample2.wav
    
    # Use built-in speaker
    python xtts_official_install.py "Hello world" --speaker "Ana Florence"
    
    # Different language
    python xtts_official_install.py "Bonjour le monde" --voice sample.wav --language fr

Supported Languages:
    en (English), es (Spanish), fr (French), de (German), it (Italian),
    pt (Portuguese), pl (Polish), tr (Turkish), ru (Russian), nl (Dutch),
    cs (Czech), ar (Arabic), zh-cn (Chinese), ja (Japanese), hu (Hungarian),
    ko (Korean)
        """
    )
    
    parser.add_argument("text", nargs="?", help="Text to synthesize")
    parser.add_argument("--voice", "-v", action="append", help="Voice sample WAV (can use multiple)")
    parser.add_argument("--speaker", "-s", help="Built-in speaker name (e.g., 'Ana Florence')")
    parser.add_argument("--output", "-o", help="Output WAV file")
    parser.add_argument("--language", "-l", default="en", help="Language code (default: en)")
    parser.add_argument("--demo", action="store_true", help="Run demonstration")
    parser.add_argument("--list-speakers", action="store_true", help="List available speakers")
    parser.add_argument("--no-gpu", action="store_true", help="Disable GPU")
    parser.add_argument("--no-split", action="store_true", help="Don't split into sentences")
    
    args = parser.parse_args()
    
    # Check/install TTS
    if not check_and_install_tts():
        sys.exit(1)
    
    if args.demo:
        run_demo()
        return
    
    if args.list_speakers:
        list_available_speakers()
        return
    
    if not args.text:
        parser.print_help()
        return
    
    # Set default output
    if not args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = str(OUTPUT_DIR / f"xtts_{timestamp}.wav")
    
    log("=" * 60)
    log("XTTS-v2 VOICE SYNTHESIS")
    log("=" * 60)
    
    try:
        if args.voice:
            # Voice cloning mode
            success = clone_voice(
                text=args.text,
                speaker_wav=args.voice,
                output_file=args.output,
                language=args.language,
                use_gpu=not args.no_gpu,
                split_sentences=not args.no_split
            )
        elif args.speaker:
            # Built-in speaker mode
            success = use_builtin_speaker(
                text=args.text,
                speaker=args.speaker,
                output_file=args.output,
                language=args.language,
                use_gpu=not args.no_gpu
            )
        else:
            log("Provide --voice for cloning or --speaker for built-in voice", "ERROR")
            parser.print_help()
            sys.exit(1)
        
        if success:
            log("=" * 60)
            log("SUCCESS!", "OK")
            log(f"Play: start {args.output}")
            log("=" * 60)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        log("Cancelled", "WARN")
        sys.exit(130)
    except Exception as e:
        log(f"Error: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
