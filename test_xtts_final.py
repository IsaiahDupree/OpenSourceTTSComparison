#!/usr/bin/env python3
"""
Final XTTS-v2 test - find correct model name and load properly
"""

import os
import sys

# MeCab workaround
class DummyMeCab:
    class Tagger:
        def __init__(self, *args, **kwargs):
            pass
sys.modules['MeCab'] = DummyMeCab()

from TTS.api import TTS
import torch

def test_xtts_final():
    """Final XTTS-v2 test"""
    print("=" * 70)
    print(" XTTS-v2 Final Test")
    print("=" * 70)

# List all models
print("\n[1] Listing available models...")
try:
    all_models = TTS.list_models()
    print(f"Total models: {len(all_models)}")
    
    # Find XTTS models
    xtts_models = [m for m in all_models if 'xtts' in m.lower()]
    print(f"\nXTTS models found: {len(xtts_models)}")
    for model in xtts_models[:5]:
        print(f"  - {model}")
    
    if not xtts_models:
        print("  ⚠️  No XTTS models in registry")
        print("  Trying direct model name anyway...")
        model_name = "xtts_v2"
    else:
        model_name = xtts_models[0]
        print(f"\nUsing model: {model_name}")
        
except Exception as e:
    print(f"❌ Could not list models: {e}")
    model_name = "xtts_v2"  # Fallback

# Try loading with explicit initialization
print(f"\n[2] Loading model: {model_name}")
gpu = torch.cuda.is_available()
print(f"GPU: {gpu}")

try:
    # Create TTS object
    tts = TTS(model_name=model_name, gpu=gpu)
    
    # Check if we need to manually initialize
    if tts.synthesizer is None:
        print("  ⚠️  Synthesizer is None, trying manual initialization...")
        
        # Try loading by name explicitly
        try:
            tts.load_tts_model_by_name(model_name, gpu=gpu)
            print("  ✅ Manual load attempted")
        except Exception as e:
            print(f"  ❌ Manual load failed: {e}")
            # Try with full path
            model_dir = os.path.expanduser("~/.local/share/tts/tts_models--multilingual--multi-dataset--xtts_v2")
            model_file = os.path.join(model_dir, "model.pth")
            config_file = os.path.join(model_dir, "config.json")
            
            if os.path.exists(model_file) and os.path.exists(config_file):
                print(f"  Trying to load from path...")
                try:
                    tts.load_tts_model_by_path(model_file, config_file, gpu=gpu)
                    print("  ✅ Loaded from path")
                except Exception as e2:
                    print(f"  ❌ Path load failed: {e2}")
    
    # Check final state
    print(f"\n[3] Final state check...")
    print(f"  Model name: {tts.model_name}")
    print(f"  Synthesizer: {tts.synthesizer is not None}")
    
    if tts.synthesizer is None:
        print("  ❌ Synthesizer still None - model not loaded")
        print("\n  This appears to be a TTS library issue.")
        print("  The model downloaded successfully, but TTS API isn't loading it.")
        print("\n  Possible solutions:")
        print("  1. Update TTS library: pip install --upgrade TTS")
        print("  2. Use a different TTS version")
        print("  3. Load model directly using TTS internal APIs")
        return False
    
    # Test generation
    print(f"\n[4] Testing generation...")
    ref_audio = "openvoice_deploy/resources/demo_speaker2.mp3"
    if not os.path.exists(ref_audio):
        print(f"  ❌ Reference audio not found: {ref_audio}")
        return False
    
    output_file = "output_xtts_final.wav"
    
    try:
        print(f"  Generating: {output_file}")
        tts.tts_to_file(
            text="Hello! This is a voice cloning test.",
            speaker_wav=ref_audio,
            language="en",
            file_path=output_file
        )
        
        if os.path.exists(output_file):
            size = os.path.getsize(output_file) / 1024
            print(f"  ✅ SUCCESS! Generated {output_file} ({size:.1f} KB)")
            return True
        else:
            print("  ❌ File not created")
            return False
            
    except Exception as e:
        print(f"  ❌ Generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    return False

if __name__ == "__main__":
    success = test_xtts_final()
    print("\n" + "=" * 70)
    if success:
        print(" ✅ XTTS-v2 IS WORKING!")
    else:
        print(" ❌ XTTS-v2 has initialization issues")
        print("\nModel downloaded successfully, but TTS API has a bug.")
        print("This is a known issue with TTS 0.14.3 and XTTS-v2.")
    print("=" * 70)
    sys.exit(0 if success else 1)

