#!/usr/bin/env python3
"""Test local OpenVoice using direct HTTP requests (bypass gradio_client)"""

import requests
import json
import time
from pathlib import Path

def test_local_http():
    """Test local server with direct HTTP"""
    print("=" * 70)
    print(" Testing Local OpenVoice via HTTP (Bypass gradio_client)")
    print("=" * 70)
    
    base_url = "http://localhost:7860"
    
    # Check server
    print("\n[1] Checking server...")
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("  [OK] Server is running")
        else:
            print(f"  [ERROR] Server returned {response.status_code}")
            return False
    except:
        print("  [ERROR] Server not running")
        return False
    
    # Get audio file
    print("\n[2] Preparing audio file...")
    audio_path = Path("openvoice_deploy/resources/demo_speaker2.mp3")
    if not audio_path.exists():
        print(f"  [ERROR] Audio file not found: {audio_path}")
        return False
    
    print(f"  [OK] Using: {audio_path.name}")
    
    # Try to upload audio first
    print("\n[3] Uploading audio file...")
    try:
        upload_url = f"{base_url}/upload"
        with open(audio_path, 'rb') as f:
            files = {'files': (audio_path.name, f, 'audio/mpeg')}
            upload_response = requests.post(upload_url, files=files, timeout=30)
        
        if upload_response.status_code == 200:
            upload_result = upload_response.json()
            audio_file = upload_result[0] if isinstance(upload_result, list) else str(audio_path.resolve())
            print(f"  [OK] Audio uploaded: {audio_file}")
        else:
            audio_file = str(audio_path.resolve())
            print(f"  [INFO] Upload failed, using direct path: {audio_file}")
    except Exception as e:
        audio_file = str(audio_path.resolve())
        print(f"  [INFO] Using direct path: {audio_file}")
    
    # Make prediction
    print("\n[4] Making prediction...")
    text = "Hello! This is a test using direct HTTP requests."
    style = "default"
    
    print(f"  Text: {text}")
    print(f"  Style: {style}")
    print(f"  Audio: {audio_file}")
    print("  (This may take 30-60 seconds for model loading...)")
    
    # Try different endpoint formats
    endpoints = [
        f"{base_url}/api/predict/",
        f"{base_url}/run/predict",
        f"{base_url}/api/predict",
    ]
    
    data = {
        "data": [text, style, audio_file, True],
        "fn_index": 1
    }
    
    success = False
    for endpoint in endpoints:
        try:
            print(f"\n  Trying: {endpoint}")
            start_time = time.time()
            response = requests.post(endpoint, json=data, timeout=300)
            elapsed = time.time() - start_time
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"  [SUCCESS] Generated in {elapsed:.1f}s!")
                
                if "data" in result:
                    info, audio_output, ref_audio = result["data"]
                    print(f"  Info: {info[:100]}...")
                    print(f"  Output Audio: {audio_output}")
                    print(f"  Reference: {ref_audio}")
                    success = True
                    break
                else:
                    print(f"  Response: {result}")
            else:
                print(f"  Response: {response.text[:200]}")
        except requests.exceptions.Timeout:
            print(f"  [ERROR] Request timed out after {elapsed:.1f}s")
        except Exception as e:
            print(f"  [ERROR] {e}")
    
    if success:
        print("\n" + "=" * 70)
        print(" [SUCCESS] HTTP API works!")
        print("=" * 70)
        return True
    else:
        print("\n" + "=" * 70)
        print(" [FAILED] HTTP API also failed")
        print("=" * 70)
        print("\nThe server is likely crashing when processing requests.")
        print("Check the server window for error messages.")
        return False

if __name__ == "__main__":
    test_local_http()

