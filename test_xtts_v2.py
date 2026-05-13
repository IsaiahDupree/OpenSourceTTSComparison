#!/usr/bin/env python3
"""
Test Coqui XTTS-v2 voice cloning
"""

import os
import sys
from pathlib import Path

def test_xtts_v2():
    """Test XTTS-v2 voice cloning"""
    print("=" * 70)
    print(" Testing Coqui XTTS-v2 Voice Cloning")
    print("=" * 70)
    
    # Check if TTS is available
    try:
        from TTS.api import TTS
        print("\n[1] TTS library imported successfully")
    except ImportError as e:
        print(f"\n[ERROR] TTS library not available: {e}")
        print("\nInstallation options:")
        print("1. Try: pip install TTS --no-deps (then install dependencies manually)")
        print("2. Try: pip install TTS --use-pep517")
        print("3. Use a virtual environment with Python 3.8-3.10")
        return False
    
    # Check for reference audio
    print("\n[2] Checking for reference audio...")
    ref_audio_paths = [
        Path("openvoice_deploy/resources/demo_speaker2.mp3"),
        Path("openvoice_deploy/resources/demo_speaker1.mp3"),
        Path("openvoice_deploy/resources/demo_speaker0.mp3"),
    ]
    
    ref_audio = None
    for path in ref_audio_paths:
        if path.exists():
            ref_audio = path
            print(f"  [OK] Found: {ref_audio}")
            break
    
    if not ref_audio:
        print("  [WARNING] No reference audio found")
        print("  Will test with a placeholder path")
        ref_audio = "ref.wav"  # Placeholder
    
    # Test model loading
    print("\n[3] Loading XTTS-v2 model...")
    print("  (This will download the model on first run - may take a few minutes)")
    
    try:
        import torch
        gpu_available = torch.cuda.is_available()
        print(f"  GPU available: {gpu_available}")
        
        print("  Initializing TTS...")
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=gpu_available)
        print("  [SUCCESS] Model loaded!")
        
    except Exception as e:
        print(f"  [ERROR] Failed to load model: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test generation
    print("\n[4] Testing voice cloning...")
    text = "This is a voice cloning test using Coqui XTTS-v2."
    output_path = "output_xtts.wav"
    
    print(f"  Text: {text}")
    print(f"  Reference: {ref_audio}")
    print(f"  Output: {output_path}")
    print("  (This may take 10-30 seconds...)")
    
    try:
        tts.tts_to_file(
            text=text,
            speaker_wav=str(ref_audio) if isinstance(ref_audio, Path) else ref_audio,
            language="en",
            file_path=output_path
        )
        
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path) / 1024
            print(f"\n  [SUCCESS] Audio generated!")
            print(f"  File: {output_path}")
            print(f"  Size: {file_size:.1f} KB")
            return True
        else:
            print(f"\n  [ERROR] Output file not created")
            return False
            
    except Exception as e:
        print(f"\n  [ERROR] Generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_xtts_v2()
    print("\n" + "=" * 70)
    if success:
        print(" [SUCCESS] XTTS-v2 test completed!")
    else:
        print(" [FAILED] Test failed - check errors above")
    print("=" * 70)
    sys.exit(0 if success else 1)

