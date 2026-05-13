#!/usr/bin/env python3
"""
Startup tests for OpenVoice - verify all components are working
"""

import os
import sys
from pathlib import Path
import importlib

def test_python_version():
    """Test Python version"""
    print("=" * 70)
    print(" [1] Python Version Check")
    print("=" * 70)
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"  ❌ Python 3.8+ required. Found: {version.major}.{version.minor}")
        return False
    print(f"  ✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def test_imports():
    """Test all critical imports"""
    print("\n" + "=" * 70)
    print(" [2] Import Tests")
    print("=" * 70)
    
    # Add openvoice_deploy to path
    base_dir = Path(__file__).parent / "openvoice_deploy"
    sys.path.insert(0, str(base_dir))
    openvoice_path = base_dir / "openvoice"
    sys.path.insert(0, str(openvoice_path))
    
    tests = [
        ("torch", "torch"),
        ("torchaudio", "torchaudio"),
        ("numpy", "numpy"),
        ("gradio", "gradio"),
        ("librosa", "librosa"),
        ("pydub", "pydub"),
        ("langid", "langid"),
        ("openvoice.se_extractor", "openvoice.se_extractor"),
        ("openvoice.api", "openvoice.api"),
    ]
    
    all_ok = True
    for name, import_name in tests:
        try:
            mod = importlib.import_module(import_name)
            print(f"  ✅ {name}")
        except ImportError as e:
            print(f"  ❌ {name}: {e}")
            all_ok = False
    
    return all_ok

def test_checkpoints():
    """Test checkpoint files exist"""
    print("\n" + "=" * 70)
    print(" [3] Checkpoint Files Check")
    print("=" * 70)
    
    checkpoints_dir = Path("openvoice_deploy/checkpoints")
    required_files = [
        "base_speakers/EN/checkpoint.pth",
        "base_speakers/EN/config.json",
        "base_speakers/EN/en_default_se.pth",
        "base_speakers/EN/en_style_se.pth",
        "base_speakers/ZH/checkpoint.pth",
        "base_speakers/ZH/config.json",
        "base_speakers/ZH/zh_default_se.pth",
        "converter/checkpoint.pth",
        "converter/config.json",
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = checkpoints_dir / file_path
        if full_path.exists():
            size = full_path.stat().st_size / (1024 * 1024)  # MB
            print(f"  ✅ {file_path} ({size:.1f} MB)")
        else:
            print(f"  ❌ {file_path} - MISSING")
            all_exist = False
    
    return all_exist

def test_resources():
    """Test resource files exist"""
    print("\n" + "=" * 70)
    print(" [4] Resource Files Check")
    print("=" * 70)
    
    resources_dir = Path("openvoice_deploy/resources")
    required_files = [
        "demo_speaker0.mp3",
        "demo_speaker1.mp3",
        "demo_speaker2.mp3",
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = resources_dir / file_path
        if full_path.exists():
            size = full_path.stat().st_size / 1024  # KB
            print(f"  ✅ {file_path} ({size:.1f} KB)")
        else:
            print(f"  ❌ {file_path} - MISSING")
            all_exist = False
    
    return all_exist

def test_model_loading():
    """Test model loading (lazy load)"""
    print("\n" + "=" * 70)
    print(" [5] Model Loading Test")
    print("=" * 70)
    
    try:
        base_dir = Path(__file__).parent / "openvoice_deploy"
        sys.path.insert(0, str(base_dir))
        openvoice_path = base_dir / "openvoice"
        sys.path.insert(0, str(openvoice_path))
        
        from openvoice.api import BaseSpeakerTTS, ToneColorConverter
        import torch
        
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"  Device: {device}")
        
        # Test loading English model
        en_ckpt = base_dir / "checkpoints/base_speakers/EN"
        print(f"  Loading English model...")
        en_model = BaseSpeakerTTS(str(en_ckpt / "config.json"), device=device)
        en_model.load_ckpt(str(en_ckpt / "checkpoint.pth"))
        print(f"  ✅ English model loaded")
        
        # Test loading converter
        conv_ckpt = base_dir / "checkpoints/converter"
        print(f"  Loading converter...")
        converter = ToneColorConverter(str(conv_ckpt / "config.json"), device=device)
        converter.load_ckpt(str(conv_ckpt / "checkpoint.pth"))
        print(f"  ✅ Converter loaded")
        
        return True
    except Exception as e:
        print(f"  ❌ Model loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 70)
    print(" OpenVoice Startup Tests")
    print("=" * 70)
    
    results = []
    results.append(("Python Version", test_python_version()))
    results.append(("Imports", test_imports()))
    results.append(("Checkpoints", test_checkpoints()))
    results.append(("Resources", test_resources()))
    results.append(("Model Loading", test_model_loading()))
    
    print("\n" + "=" * 70)
    print(" Test Summary")
    print("=" * 70)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print(" ✅ All startup tests PASSED!")
        print("=" * 70)
        return 0
    else:
        print(" ❌ Some tests FAILED")
        print("=" * 70)
        return 1

if __name__ == "__main__":
    sys.exit(main())

