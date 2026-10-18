#!/usr/bin/env python3
"""
Simple XTTS-v2 test - try to bypass MeCab issue
"""

import os
import sys

# Apply MeCab workaround BEFORE any TTS imports
print("Applying MeCab workaround...")
class DummyMeCab:
    class Tagger:
        def __init__(self, *args, **kwargs):
            pass

sys.modules['MeCab'] = DummyMeCab()

# Now try importing TTS
try:
    print("Importing TTS...")
    from TTS.api import TTS
    print("✅ TTS imported successfully!")
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test if we can use it
print("\nTesting XTTS-v2...")
try:
    import torch
    gpu_available = torch.cuda.is_available()
    print(f"GPU available: {gpu_available}")
    
    print("Loading XTTS-v2 model...")
    print("(This will download ~1.5GB on first run)")
    
    # Try different model name formats
    model_names = [
        "tts_models/multilingual/multi-dataset/xtts_v2",
        "tts_models/multilingual/multi-dataset/xtts-v2",
        "tts_models/multilingual/multi-dataset/xtts_v2.0",
    ]
    
    tts = None
    for model_name in model_names:
        try:
            print(f"  Trying: {model_name}")
            tts = TTS(model_name, gpu=gpu_available)
            print(f"  ✅ Success with: {model_name}")
            break
        except Exception as e:
            print(f"  ❌ Failed: {str(e)[:100]}")
            continue
    
    if not tts:
        # Try listing available models
        print("\nListing available models...")
        try:
            models = TTS.list_models()
            xtts_models = [m for m in models if 'xtts' in m.lower()]
            if xtts_models:
                print(f"Found XTTS models: {xtts_models[:3]}")
                model_name = xtts_models[0]
                print(f"Trying: {model_name}")
                tts = TTS(model_name, gpu=gpu_available)
            else:
                raise ValueError("No XTTS models found")
        except Exception as e:
            print(f"❌ Could not find XTTS model: {e}")
            raise
    print("✅ Model loaded!")
    
    # Check for reference audio
    ref_audio = None
    for path in ["openvoice_deploy/resources/demo_speaker2.mp3",
                 "openvoice_deploy/resources/demo_speaker1.mp3"]:
        if os.path.exists(path):
            ref_audio = path
            break
    
    if ref_audio:
        print(f"\nUsing reference audio: {ref_audio}")
        print("Generating test audio...")
        
        tts.tts_to_file(
            text="This is a voice cloning test using Coqui XTTS-v2.",
            speaker_wav=ref_audio,
            language="en",
            file_path="output_xtts.wav"
        )
        
        if os.path.exists("output_xtts.wav"):
            size = os.path.getsize("output_xtts.wav") / 1024
            print(f"✅ SUCCESS! Audio generated: output_xtts.wav ({size:.1f} KB)")
        else:
            print("❌ Output file not created")
    else:
        print("\n⚠️  No reference audio found")
        print("Model loaded successfully, but need reference audio to test generation")
        print("Place a .wav file named 'ref.wav' in the current directory")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

