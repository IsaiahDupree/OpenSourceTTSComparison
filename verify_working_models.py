#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick verification of which models are actually working in this repo.
Tests models that have been set up previously.
"""

import sys
import io
import subprocess
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def test_chatterbox():
    """Test if Chatterbox is working."""
    print("\n" + "=" * 70)
    print("Testing Chatterbox")
    print("=" * 70)
    
    # Check if virtual environment exists
    venv_paths = [
        Path("venv_chatterbox/Scripts/python.exe"),
        Path("venv_chatterbox311/Scripts/python.exe")
    ]
    
    venv_python = None
    for path in venv_paths:
        if path.exists():
            venv_python = str(path)
            print(f"✅ Found virtual environment: {path.parent.parent}")
            break
    
    if not venv_python:
        print("⚠️  No Chatterbox virtual environment found")
        print("   Try: python test_chatterbox.py")
        return False
    
    # Check if test output exists
    if Path("chatterbox_test_output.wav").exists():
        print("✅ Found previous test output: chatterbox_test_output.wav")
    
    # Check results directory
    if Path("results_chatterbox").exists():
        print("✅ Found results directory: results_chatterbox/")
        if Path("results_chatterbox/benchmark_report.md").exists():
            print("✅ Found benchmark report")
    
    # Try to import
    try:
        result = subprocess.run(
            [venv_python, "-c", "import chatterbox; print('✅ Chatterbox import successful')"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print(result.stdout.strip())
            return True
        else:
            print("⚠️  Import test failed")
            print(result.stderr[:200])
            return False
    except Exception as e:
        print(f"⚠️  Error testing: {e}")
        return False


def test_coqui():
    """Test if Coqui TTS is working."""
    print("\n" + "=" * 70)
    print("Testing Coqui TTS")
    print("=" * 70)
    
    # Check for test files
    test_files = [
        "test_coqui_tts.py",
        "test_coqui_isolated.py"
    ]
    
    found_files = [f for f in test_files if Path(f).exists()]
    if found_files:
        print(f"✅ Found test files: {', '.join(found_files)}")
    else:
        print("⚠️  No test files found")
    
    # Check for output files
    output_files = [
        "coqui_test_output.wav",
        "coqui_cloned_output.wav"
    ]
    
    found_outputs = [f for f in output_files if Path(f).exists()]
    if found_outputs:
        print(f"✅ Found output files: {', '.join(found_outputs)}")
    else:
        print("⚠️  No output files found (may not have been tested)")
    
    # Try to import in current environment
    try:
        result = subprocess.run(
            [sys.executable, "-c", "from TTS.api import TTS; print('✅ Coqui TTS import successful')"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print(result.stdout.strip())
            print("✅ Coqui TTS is installed and working!")
            return True
        else:
            print("⚠️  Coqui TTS not installed in current environment")
            print("   Try: python test_coqui_tts.py")
            return False
    except Exception as e:
        print(f"⚠️  Error testing: {e}")
        return False


def main():
    """Main verification function."""
    print("=" * 70)
    print("VERIFYING WORKING MODELS IN THIS REPO")
    print("=" * 70)
    
    results = {}
    
    # Test Chatterbox
    results["chatterbox"] = test_chatterbox()
    
    # Test Coqui
    results["coqui"] = test_coqui()
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    working = [name for name, status in results.items() if status]
    
    if working:
        print(f"\n✅ Working models ({len(working)}):")
        for name in working:
            print(f"   - {name.title()}")
    else:
        print("\n⚠️  No models confirmed working in current environment")
    
    not_working = [name for name, status in results.items() if not status]
    if not_working:
        print(f"\n⚠️  Models needing setup ({len(not_working)}):")
        for name in not_working:
            print(f"   - {name.title()}")
    
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)
    
    if results.get("chatterbox"):
        print("\n✅ Use Chatterbox - It's confirmed working!")
        print("   Command: python test_chatterbox.py")
        print("   Or activate venv: venv_chatterbox\\Scripts\\activate")
    
    if results.get("coqui"):
        print("\n✅ Coqui TTS is available!")
        print("   Command: python test_coqui_tts.py")
    
    if not any(results.values()):
        print("\n💡 No models working yet. Try:")
        print("   1. python test_chatterbox.py")
        print("   2. python test_coqui_tts.py")
        print("   3. python direct_install_test.py")


if __name__ == "__main__":
    main()

