#!/usr/bin/env python3
"""
Diagnose OpenVoice API Issues
==============================
Check what's wrong with the OpenVoice API connection.
"""

import os
import sys
from gradio_client import Client, handle_file
from pathlib import Path

def main():
    print("=" * 70)
    print(" OpenVoice API Diagnosis")
    print("=" * 70)
    
    token = os.getenv("HF_TOKEN", __import__('os').environ['HF_TOKEN'])
    
    print("\n[1] Testing connection...")
    try:
        client = Client("myshell-ai/OpenVoiceV2", hf_token=token)
        print("  [OK] Connected to Space")
    except Exception as e:
        print(f"  [ERROR] Connection failed: {e}")
        return
    
    print("\n[2] Checking API endpoints...")
    try:
        api_info = client.view_api()
        print("  [OK] API info retrieved")
    except Exception as e:
        print(f"  [ERROR] Failed to get API info: {e}")
    
    print("\n[3] Testing with a simple request...")
    
    # Find a reference file
    segments_dir = Path("processed_segments")
    if not segments_dir.exists():
        print("  [ERROR] processed_segments not found")
        return
    
    wav_files = list(segments_dir.glob("*.wav"))
    if not wav_files:
        print("  [ERROR] No WAV files found")
        return
    
    ref_file = wav_files[0]
    print(f"  Using reference: {ref_file.name}")
    
    try:
        # Try the API call
        audio_file = handle_file(str(ref_file.resolve()))
        print("  [OK] File handle created")
        
        print("  Calling API (this may take a moment)...")
        result = client.predict(
            "Test message",
            "en_default",
            audio_file,
            True,
            fn_index=1
        )
        
        print(f"  [SUCCESS] API call completed!")
        print(f"  Result type: {type(result)}")
        print(f"  Result length: {len(result) if result else 'None'}")
        
        if result and len(result) >= 2:
            print(f"  Audio path: {result[1]}")
        
    except ValueError as ve:
        if "None" in str(ve):
            print(f"  [ERROR] API returned None error")
            print(f"  This usually means:")
            print(f"    1. The Space is down or having issues")
            print(f"    2. Rate limiting is active")
            print(f"    3. Authentication/permission issues")
            print(f"    4. The Space requires different parameters")
        else:
            print(f"  [ERROR] ValueError: {ve}")
    except Exception as e:
        print(f"  [ERROR] Exception: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n[4] Recommendations:")
    print("  - Check Space status: https://huggingface.co/spaces/myshell-ai/OpenVoiceV2")
    print("  - Verify token permissions at: https://huggingface.co/settings/tokens")
    print("  - Check billing/credits: https://huggingface.co/settings/billing")
    print("  - Try accessing the Space UI directly to see if it works there")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()

