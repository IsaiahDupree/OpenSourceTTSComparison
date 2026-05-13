#!/usr/bin/env python3
"""
Docker Voice Cloning - Easy to Use
===================================
Uses Coqui TTS via Docker for smooth, natural voice cloning.

Requirements:
- Docker installed and running
- A voice sample (WAV file, at least 6 seconds of clear speech)

Usage:
    python docker_voice_clone.py "Your text here" --voice sample.wav --output output.wav
    python docker_voice_clone.py --demo  # Run a demo with default voice
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime

# Output directory
OUTPUT_DIR = Path("voice_clone_output")
OUTPUT_DIR.mkdir(exist_ok=True)

def log(msg: str, level: str = "INFO"):
    """Simple logging with timestamp."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    symbols = {"INFO": "ℹ️", "OK": "✅", "WARN": "⚠️", "ERROR": "❌"}
    symbol = symbols.get(level, "•")
    print(f"[{timestamp}] {symbol} {msg}")

def check_docker():
    """Check if Docker is available."""
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            log(f"Docker available: {result.stdout.strip()}", "OK")
            return True
    except Exception as e:
        log(f"Docker check failed: {e}", "ERROR")
    return False

def synthesize_with_docker(
    text: str,
    output_file: str,
    speaker_wav: str = None,
    language: str = "en",
    model: str = None,
    use_gpu: bool = True
) -> bool:
    """
    Synthesize speech using Docker Coqui TTS.
    
    Args:
        text: Text to synthesize
        output_file: Output WAV file path
        speaker_wav: Optional voice sample for cloning
        language: Language code (en, es, fr, de, etc.)
        model: TTS model to use (default: XTTS-v2 for cloning, tacotron2 for basic)
        use_gpu: Whether to use GPU acceleration
    
    Returns:
        True if successful, False otherwise
    """
    output_path = Path(output_file).absolute()
    output_dir = output_path.parent
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Base docker command
    docker_cmd = ["docker", "run", "--rm", "-e", "COQUI_TOS_AGREED=1"]
    
    # Add GPU support if available
    if use_gpu:
        docker_cmd.extend(["--gpus", "all"])
    
    # Mount output directory
    docker_cmd.extend(["-v", f"{output_dir}:/output"])
    
    # Mount voice sample if provided
    volumes = []
    speaker_path_in_container = None
    if speaker_wav:
        speaker_path = Path(speaker_wav).absolute()
        if not speaker_path.exists():
            log(f"Voice sample not found: {speaker_path}", "ERROR")
            return False
        speaker_dir = speaker_path.parent
        docker_cmd.extend(["-v", f"{speaker_dir}:/samples"])
        speaker_path_in_container = f"/samples/{speaker_path.name}"
        log(f"Using voice sample: {speaker_path.name}")
    
    # Add container image
    docker_cmd.append("ghcr.io/coqui-ai/tts:latest")
    
    # Add TTS arguments
    docker_cmd.extend(["--text", text])
    docker_cmd.extend(["--out_path", f"/output/{output_path.name}"])
    
    # Choose model based on whether we're doing voice cloning
    if speaker_wav and speaker_path_in_container:
        # Use XTTS-v2 for voice cloning
        if model is None:
            model = "tts_models/multilingual/multi-dataset/xtts_v2"
        docker_cmd.extend(["--model_name", model])
        docker_cmd.extend(["--speaker_wav", speaker_path_in_container])
        docker_cmd.extend(["--language_idx", language])
        log(f"Voice cloning mode with XTTS-v2 (language: {language})")
    else:
        # Use a good quality model for basic TTS
        if model is None:
            model = "tts_models/en/ljspeech/tacotron2-DDC"
        docker_cmd.extend(["--model_name", model])
        log(f"Basic TTS mode with {model.split('/')[-1]}")
    
    # Run the command
    log(f"Generating speech ({len(text)} characters)...")
    log(f"This may take a minute on first run (downloading model)...")
    
    try:
        result = subprocess.run(
            docker_cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        
        if result.returncode == 0:
            if output_path.exists():
                size_kb = output_path.stat().st_size / 1024
                log(f"Audio saved: {output_path} ({size_kb:.1f} KB)", "OK")
                return True
            else:
                log("Output file not created", "ERROR")
                return False
        else:
            log(f"Docker TTS failed: {result.stderr[:500]}", "ERROR")
            return False
            
    except subprocess.TimeoutExpired:
        log("Timeout - synthesis took too long", "ERROR")
        return False
    except Exception as e:
        log(f"Error: {e}", "ERROR")
        return False


def run_demo():
    """Run a demo to show the TTS quality."""
    log("=" * 50)
    log("DOCKER VOICE CLONING DEMO")
    log("=" * 50)
    
    if not check_docker():
        log("Docker is required for this demo", "ERROR")
        return False
    
    # Demo texts
    demos = [
        ("Hello! This is a demo of natural sounding text to speech.", "demo_hello.wav"),
        ("The quick brown fox jumps over the lazy dog. This sentence contains every letter of the alphabet.", "demo_pangram.wav"),
        ("Welcome to the world of AI voice synthesis. This technology can read any text aloud with natural intonation.", "demo_welcome.wav"),
    ]
    
    log("\nGenerating demo audio files...")
    
    for text, filename in demos:
        output_file = OUTPUT_DIR / filename
        log(f"\nGenerating: {filename}")
        log(f"Text: \"{text[:50]}...\"" if len(text) > 50 else f"Text: \"{text}\"")
        
        success = synthesize_with_docker(text, str(output_file), use_gpu=True)
        
        if not success:
            log(f"Failed to generate {filename}", "WARN")
    
    log("\n" + "=" * 50)
    log("DEMO COMPLETE", "OK")
    log(f"Output files are in: {OUTPUT_DIR.absolute()}")
    log("=" * 50)
    
    return True


def clone_voice_demo(voice_sample: str):
    """Demo voice cloning with a provided sample."""
    log("=" * 50)
    log("VOICE CLONING DEMO")
    log("=" * 50)
    
    if not check_docker():
        log("Docker is required for voice cloning", "ERROR")
        return False
    
    if not Path(voice_sample).exists():
        log(f"Voice sample not found: {voice_sample}", "ERROR")
        return False
    
    texts = [
        "Hello, this is my cloned voice speaking.",
        "The voice cloning technology can reproduce my speaking style.",
        "This is amazing! My voice can now say anything.",
    ]
    
    log(f"\nCloning voice from: {voice_sample}")
    log("Note: First run may take a few minutes to download the XTTS-v2 model (2-3 GB)")
    
    for i, text in enumerate(texts, 1):
        output_file = OUTPUT_DIR / f"cloned_voice_{i}.wav"
        log(f"\n[{i}/{len(texts)}] Generating: {output_file.name}")
        log(f"Text: \"{text}\"")
        
        success = synthesize_with_docker(
            text, 
            str(output_file), 
            speaker_wav=voice_sample,
            language="en"
        )
        
        if not success:
            log(f"Failed to generate cloned audio", "WARN")
    
    log("\n" + "=" * 50)
    log("VOICE CLONING COMPLETE", "OK")
    log(f"Output files are in: {OUTPUT_DIR.absolute()}")
    log("=" * 50)
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Easy Docker Voice Cloning",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Run demo (no voice cloning, just TTS quality demo)
    python docker_voice_clone.py --demo
    
    # Generate speech from text
    python docker_voice_clone.py "Hello world"
    
    # Clone a voice (requires a 6+ second WAV sample)
    python docker_voice_clone.py "Hello in my voice" --voice my_voice.wav
    
    # Clone voice with specific output file
    python docker_voice_clone.py "Hello" --voice sample.wav --output hello.wav
    
    # Voice cloning demo with your sample
    python docker_voice_clone.py --clone-demo --voice my_voice.wav
        """
    )
    
    parser.add_argument("text", nargs="?", help="Text to synthesize")
    parser.add_argument("--voice", "-v", help="Voice sample WAV for cloning (6+ seconds)")
    parser.add_argument("--output", "-o", help="Output WAV file path")
    parser.add_argument("--language", "-l", default="en", help="Language code (default: en)")
    parser.add_argument("--demo", action="store_true", help="Run TTS quality demo")
    parser.add_argument("--clone-demo", action="store_true", help="Run voice cloning demo")
    parser.add_argument("--no-gpu", action="store_true", help="Disable GPU acceleration")
    
    args = parser.parse_args()
    
    if args.demo:
        run_demo()
        return
    
    if args.clone_demo:
        if not args.voice:
            log("Voice cloning demo requires --voice <sample.wav>", "ERROR")
            sys.exit(1)
        clone_voice_demo(args.voice)
        return
    
    if not args.text:
        parser.print_help()
        return
    
    if not check_docker():
        log("Docker is required. Please install Docker Desktop.", "ERROR")
        sys.exit(1)
    
    # Default output file
    if not args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = str(OUTPUT_DIR / f"output_{timestamp}.wav")
    
    success = synthesize_with_docker(
        args.text,
        args.output,
        speaker_wav=args.voice,
        language=args.language,
        use_gpu=not args.no_gpu
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
