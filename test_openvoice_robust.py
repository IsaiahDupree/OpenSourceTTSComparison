#!/usr/bin/env python3
"""
Robust OpenVoice V2 Test
========================
Using best practices: canonical Space ID, handle_file(), wake + retry loop.
Based on: https://github.com/myshell-ai/OpenVoice
"""

import os
import time
import requests
from pathlib import Path
from gradio_client import Client, handle_file

SPACE_ID = "myshell-ai/OpenVoiceV2"

# Real runtime URL (the actual app, not the Hub page)
SPACE_SUBDOMAIN = SPACE_ID.replace("/", "-").lower()  # myshell-ai-openvoicev2
SPACE_APP_URL = f"https://{SPACE_SUBDOMAIN}.hf.space/"

def wake_space():
    """Wake up Space by pinging the actual app domain"""
    try:
        r = requests.get(SPACE_APP_URL, timeout=15)
        print(f"  [WAKE] {SPACE_APP_URL} -> HTTP {r.status_code}")
    except Exception as e:
        print(f"  [WAKE WARNING] {e}")

def main():
    print("=" * 70)
    print(" Robust OpenVoice V2 Test")
    print("=" * 70)
    
    token = os.getenv("HF_TOKEN", (__import__('os').environ['HF_TOKEN']))
    
    # Get reference file
    ref_file = Path("processed_segments/0YWpkJkbXxs_Never lose power again. UPS UNBOXING._segment_0.wav")
    if not ref_file.exists():
        print(f"\n[ERROR] Reference file not found: {ref_file}")
        return
    
    print(f"\n[1] Reference file: {ref_file.name}")
    
    # Initialize client with canonical Space ID
    print(f"\n[2] Connecting to Space: {SPACE_ID}")
    try:
        client = Client(SPACE_ID, hf_token=token)
        print("  [OK] Connected")
    except Exception as e:
        print(f"  [ERROR] Connection failed: {e}")
        return
    
    # View API to see available endpoints
    print("\n[3] Checking API endpoints...")
    try:
        client.view_api()
        print("  [OK] API endpoints available")
    except Exception as e:
        print(f"  [WARNING] Could not view API: {e}")
    
    # IMPORTANT: Upload local file using handle_file()
    print("\n[4] Uploading reference audio...")
    ref_audio = handle_file(str(ref_file.resolve()))
    print("  [OK] File uploaded via handle_file()")
    
    # Test parameters
    text = "Hello, this is a test of OpenVoice V2 using the robust method."
    style = "en_default"  # or en_us, en_br, en_au, en_in
    
    print(f"\n[5] Calling API...")
    print(f"  Text: {text}")
    print(f"  Style: {style}")
    
    # Retry loop with exponential backoff
    # ValueError: None is NOT "asleep" - it's cold start/overload/crash
    # Cold starts can take 30-180s, so use longer timeout
    backoffs = [5, 10, 20, 30, 45, 60]
    last_err = None
    
    for attempt, sleep_s in enumerate(backoffs, start=1):
        try:
            print(f"\n  Attempt {attempt}/{len(backoffs)} (timeout=300s)...")
            
            # Use submit().result() instead of predict() for better timeout handling
            # Try api_name first (more stable), fallback to fn_index
            try:
                job = client.submit(
                    text,
                    style,
                    ref_audio,
                    True,
                    api_name="/predict"
                )
            except:
                # Fallback to fn_index if api_name doesn't work
                job = client.submit(
                    text,
                    style,
                    ref_audio,
                    True,
                    fn_index=1
                )
            
            # Wait with longer timeout for cold starts
            result = job.result(timeout=300)
            print(f"  [SUCCESS] API call completed!")
            break
            
        except ValueError as ve:
            # ValueError: None is NOT "asleep" - it's cold start/overload/crash
            last_err = ve
            print(f"  [FAIL] ValueError: {ve}")
            if attempt < len(backoffs):
                print(f"  Waking + waiting {sleep_s}s...")
                wake_space()
                time.sleep(sleep_s)
                continue
            else:
                raise RuntimeError(f"Space call never succeeded. Last error: {last_err}")
        except Exception as e:
            last_err = e
            print(f"  [FAIL] {type(e).__name__}: {e}")
            if attempt < len(backoffs):
                print(f"  Waking + waiting {sleep_s}s...")
                wake_space()
                time.sleep(sleep_s)
                continue
            else:
                raise RuntimeError(f"Space call never succeeded. Last error: {last_err}")
    
    # Process result
    if result:
        print(f"\n[6] Result received:")
        print(f"  Type: {type(result)}")
        print(f"  Length: {len(result) if result else 'None'}")
        
        if len(result) >= 3:
            info = result[0]
            synthesised_audio = result[1]
            reference_audio_used = result[2]
            
            print(f"\n  Info: {info}")
            print(f"  Synthesised Audio: {synthesised_audio}")
            print(f"  Reference Audio Used: {reference_audio_used}")
            
            if synthesised_audio:
                print(f"\n  [SUCCESS] Generated audio: {synthesised_audio}")
                if Path(synthesised_audio).exists():
                    size = Path(synthesised_audio).stat().st_size
                    print(f"  File size: {size:,} bytes")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()

