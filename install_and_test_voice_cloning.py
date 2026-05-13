#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Install Voice Cloning Model and Test with Existing Segments

Full console logging throughout.
"""

import sys
import io
import subprocess
import time
from pathlib import Path
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

def try_chatterbox_venv():
    """Try using Chatterbox from existing venv."""
    log_section("TRYING CHATTERBOX FROM EXISTING VENV")
    
    venv_python = Path("venv_chatterbox311/Scripts/python.exe")
    if not venv_python.exists():
        venv_python = Path("venv_chatterbox/Scripts/python.exe")
    
    if not venv_python.exists():
        log("No Chatterbox venv found", "WARNING")
        return False
    
    log(f"Found venv: {venv_python.parent.parent}")
    
    try:
        # Test import
        result = subprocess.run(
            [str(venv_python), "-c", "import chatterbox; print('OK')"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            log("Chatterbox available in venv!", "INFO")
            
            # Run voice cloning test
            segment_file = "processed_segments/0YWpkJkbXxs_Never lose power again. UPS UNBOXING._segment_0.wav"
            if Path(segment_file).exists():
                log("Running voice cloning test...")
                log("")
                
                test_script = f"""
import chatterbox
import torch
import soundfile as sf
from pathlib import Path

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device: {{device}}")

print("Loading model...")
tts = chatterbox.ChatterboxTTS.from_pretrained(device)
print("Model loaded!")

test_text = "Hello, this is a test of voice cloning using my voice from YouTube videos."
print(f"Generating: '{{test_text}}'")

audio_tensor = tts.generate(test_text, audio_prompt_path="{segment_file}")
audio_np = audio_tensor.squeeze(0).detach().cpu().numpy()
sr = int(getattr(tts, "sr", 24000))

output_file = "voice_clone_test_chatterbox.wav"
sf.write(output_file, audio_np, sr)
print(f"SUCCESS! Output saved to: {{output_file}}")
print(f"Audio length: {{len(audio_np)/sr:.2f}}s")
"""
                
                result = subprocess.run(
                    [str(venv_python), "-c", test_script],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                print(result.stdout)
                if result.stderr:
                    print(result.stderr)
                
                if result.returncode == 0:
                    log("Voice cloning test successful!", "INFO")
                    return True
                else:
                    log("Voice cloning test failed", "ERROR")
                    return False
            else:
                log(f"Segment file not found: {segment_file}", "ERROR")
                return False
        else:
            log("Chatterbox not available in venv", "WARNING")
            return False
            
    except Exception as e:
        log(f"Error testing venv: {e}", "ERROR")
        return False

def install_coqui_tts():
    """Install Coqui TTS."""
    log_section("INSTALLING COQUI TTS")
    
    log("This may take 5-30 minutes depending on build requirements...")
    log("Installing TTS package...")
    print("")
    
    try:
        process = subprocess.Popen(
            [sys.executable, "-m", "pip", "install", "TTS", "--upgrade"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        for line in process.stdout:
            line = line.strip()
            if line and ("Downloading" in line or "Installing" in line or "Building" in line or "Successfully" in line):
                if "already satisfied" not in line.lower():
                    print(f"  {line[:80]}", flush=True)
        
        return_code = process.wait()
        
        if return_code == 0:
            log("Coqui TTS installed successfully!", "INFO")
            return True
        else:
            log("Installation failed", "ERROR")
            return False
            
    except Exception as e:
        log(f"Installation error: {e}", "ERROR")
        return False

def test_coqui_cloning():
    """Test Coqui TTS voice cloning."""
    log_section("TESTING COQUI TTS VOICE CLONING")
    
    segment_file = "processed_segments/0YWpkJkbXxs_Never lose power again. UPS UNBOXING._segment_0.wav"
    
    if not Path(segment_file).exists():
        log(f"Segment not found: {segment_file}", "ERROR")
        return False
    
    try:
        from TTS.api import TTS
        import soundfile as sf
        
        log("Loading XTTS-v2 model (may download on first run)...")
        start = time.time()
        model = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
        load_time = time.time() - start
        log(f"Model loaded in {load_time:.2f}s")
        
        test_text = "Hello, this is a test of voice cloning using my voice from YouTube videos."
        log(f"Generating: '{test_text}'")
        
        start = time.time()
        output_file = "voice_clone_test_coqui.wav"
        model.tts_to_file(
            text=test_text,
            speaker_wav=segment_file,
            file_path=output_file
        )
        gen_time = time.time() - start
        
        file_size = Path(output_file).stat().st_size / 1024
        
        log_section("VOICE CLONING SUCCESS!")
        log(f"Output: {output_file}")
        log(f"Size: {file_size:.1f} KB")
        log(f"Generation time: {gen_time:.2f}s")
        log("")
        log("SUCCESS: Voice cloning is working!", "INFO")
        return True
        
    except Exception as e:
        log(f"Voice cloning failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function."""
    log_section("INSTALL AND TEST VOICE CLONING")
    log(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check segments
    segments = list(Path("processed_segments").glob("*.wav"))
    if not segments:
        log("ERROR: No processed segments found", "ERROR")
        log("Run: python improved_audio_processor.py first", "INFO")
        return
    
    log(f"Found {len(segments)} segments ready for voice cloning")
    print("")
    
    # Try Chatterbox venv first
    if try_chatterbox_venv():
        log_section("COMPLETE")
        log("Voice cloning working with Chatterbox!", "INFO")
        return
    
    # Install Coqui TTS
    print("")
    if install_coqui_tts():
        print("")
        if test_coqui_cloning():
            log_section("COMPLETE")
            log("Voice cloning working with Coqui TTS!", "INFO")
        else:
            log("Installation succeeded but test failed", "ERROR")
    else:
        log("Could not install Coqui TTS", "ERROR")
        log("Try manually: pip install TTS", "INFO")

if __name__ == "__main__":
    main()

