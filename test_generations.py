#!/usr/bin/env python3
"""
Test voice generation - run sample generations to verify functionality
"""

import os
import sys
from pathlib import Path
import time

def setup_paths():
    """Setup Python paths"""
    base_dir = Path(__file__).parent / "openvoice_deploy"
    base_dir = base_dir.resolve()  # Get absolute path
    if str(base_dir) not in sys.path:
        sys.path.insert(0, str(base_dir))
    openvoice_path = base_dir / "openvoice"
    if str(openvoice_path) not in sys.path:
        sys.path.insert(0, str(openvoice_path))
    original_cwd = os.getcwd()
    os.chdir(base_dir)
    return base_dir, original_cwd

def test_generation(base_dir, text, style, audio_file, test_name):
    """Test a single generation"""
    print(f"\n{'='*70}")
    print(f" Test: {test_name}")
    print(f"{'='*70}")
    print(f"  Text: {text[:50]}...")
    print(f"  Style: {style}")
    print(f"  Reference: {audio_file}")
    
    try:
        # Import predict function directly
        import importlib.util
        app_path = Path(base_dir) / "app.py"
        app_path = app_path.resolve()  # Get absolute path
        if not app_path.exists():
            raise FileNotFoundError(f"app.py not found at {app_path}")
        spec = importlib.util.spec_from_file_location("app", str(app_path))
        app_module = importlib.util.module_from_spec(spec)
        sys.modules["app"] = app_module
        spec.loader.exec_module(app_module)
        predict = app_module.predict
        
        start_time = time.time()
        result = predict(text, style, audio_file, True)
        elapsed = time.time() - start_time
        
        info_text, audio_path, ref_audio = result
        
        if "ERROR" in info_text:
            print(f"  ❌ FAILED: {info_text}")
            return False
        
        if audio_path and os.path.exists(audio_path):
            file_size = os.path.getsize(audio_path) / 1024  # KB
            print(f"  ✅ SUCCESS")
            print(f"  ⏱️  Time: {elapsed:.1f}s")
            print(f"  📁 Output: {audio_path}")
            print(f"  📊 Size: {file_size:.1f} KB")
            return True
        else:
            print(f"  ❌ FAILED: No audio generated")
            print(f"  Info: {info_text}")
            return False
            
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 70)
    print(" OpenVoice Generation Tests")
    print("=" * 70)
    
    base_dir, original_cwd = setup_paths()
    
    # Wait for models to load if needed
    print("\n[INFO] Loading models (this may take 30-60 seconds on first run)...")
    print("       Models are loaded lazily, so first generation will be slower.")
    
    # Test cases
    test_cases = [
        {
            "name": "Short English - Default Style",
            "text": "Hello, this is a test of the OpenVoice system.",
            "style": "default",
            "audio": "resources/demo_speaker2.mp3"
        },
        {
            "name": "English - Whispering Style",
            "text": "This is a whispering test.",
            "style": "whispering",
            "audio": "resources/demo_speaker2.mp3"
        },
        {
            "name": "English - Cheerful Style",
            "text": "This is a cheerful test!",
            "style": "cheerful",
            "audio": "resources/demo_speaker0.mp3"
        },
    ]
    
    results = []
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[{i}/{len(test_cases)}] Running test...")
        result = test_generation(
            base_dir,
            test_case["text"],
            test_case["style"],
            test_case["audio"],
            test_case["name"]
        )
        results.append((test_case["name"], result))
        
        # Small delay between tests
        if i < len(test_cases):
            time.sleep(2)
    
    # Restore original directory
    os.chdir(original_cwd)
    
    # Summary
    print("\n" + "=" * 70)
    print(" Generation Test Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {name}: {status}")
    
    print(f"\n  Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n" + "=" * 70)
        print(" ✅ All generation tests PASSED!")
        print("=" * 70)
        print("\n🎉 OpenVoice is working correctly!")
        return 0
    else:
        print("\n" + "=" * 70)
        print(" ⚠️  Some generation tests FAILED")
        print("=" * 70)
        return 1

if __name__ == "__main__":
    sys.exit(main())

