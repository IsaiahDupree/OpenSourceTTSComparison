#!/usr/bin/env python3
"""
Comprehensive XTTS-v2 test - multiple methods and verification
"""

import os
import sys
from pathlib import Path

# Apply MeCab workaround BEFORE any imports
class DummyMeCab:
    class Tagger:
        def __init__(self, *args, **kwargs):
            pass
sys.modules['MeCab'] = DummyMeCab()

def log(message, level="INFO"):
    """Console logging"""
    print(f"[{level}] {message}")

def check_dependencies():
    """Check if all dependencies are available"""
    log("=" * 70, "TEST")
    log("Checking Dependencies", "TEST")
    log("=" * 70, "TEST")
    
    checks = {}
    
    # Check TTS
    try:
        import TTS
        log(f"✅ TTS version: {TTS.__version__}", "SUCCESS")
        checks['TTS'] = True
    except Exception as e:
        log(f"❌ TTS: {e}", "ERROR")
        checks['TTS'] = False
    
    # Check torch
    try:
        import torch
        log(f"✅ PyTorch version: {torch.__version__}", "SUCCESS")
        log(f"   CUDA available: {torch.cuda.is_available()}", "INFO")
        if torch.cuda.is_available():
            log(f"   CUDA device: {torch.cuda.get_device_name(0)}", "INFO")
        checks['torch'] = True
    except Exception as e:
        log(f"❌ PyTorch: {e}", "ERROR")
        checks['torch'] = False
    
    # Check transformers
    try:
        import transformers
        log(f"✅ Transformers version: {transformers.__version__}", "SUCCESS")
        checks['transformers'] = True
    except Exception as e:
        log(f"❌ Transformers: {e}", "ERROR")
        checks['transformers'] = False
    
    return all(checks.values())

def method1_huggingface_direct():
    """Method 1: Download from Hugging Face directly"""
    log("\n" + "=" * 70, "TEST")
    log("Method 1: Hugging Face Direct Download", "TEST")
    log("=" * 70, "TEST")
    
    try:
        from huggingface_hub import snapshot_download
        import torch
        
        model_id = "coqui/XTTS-v2"
        cache_dir = Path.home() / ".local" / "share" / "tts" / "tts_models--multilingual--multi-dataset--xtts_v2"
        
        log(f"Downloading from: {model_id}")
        log(f"Cache directory: {cache_dir}")
        log("(This may take 10-20 minutes, ~1.5GB download)")
        
        try:
            model_path = snapshot_download(
                repo_id=model_id,
                cache_dir=str(cache_dir.parent),
                local_dir=str(cache_dir)
            )
            log(f"✅ Model downloaded to: {model_path}", "SUCCESS")
            return model_path
        except Exception as e:
            log(f"❌ Download failed: {e}", "ERROR")
            return None
            
    except Exception as e:
        log(f"❌ Method 1 failed: {e}", "ERROR")
        return None

def method2_tts_api():
    """Method 2: Use TTS API with different model names"""
    log("\n" + "=" * 70, "TEST")
    log("Method 2: TTS API (Auto-download)", "TEST")
    log("=" * 70, "TEST")
    
    try:
        from TTS.api import TTS
        import torch
        
        gpu = torch.cuda.is_available()
        log(f"GPU available: {gpu}")
        
        # Try different model name formats
        model_names = [
            "tts_models/multilingual/multi-dataset/xtts_v2",
            "tts_models/multilingual/multi-dataset/xtts-v2",
            "tts_models/multilingual/multi-dataset/xtts",
            "xtts_v2",
            "xtts-v2",
        ]
        
        for model_name in model_names:
            try:
                log(f"Trying: {model_name}")
                tts = TTS(model_name, gpu=gpu)
                log(f"✅ Success with: {model_name}", "SUCCESS")
                return tts, model_name
            except Exception as e:
                error_msg = str(e)[:100]
                log(f"   ❌ Failed: {error_msg}", "INFO")
                continue
        
        # Try listing models
        log("\nListing all available models...")
        try:
            all_models = TTS.list_models()
            log(f"Found {len(all_models)} models")
            
            # Filter for XTTS
            xtts_models = [m for m in all_models if 'xtts' in m.lower() or 'xtts' in m]
            if xtts_models:
                log(f"Found XTTS models: {xtts_models[:5]}", "SUCCESS")
                model_name = xtts_models[0]
                log(f"Trying first match: {model_name}")
                tts = TTS(model_name, gpu=gpu)
                return tts, model_name
            else:
                log("No XTTS models found in registry", "WARNING")
        except Exception as e:
            log(f"Could not list models: {e}", "WARNING")
        
        return None, None
        
    except Exception as e:
        log(f"❌ Method 2 failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return None, None

def method3_manual_path():
    """Method 3: Load from manual path if downloaded"""
    log("\n" + "=" * 70, "TEST")
    log("Method 3: Manual Path Loading", "TEST")
    log("=" * 70, "TEST")
    
    try:
        from TTS.api import TTS
        import torch
        
        # Check common cache locations
        cache_paths = [
            Path.home() / ".local" / "share" / "tts" / "tts_models--multilingual--multi-dataset--xtts_v2",
            Path.home() / ".cache" / "tts" / "tts_models--multilingual--multi-dataset--xtts_v2",
            Path("xtts_v2"),
            Path("models") / "xtts_v2",
        ]
        
        for cache_path in cache_paths:
            if cache_path.exists():
                log(f"Found model directory: {cache_path}")
                
                # Look for model files
                model_file = cache_path / "model.pth"
                config_file = cache_path / "config.json"
                
                if model_file.exists() and config_file.exists():
                    log(f"✅ Found model files", "SUCCESS")
                    try:
                        tts = TTS(model_path=str(model_file), config_path=str(config_file), gpu=torch.cuda.is_available())
                        log(f"✅ Model loaded from: {cache_path}", "SUCCESS")
                        return tts
                    except Exception as e:
                        log(f"❌ Failed to load: {e}", "ERROR")
                else:
                    log(f"Model files not found in {cache_path}", "INFO")
        
        log("No cached model found", "INFO")
        return None
        
    except Exception as e:
        log(f"❌ Method 3 failed: {e}", "ERROR")
        return None

def test_voice_cloning(tts, method_name):
    """Test actual voice cloning"""
    log("\n" + "=" * 70, "TEST")
    log(f"Testing Voice Cloning ({method_name})", "TEST")
    log("=" * 70, "TEST")
    
    if not tts:
        log("❌ No TTS model available", "ERROR")
        return False
    
    # Find reference audio
    ref_audio = None
    for path in [
        "openvoice_deploy/resources/demo_speaker2.mp3",
        "openvoice_deploy/resources/demo_speaker1.mp3",
        "openvoice_deploy/resources/demo_speaker0.mp3",
    ]:
        if os.path.exists(path):
            ref_audio = path
            break
    
    if not ref_audio:
        log("❌ No reference audio found", "ERROR")
        log("Place a .wav or .mp3 file in openvoice_deploy/resources/", "INFO")
        return False
    
    log(f"Using reference audio: {ref_audio}")
    
    # Test generation
    output_file = "output_xtts_test.wav"
    test_text = "Hello! This is a voice cloning test using Coqui XTTS-v2. The model should replicate the voice from the reference audio."
    
    try:
        log(f"Generating audio...")
        log(f"Text: {test_text[:60]}...")
        log("(This may take 30-60 seconds)")
        
        tts.tts_to_file(
            text=test_text,
            speaker_wav=ref_audio,
            language="en",
            file_path=output_file
        )
        
        if os.path.exists(output_file):
            size = os.path.getsize(output_file) / 1024
            log(f"✅ SUCCESS! Audio generated: {output_file}", "SUCCESS")
            log(f"   File size: {size:.1f} KB", "INFO")
            return True
        else:
            log("❌ Output file not created", "ERROR")
            return False
            
    except Exception as e:
        log(f"❌ Generation failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 70)
    print(" XTTS-v2 Comprehensive Test Suite")
    print("=" * 70)
    
    # Check dependencies
    if not check_dependencies():
        log("❌ Dependency check failed", "ERROR")
        return 1
    
    # Try Method 1: Hugging Face direct
    hf_path = method1_huggingface_direct()
    
    # Try Method 2: TTS API
    tts_api, model_name = method2_tts_api()
    
    # Try Method 3: Manual path
    tts_manual = method3_manual_path()
    
    # Use whichever method worked
    tts = None
    method_used = None
    
    if tts_api:
        tts = tts_api
        method_used = f"TTS API ({model_name})"
    elif tts_manual:
        tts = tts_manual
        method_used = "Manual Path"
    elif hf_path:
        # Try loading from downloaded path
        tts_manual = method3_manual_path()
        if tts_manual:
            tts = tts_manual
            method_used = "Hugging Face + Manual Path"
    
    # Test voice cloning
    if tts:
        success = test_voice_cloning(tts, method_used)
        
        # Final summary
        print("\n" + "=" * 70)
        print(" FINAL SUMMARY")
        print("=" * 70)
        print(f"✅ TTS Library: Working")
        print(f"✅ Model Loading: {method_used}")
        print(f"{'✅' if success else '❌'} Voice Cloning: {'Working' if success else 'Failed'}")
        print("=" * 70)
        
        return 0 if success else 1
    else:
        print("\n" + "=" * 70)
        print(" FINAL SUMMARY")
        print("=" * 70)
        print("❌ Could not load XTTS-v2 model")
        print("=" * 70)
        print("\nRecommendations:")
        print("1. Check internet connection for model download")
        print("2. Verify Hugging Face access")
        print("3. Try manual download from: https://huggingface.co/coqui/XTTS-v2")
        print("=" * 70)
        return 1

if __name__ == "__main__":
    sys.exit(main())

