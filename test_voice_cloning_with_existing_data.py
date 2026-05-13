#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Voice Cloning with Existing Processed Segments

Uses existing segments to test voice cloning with full console logging.
"""

import sys
import io
import json
from pathlib import Path
import time
from datetime import datetime

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def log(msg, level="INFO"):
    """Simple logging."""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"{timestamp} [{level}] {msg}", flush=True)

def log_section(title):
    """Section header."""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

# Check existing segments
log_section("CHECKING EXISTING SEGMENTS")

segments_dir = Path("processed_segments")
if not segments_dir.exists():
    log("ERROR: processed_segments directory not found", "ERROR")
    sys.exit(1)

segment_files = list(segments_dir.glob("*.wav"))
log(f"Found {len(segment_files)} segment files")

# Check results file for best segment
results_file = segments_dir / "processing_results.json"
best_segment = None

if results_file.exists():
    with open(results_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    # Try to get best segment from results
    best_segments = results.get('best_segments', [])
    if best_segments:
        best_segment = best_segments[0].get('output_file')
        log(f"Best segment from results: {Path(best_segment).name}")
        log(f"  Quality: {best_segments[0].get('quality_score', 0):.3f}")
        log(f"  Duration: {best_segments[0].get('duration', 0):.2f}s")
        log(f"  SNR: {best_segments[0].get('snr', 0):.1f}dB")
    else:
        # Use first available segment
        if segment_files:
            best_segment = str(segment_files[0])
            log(f"Using first available segment: {Path(best_segment).name}")
else:
    # Use first segment
    if segment_files:
        best_segment = str(segment_files[0])
        log(f"Using first segment: {Path(best_segment).name}")

if not best_segment or not Path(best_segment).exists():
    log("ERROR: No valid segment found", "ERROR")
    sys.exit(1)

log(f"Segment file: {best_segment}")
print("")

# Try Chatterbox
log_section("TESTING WITH CHATTERBOX")

try:
    import chatterbox
    import torch
    import soundfile as sf
    
    log("Chatterbox imported successfully")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    log(f"Device: {device}")
    
    log("Loading Chatterbox model (this may take a moment)...")
    start = time.time()
    tts = chatterbox.ChatterboxTTS.from_pretrained(device)
    load_time = time.time() - start
    log(f"Model loaded in {load_time:.2f}s")
    
    test_text = "Hello, this is a test of voice cloning using my voice from YouTube videos. Does it sound natural and clear?"
    log(f"Test text: '{test_text}'")
    log("Generating cloned voice...")
    
    start = time.time()
    audio_tensor = tts.generate(test_text, audio_prompt_path=best_segment)
    gen_time = time.time() - start
    
    output_file = "voice_clone_test_chatterbox.wav"
    audio_np = audio_tensor.squeeze(0).detach().cpu().numpy()
    sr = int(getattr(tts, "sr", 24000))
    sf.write(output_file, audio_np, sr)
    
    file_size = Path(output_file).stat().st_size / 1024  # KB
    
    log_section("VOICE CLONING SUCCESS!")
    log(f"Output file: {output_file}")
    log(f"File size: {file_size:.1f} KB")
    log(f"Generation time: {gen_time:.2f}s")
    log(f"Audio duration: {len(audio_np)/sr:.2f}s")
    log(f"Real-time factor: {gen_time / (len(audio_np)/sr):.2f}x")
    log("")
    log("SUCCESS: Voice cloning is working!", "INFO")
    log(f"Listen to: {output_file}", "INFO")
    
except ImportError:
    log("Chatterbox not available, trying Coqui TTS...", "WARNING")
    print("")
    
    # Try Coqui
    log_section("TESTING WITH COQUI TTS")
    
    try:
        from TTS.api import TTS
        import soundfile as sf
        
        log("Coqui TTS imported successfully")
        log("Loading XTTS-v2 model (this will download on first run)...")
        
        start = time.time()
        model = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
        load_time = time.time() - start
        log(f"Model loaded in {load_time:.2f}s")
        
        test_text = "Hello, this is a test of voice cloning using my voice from YouTube videos."
        log(f"Test text: '{test_text}'")
        log("Generating cloned voice...")
        
        start = time.time()
        output_file = "voice_clone_test_coqui.wav"
        model.tts_to_file(
            text=test_text,
            speaker_wav=best_segment,
            file_path=output_file
        )
        gen_time = time.time() - start
        
        file_size = Path(output_file).stat().st_size / 1024  # KB
        
        log_section("VOICE CLONING SUCCESS!")
        log(f"Output file: {output_file}")
        log(f"File size: {file_size:.1f} KB")
        log(f"Generation time: {gen_time:.2f}s")
        log("")
        log("SUCCESS: Voice cloning is working!", "INFO")
        log(f"Listen to: {output_file}", "INFO")
        
    except ImportError:
        log("ERROR: Coqui TTS not available", "ERROR")
        log("Install with: pip install TTS", "INFO")
        sys.exit(1)
    except Exception as e:
        log(f"ERROR: Coqui TTS failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
except Exception as e:
    log(f"ERROR: Chatterbox failed: {e}", "ERROR")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("")
log_section("COMPLETE")
log("Voice cloning test finished successfully!", "INFO")

