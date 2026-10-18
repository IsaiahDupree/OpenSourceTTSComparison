#!/usr/bin/env python3
"""Simple test of OpenVoice V2 - quick connection check"""

from gradio_client import Client
import os
import time
import requests

endpoint = "https://myshell-ai-openvoicev2.hf.space/--replicas/c2rsh/"
token = os.getenv("HF_TOKEN", (__import__('os').environ['HF_TOKEN']))

print("=" * 70)
print(" OpenVoice V2 Quick Test")
print("=" * 70)

print(f"\n[1] Connecting to: {endpoint}")
try:
    client = Client(endpoint, hf_token=token)
    print("  [OK] Connected!")
except Exception as e:
    print(f"  [ERROR] {e}")
    exit(1)

print("\n[2] Testing API call with retry logic...")
print("  Text: 'Howdy! This is a test.'")
print("  Style: 'en_default'")
print("  Audio: Using demo audio URL")
print("  (This may take 30-180 seconds for cold start...)")

# Retry logic with exponential backoff
import time
import requests

retry_delays = [5, 10, 20, 30, 45, 60]
max_retries = len(retry_delays)
space_url = "https://myshell-ai-openvoicev2.hf.space/--replicas/c2rsh/"

for attempt in range(max_retries):
    try:
        # Wake up the Space by pinging it
        if attempt > 0:
            print(f"\n  [RETRY {attempt}/{max_retries-1}] Waiting {retry_delays[attempt-1]}s, then pinging Space...")
            time.sleep(retry_delays[attempt-1])
            try:
                wake_response = requests.get(space_url, timeout=10)
                print(f"  [OK] Space ping: HTTP {wake_response.status_code}")
            except:
                print(f"  [WARNING] Space ping failed, continuing anyway...")
        
        print(f"\n  [ATTEMPT {attempt+1}/{max_retries}] Submitting request...")
        job = client.submit(
            "Howdy! This is a test.",
            "en_default",
            "https://github.com/gradio-app/gradio/raw/main/test/test_files/audio_sample.wav",
            True,
            fn_index=1
        )
        
        print("  [OK] Request submitted, waiting for result...")
        print("  (This may take 30-180 seconds, especially on first request)")
        
        # Use longer timeout for cold starts
        timeout = 300 if attempt == 0 else 180
        result = job.result(timeout=timeout)
        
        info, audio, ref = result
        print(f"\n  [SUCCESS] Completed!")
        print(f"  Info: {info[:200]}")
        print(f"  Output Audio: {audio}")
        print(f"  Reference: {ref}")
        break  # Success, exit retry loop
        
    except ValueError as e:
        error_msg = str(e)
        if error_msg == "None" or "None" in error_msg:
            if attempt < max_retries - 1:
                print(f"  [WARNING] Cold start/overload detected (ValueError: None)")
                print(f"  Will retry in {retry_delays[attempt]} seconds...")
                continue
            else:
                print(f"\n  [ERROR] All retries exhausted. Space may be overloaded or down.")
                print(f"  Error: {error_msg}")
                raise
        else:
            print(f"\n  [ERROR] {error_msg}")
            raise
    except KeyboardInterrupt:
        print("\n  [CANCELED] Test interrupted by user")
        break
    except Exception as e:
        error_msg = str(e)
        if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
            if attempt < max_retries - 1:
                print(f"  [WARNING] Request timed out")
                print(f"  Will retry in {retry_delays[attempt]} seconds...")
                continue
            else:
                print(f"\n  [ERROR] Request timed out after all retries")
                raise
        else:
            print(f"\n  [ERROR] {error_msg}")
            import traceback
            traceback.print_exc()
            raise

print("\n" + "=" * 70)

