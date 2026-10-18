#!/usr/bin/env python3
"""
Fixed XTTS-v2 test with proper initialization
"""

import os
import sys
from pathlib import Path

# Apply MeCab workaround
class DummyMeCab:
    class Tagger:
        def __init__(self, *args, **kwargs):
            pass
sys.modules['MeCab'] = DummyMeCab()

def test_xtts_v2():
    """Test XTTS-v2 with proper initialization"""
    print("=" * 70)
    print(" XTTS-v2 Voice Cloning Test")
    print("=" * 70)
    
    # Import TTS
    print("\n[1] Importing TTS...")
    try:
        from TTS.api import TTS
        import torch
        print("  ✅ TTS imported")
        print(f"  ✅ PyTorch {torch.__version__}")
        print(f"  ✅ CUDA: {torch.cuda.is_available()}")
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        return False
    
    # Load model
    print("\n[2] Loading XTTS-v2 model...")
    print("  Model name: xtts_v2")
    print("  (Model already downloaded, loading from cache)")
    
    try:
        gpu = torch.cuda.is_available()
        tts = TTS("xtts_v2", gpu=gpu)
        print("  ✅ Model loaded!")
        
        # Verify model is properly initialized
        if hasattr(tts, 'synthesizer') and tts.synthesizer:
            if hasattr(tts.synthesizer, 'tts_model') and tts.synthesizer.tts_model:
                print("  ✅ Model properly initialized")
            else:
                print("  ⚠️  Model not fully initialized, trying to reload...")
                # Try reloading
                tts = TTS("xtts_v2", gpu=gpu)
        else:
            print("  ⚠️  Synthesizer not initialized")
            
    except Exception as e:
        print(f"  ❌ Model loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Find reference audio
    print("\n[3] Finding reference audio...")
    ref_audio = None
    for path in [
        "openvoice_deploy/resources/demo_speaker2.mp3",
        "openvoice_deploy/resources/demo_speaker1.mp3",
        "openvoice_deploy/resources/demo_speaker0.mp3",
    ]:
        if os.path.exists(path):
            ref_audio = path
            print(f"  ✅ Found: {ref_audio}")
            break
    
    if not ref_audio:
        print("  ❌ No reference audio found")
        return False
    
    # Generate audio
    print("\n[4] Generating voice clone...")
    output_file = "output_xtts_v2.wav"
    test_text = "Hello! This is a voice cloning test using Coqui XTTS-v2."
    
    print(f"  Text: {test_text}")
    print(f"  Reference: {ref_audio}")
    print(f"  Output: {output_file}")
    print("  (This may take 30-60 seconds...)")
    
    try:
        # Use the correct API method
        tts.tts_to_file(
            text=test_text,
            speaker_wav=ref_audio,
            language="en",
            file_path=output_file
        )
        
        if os.path.exists(output_file):
            size = os.path.getsize(output_file) / 1024
            print(f"\n  ✅ SUCCESS! Audio generated")
            print(f"  File: {output_file}")
            print(f"  Size: {size:.1f} KB")
            return True
        else:
            print("  ❌ Output file not created")
            return False
            
    except Exception as e:
        print(f"  ❌ Generation failed: {e}")
        import traceback
        traceback.print_exc()
        
        # Try alternative method
        print("\n  Trying alternative method...")
        try:
            # Try using synthesize method directly
            wav = tts.tts(
                text=test_text,
                speaker_wav=ref_audio,
                language="en"
            )
            
            # Save manually
            import soundfile as sf
            sf.write(output_file, wav, samplerate=22050)
            
            if os.path.exists(output_file):
                size = os.path.getsize(output_file) / 1024
                print(f"  ✅ SUCCESS with alternative method!")
                print(f"  File: {output_file} ({size:.1f} KB)")
                return True
        except Exception as e2:
            print(f"  ❌ Alternative method also failed: {e2}")
        
        return False

if __name__ == "__main__":
    success = test_xtts_v2()
    print("\n" + "=" * 70)
    if success:
        print(" ✅ XTTS-v2 TEST PASSED!")
        print(" Voice cloning is working!")
    else:
        print(" ❌ XTTS-v2 TEST FAILED")
        print(" Check errors above")
    print("=" * 70)
    sys.exit(0 if success else 1)

