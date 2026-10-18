#!/usr/bin/env python3
"""Test Qwen3-TTS with upgraded gradio_client and retry logic"""

from gradio_client import Client
import os
import time
import requests

def test_qwen3_tts():
    """Test Qwen3-TTS Voice Design API"""
    print("=" * 70)
    print(" Testing Qwen3-TTS Voice Design API")
    print("=" * 70)
    
    space_id = "Qwen/Qwen3-TTS-Voice-Design"
    token = os.getenv("HF_TOKEN", (__import__('os').environ['HF_TOKEN']))
    base_url = "https://qwen-qwen3-tts-voice-design.hf.space"
    
    print(f"\n[1] Connecting to: {space_id}")
    
    # Wake up the Space first
    print("  Waking up Space...")
    try:
        wake_response = requests.get(base_url, timeout=10)
        print(f"  [OK] Space ping: HTTP {wake_response.status_code}")
    except:
        print("  [WARNING] Space ping failed, continuing...")
    
    try:
        client = Client(space_id, hf_token=token)
        print("  [OK] Connected successfully!")
    except Exception as e:
        print(f"  [ERROR] Connection failed: {e}")
        return False
    
    print("\n[2] Testing voice generation...")
    text = "Hello! This is a test of the Qwen3-TTS voice design system."
    instruct = "A clear and natural female voice, moderate speed, stable tone."
    
    print(f"  Text: {text}")
    print(f"  Instruction: {instruct}")
    print("  (This may take 10-30 seconds...)")
    
    # Try with retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                print(f"\n  [RETRY {attempt}] Waiting 5 seconds...")
                time.sleep(5)
                # Wake up again
                try:
                    requests.get(base_url, timeout=5)
                except:
                    pass
            
            print(f"  [ATTEMPT {attempt+1}/{max_retries}] Submitting request...")
            
            # Use submit() with longer timeout
            job = client.submit(
                text,
                instruct,
                api_name="/tts_interface"
            )
            
            print("  [OK] Request submitted, waiting for result...")
            result = job.result(timeout=180)  # 3 minute timeout
            
            print(f"\n  [SUCCESS] Generated!")
            print(f"  Audio file: {result}")
            return True
            
        except Exception as e:
            error_msg = str(e)
            if "WebSocket" in error_msg or "websocket" in error_msg.lower():
                if attempt < max_retries - 1:
                    print(f"  [WARNING] WebSocket error: {error_msg[:100]}")
                    print(f"  Will retry...")
                    continue
                else:
                    print(f"\n  [ERROR] WebSocket connection failed after {max_retries} attempts")
                    print(f"  This is a known issue with gradio_client and newer Gradio versions")
                    print(f"  Error: {error_msg}")
                    return False
            else:
                print(f"\n  [ERROR] {error_msg}")
                import traceback
                traceback.print_exc()
                return False
    
    return False

if __name__ == "__main__":
    success = test_qwen3_tts()
    print("\n" + "=" * 70)
    if success:
        print(" [SUCCESS] Test completed!")
    else:
        print(" [FAILED] Test failed - WebSocket connection issue")
        print("  Note: This is a gradio_client compatibility issue")
        print("  The API works in the browser, but gradio_client has WebSocket issues")
    print("=" * 70)
    exit(0 if success else 1)

