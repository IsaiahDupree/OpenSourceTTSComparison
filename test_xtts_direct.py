#!/usr/bin/env python3
"""
Direct XTTS-v2 loading - bypass TTS API issues
"""

import os
import sys
from pathlib import Path

# MeCab workaround
class DummyMeCab:
    class Tagger:
        def __init__(self, *args, **kwargs):
            pass
sys.modules['MeCab'] = DummyMeCab()

def test_xtts_direct():
    """Test XTTS-v2 with direct model loading"""
    print("=" * 70)
    print(" XTTS-v2 Direct Loading Test")
    print("=" * 70)
    
    try:
        from TTS.api import TTS
        import torch
        print("\n[1] Dependencies OK")
        print(f"   PyTorch: {torch.__version__}")
        print(f"   CUDA: {torch.cuda.is_available()}")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Find downloaded model
    print("\n[2] Finding downloaded model...")
    model_dir = Path.home() / ".local" / "share" / "tts" / "tts_models--multilingual--multi-dataset--xtts_v2"
    
    if not model_dir.exists():
        print(f"❌ Model directory not found: {model_dir}")
        return False
    
    print(f"✅ Model directory: {model_dir}")
    
    model_file = model_dir / "model.pth"
    config_file = model_dir / "config.json"
    
    if not model_file.exists():
        print(f"❌ Model file not found: {model_file}")
        return False
    
    if not config_file.exists():
        print(f"❌ Config file not found: {config_file}")
        return False
    
    print(f"✅ Model files found")
    
    # Try loading with TTS API using model_path
    print("\n[3] Loading model directly...")
    try:
        gpu = torch.cuda.is_available()
        
        # Method 1: Use model_path parameter
        print("  Trying: TTS(model_path=...)")
        try:
            tts = TTS(model_path=str(model_file), config_path=str(config_file), gpu=gpu)
            print("  ✅ Loaded with model_path")
        except Exception as e1:
            print(f"  ❌ Failed: {e1}")
            
            # Method 2: Use just model name (should use cache)
            print("  Trying: TTS('xtts_v2')")
            try:
                tts = TTS("xtts_v2", gpu=gpu)
                print("  ✅ Loaded with model name")
            except Exception as e2:
                print(f"  ❌ Failed: {e2}")
                
                # Method 3: Check what's wrong with the TTS object
                print("  Debugging TTS object...")
                tts = TTS("xtts_v2", gpu=gpu)
                print(f"  TTS object: {type(tts)}")
                print(f"  Has synthesizer: {hasattr(tts, 'synthesizer')}")
                if hasattr(tts, 'synthesizer'):
                    print(f"  Synthesizer: {tts.synthesizer}")
                    print(f"  Synthesizer type: {type(tts.synthesizer)}")
                
                # Try to manually initialize
                if hasattr(tts, 'synthesizer') and tts.synthesizer is None:
                    print("  Attempting manual initialization...")
                    # This might not work, but let's see
                    raise Exception("Synthesizer is None - cannot proceed")
        
        # Verify it works
        print("\n[4] Verifying model...")
        if hasattr(tts, 'synthesizer') and tts.synthesizer:
            if hasattr(tts.synthesizer, 'tts_model') and tts.synthesizer.tts_model:
                print("  ✅ Model verified")
            else:
                print("  ⚠️  tts_model is None")
                # Check if we can access it differently
                print(f"  Synthesizer attributes: {dir(tts.synthesizer)}")
        else:
            print("  ❌ Synthesizer is None")
            print(f"  TTS attributes: {dir(tts)}")
            return False
        
        # Test generation
        print("\n[5] Testing generation...")
        ref_audio = "openvoice_deploy/resources/demo_speaker2.mp3"
        if not os.path.exists(ref_audio):
            print(f"  ❌ Reference audio not found: {ref_audio}")
            return False
        
        output_file = "output_xtts_direct.wav"
        
        try:
            print(f"  Generating: {output_file}")
            tts.tts_to_file(
                text="Hello! This is a test.",
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
            print(f"  ❌ Generation error: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_xtts_direct()
    print("\n" + "=" * 70)
    if success:
        print(" ✅ TEST PASSED")
    else:
        print(" ❌ TEST FAILED")
    print("=" * 70)
    sys.exit(0 if success else 1)

