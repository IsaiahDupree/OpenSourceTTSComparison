#!/usr/bin/env python3
"""Test Qwen3-TTS using direct HTTP requests"""

import requests
import json
import time

def test_qwen3_tts_http():
    """Test Qwen3-TTS using HTTP API"""
    print("=" * 70)
    print(" Testing Qwen3-TTS Voice Design (HTTP)")
    print("=" * 70)
    
    base_url = "https://qwen-qwen3-tts-voice-design.hf.space"
    api_url = f"{base_url}/api/tts_interface/"
    
    print(f"\n[1] Testing endpoint: {base_url}")
    try:
        response = requests.get(base_url, timeout=10)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print("  [OK] Endpoint accessible")
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False
    
    print("\n[2] Making API request...")
    text = "Hello! This is a test of the Qwen3-TTS voice design system."
    instruct = "A clear and natural female voice, moderate speed, stable tone."
    
    print(f"  Text: {text}")
    print(f"  Instruction: {instruct}")
    print("  (This may take 10-30 seconds...)")
    
    data = {
        "data": [text, instruct],
        "fn_index": 0  # First endpoint
    }
    
    try:
        start_time = time.time()
        response = requests.post(api_url, json=data, timeout=120)
        elapsed = time.time() - start_time
        
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n  [SUCCESS] Generated in {elapsed:.1f}s!")
            
            if "data" in result:
                audio_file = result["data"]
                print(f"  Audio file: {audio_file}")
            else:
                print(f"  Result: {result}")
            
            return True
        else:
            print(f"  [ERROR] HTTP {response.status_code}")
            print(f"  Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"  [ERROR] Request timed out after {elapsed:.1f}s")
        return False
    except Exception as e:
        print(f"  [ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_qwen3_tts_http()
    print("\n" + "=" * 70)
    if success:
        print(" [SUCCESS] Test completed!")
    else:
        print(" [FAILED] Test failed")
    print("=" * 70)
    exit(0 if success else 1)

