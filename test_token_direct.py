#!/usr/bin/env python3
"""
Direct Token Test
=================
Test the token with a simple API call to see what happens.
"""

import os
from gradio_client import Client, handle_file
from pathlib import Path

def main():
    token = os.getenv("HF_TOKEN", (__import__('os').environ['HF_TOKEN']))
    
    print("=" * 70)
    print(" Direct Token Test")
    print("=" * 70)
    
    print(f"\nToken: {token[:10]}...{token[-5:]}")
    
    # Test 1: Basic connection
    print("\n[1] Testing Space connection...")
    try:
        client = Client("myshell-ai/OpenVoiceV2", hf_token=token)
        print("  [OK] Connected successfully")
    except Exception as e:
        print(f"  [ERROR] Connection failed: {e}")
        return
    
    # Test 2: Get reference file
    print("\n[2] Preparing test file...")
    segments_dir = Path("processed_segments")
    if not segments_dir.exists():
        print("  [ERROR] processed_segments not found")
        return
    
    wav_files = list(segments_dir.glob("*.wav"))
    if not wav_files:
        print("  [ERROR] No WAV files found")
        return
    
    ref_file = wav_files[0]
    print(f"  Using: {ref_file.name}")
    
    # Test 3: Try API call with longer timeout
    print("\n[3] Attempting API call (this may take 30-60 seconds)...")
    print("  Text: 'Hello, this is a test of voice cloning.'")
    print("  Style: en_default")
    
    try:
        audio_file = handle_file(str(ref_file.resolve()))
        print("  [OK] File handle created")
        
        # Try without api_name
        print("  Calling API (without api_name parameter)...")
        result = client.predict(
            "Hello, this is a test of voice cloning.",
            "en_default",
            audio_file,
            True,  # agree
            fn_index=1
        )
        
        print(f"  [SUCCESS] API call completed!")
        print(f"  Result type: {type(result)}")
        if result:
            print(f"  Result length: {len(result)}")
            if len(result) >= 2:
                print(f"  Audio path: {result[1]}")
                if result[1]:
                    print(f"  [SUCCESS] Generated audio: {result[1]}")
        
    except ValueError as ve:
        error_msg = str(ve)
        print(f"  [ERROR] ValueError: {error_msg}")
        if "None" in error_msg:
            print("\n  This 'None' error typically means:")
            print("    - The Space needs to be woken up (visit the UI first)")
            print("    - The Space is having issues")
            print("    - Rate limiting is active")
            print("    - The request format might be incorrect")
            print("\n  Try visiting: https://huggingface.co/spaces/myshell-ai/OpenVoiceV2")
            print("  And using the UI to generate one audio first, then try API again")
    except Exception as e:
        print(f"  [ERROR] Exception: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()

