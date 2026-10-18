#!/usr/bin/env python3
"""
Test OpenVoice V2 with Official API Documentation
==================================================
Using the exact format from the official documentation.
"""

import os
from gradio_client import Client
from pathlib import Path

def main():
    print("=" * 70)
    print(" Testing OpenVoice V2 with Official API Format")
    print("=" * 70)
    
    token = os.getenv("HF_TOKEN", (__import__('os').environ['HF_TOKEN']))
    
    # Use the replica endpoint from official docs
    replica_url = "https://myshell-ai-openvoicev2.hf.space/--replicas/c2rsh/"
    
    print(f"\n[1] Connecting to replica endpoint...")
    print(f"    URL: {replica_url}")
    
    try:
        client = Client(replica_url, hf_token=token)
        print("  [OK] Connected successfully")
    except Exception as e:
        print(f"  [ERROR] Connection failed: {e}")
        print("  Trying standard endpoint...")
        try:
            client = Client("myshell-ai/OpenVoiceV2", hf_token=token)
            print("  [OK] Connected to standard endpoint")
        except Exception as e2:
            print(f"  [ERROR] Standard endpoint also failed: {e2}")
            return
    
    # Get reference file
    print("\n[2] Preparing reference audio...")
    ref_file = Path("processed_segments/0YWpkJkbXxs_Never lose power again. UPS UNBOXING._segment_0.wav")
    if not ref_file.exists():
        print("  [ERROR] Reference file not found")
        return
    
    print(f"  [OK] Using: {ref_file.name}")
    audio_path = str(ref_file.resolve())
    
    # Test with official API format
    print("\n[3] Testing with official API format...")
    print("  Text: 'Hello, this is a test of OpenVoice V2 using the official API format.'")
    print("  Style: en_default")
    print("  Reference: Local file path")
    print("  Agree: True")
    
    try:
        # Per official docs - use filepath directly
        result = client.predict(
            "Hello, this is a test of OpenVoice V2 using the official API format.",  # Text (under 200 chars)
            "en_default",  # Style
            audio_path,    # Reference audio (filepath)
            True,          # Agree
            fn_index=1
        )
        
        print("\n  [SUCCESS] API call completed!")
        print(f"  Result type: {type(result)}")
        print(f"  Result length: {len(result) if result else 'None'}")
        
        if result and len(result) >= 3:
            info = result[0]
            synthesised_audio = result[1]
            reference_audio_used = result[2]
            
            print(f"\n  Info: {info}")
            print(f"  Synthesised Audio: {synthesised_audio}")
            print(f"  Reference Audio Used: {reference_audio_used}")
            
            if synthesised_audio:
                print(f"\n  [SUCCESS] Generated audio path: {synthesised_audio}")
                if Path(synthesised_audio).exists():
                    size = Path(synthesised_audio).stat().st_size
                    print(f"  File size: {size:,} bytes")
                else:
                    print(f"  [INFO] File will be downloaded/copied to this location")
        else:
            print(f"  [ERROR] Unexpected result format: {result}")
            
    except ValueError as ve:
        error_msg = str(ve)
        print(f"\n  [ERROR] ValueError: {error_msg}")
        if "None" in error_msg:
            print("\n  The Space might be sleeping. Try:")
            print("  1. Visit: https://huggingface.co/spaces/myshell-ai/OpenVoiceV2")
            print("  2. Generate one audio in the UI")
            print("  3. Then try this script again")
    except Exception as e:
        print(f"\n  [ERROR] Exception: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()

