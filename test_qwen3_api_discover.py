#!/usr/bin/env python3
"""Discover Qwen3-TTS API endpoints"""

import requests

base_url = "https://qwen-qwen3-tts-voice-design.hf.space"

# Try different API paths
endpoints = [
    f"{base_url}/api/",
    f"{base_url}/api/predict/",
    f"{base_url}/api/tts_interface/",
    f"{base_url}/api/tts_interface",
    f"{base_url}/run/tts_interface/",
]

print("=" * 70)
print(" Discovering Qwen3-TTS API Endpoints")
print("=" * 70)

for endpoint in endpoints:
    print(f"\nTrying: {endpoint}")
    try:
        # Try GET first
        response = requests.get(endpoint, timeout=5)
        print(f"  GET Status: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"  [OK] JSON response: {json.dumps(data, indent=2)[:200]}")
            except:
                print(f"  Response: {response.text[:200]}")
        
        # Try POST with minimal data
        response = requests.post(endpoint, json={"data": ["test", "test"]}, timeout=5)
        print(f"  POST Status: {response.status_code}")
        if response.status_code != 404:
            print(f"  Response: {response.text[:200]}")
    except Exception as e:
        print(f"  [ERROR] {e}")

print("\n" + "=" * 70)

