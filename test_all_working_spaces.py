#!/usr/bin/env python3
"""
Test All Working Voice Cloning Spaces
=====================================
Test the 4 working spaces we found to see which ones actually work.
"""

import os
import sys
from pathlib import Path
from gradio_client import Client, handle_file
import time

# Add pubsub to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_openvoice_v1(token):
    """Test original OpenVoice (not V2)"""
    print("\n" + "=" * 70)
    print(" Testing: myshell-ai/OpenVoice (V1)")
    print("=" * 70)
    
    try:
        client = Client("myshell-ai/OpenVoice", hf_token=token)
        print("[OK] Connected")
        
        # Get reference file
        ref_file = Path("processed_segments/0YWpkJkbXxs_Never lose power again. UPS UNBOXING._segment_0.wav")
        if not ref_file.exists():
            print("[ERROR] Reference file not found")
            return False
        
        print(f"[OK] Using reference: {ref_file.name}")
        
        # Test API call
        print("[INFO] Calling API...")
        audio_file = handle_file(str(ref_file.resolve()))
        
        result = client.predict(
            "Hello, this is a test of OpenVoice version one.",
            "default",  # Different style options than V2
            audio_file,
            True,
            fn_index=1
        )
        
        if result and len(result) >= 2:
            audio_path = result[1]
            print(f"[SUCCESS] Generated audio: {audio_path}")
            return True
        else:
            print(f"[ERROR] Invalid result: {result}")
            return False
            
    except ValueError as ve:
        if "None" in str(ve):
            print(f"[ERROR] API returned None (Space might be sleeping)")
        else:
            print(f"[ERROR] ValueError: {ve}")
        return False
    except Exception as e:
        print(f"[ERROR] Exception: {e}")
        return False

def test_voicecloning_be(token):
    """Test VoiceCloning-be/text-to-speech"""
    print("\n" + "=" * 70)
    print(" Testing: VoiceCloning-be/text-to-speech")
    print("=" * 70)
    
    try:
        client = Client("VoiceCloning-be/text-to-speech", hf_token=token)
        print("[OK] Connected")
        
        # This one uses pre-made voices, not voice cloning
        print("[INFO] This space uses pre-made voices (not voice cloning)")
        print("[INFO] Testing with default voice...")
        
        result = client.predict(
            "Hello, this is a test of the text to speech system.",
            "",  # Empty voice = default
            0,   # rate
            0,   # pitch
            api_name="/predict"
        )
        
        if result and len(result) >= 1:
            audio_path = result[0]
            print(f"[SUCCESS] Generated audio: {audio_path}")
            return True
        else:
            print(f"[ERROR] Invalid result: {result}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Exception: {e}")
        return False

def test_kikirilkov(token):
    """Test Kikirilkov/Voice_Cloning"""
    print("\n" + "=" * 70)
    print(" Testing: Kikirilkov/Voice_Cloning")
    print("=" * 70)
    
    try:
        client = Client("Kikirilkov/Voice_Cloning", hf_token=token)
        print("[OK] Connected")
        
        # This one uses spectrograms - different format
        print("[INFO] This space uses spectrograms (different format)")
        print("[WARNING] Would need spectrogram input, skipping detailed test")
        return None  # Can't test without proper input format
        
    except Exception as e:
        print(f"[ERROR] Exception: {e}")
        return False

def main():
    token = os.getenv("HF_TOKEN", (__import__('os').environ['HF_TOKEN']))
    
    print("=" * 70)
    print(" Testing All Working Voice Cloning Spaces")
    print("=" * 70)
    print(f"\nToken: {token[:10]}...{token[-5:]}")
    
    results = {}
    
    # Test 1: OpenVoice V1
    results['OpenVoice V1'] = test_openvoice_v1(token)
    time.sleep(2)
    
    # Test 2: VoiceCloning-be
    results['VoiceCloning-be'] = test_voicecloning_be(token)
    time.sleep(2)
    
    # Test 3: Kikirilkov (info only)
    results['Kikirilkov'] = test_kikirilkov(token)
    
    # Summary
    print("\n" + "=" * 70)
    print(" Test Results Summary")
    print("=" * 70)
    
    for name, result in results.items():
        if result is True:
            print(f"  ✅ {name}: WORKING")
        elif result is False:
            print(f"  ❌ {name}: FAILED")
        else:
            print(f"  ⚠️  {name}: SKIPPED (different format)")
    
    # Recommendations
    print("\n" + "=" * 70)
    print(" Recommendations")
    print("=" * 70)
    
    working = [name for name, result in results.items() if result is True]
    
    if working:
        print(f"\n✅ Working spaces: {', '.join(working)}")
        print("  You can use these in your pub/sub system!")
    else:
        print("\n⚠️  No spaces worked in this test")
        print("  They might need to be woken up via UI first")
        print("  Or there might be rate limiting/authentication issues")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()

