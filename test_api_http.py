#!/usr/bin/env python3
"""
Test OpenVoice API using direct HTTP requests (bypasses gradio_client issues)
"""

import requests
import json
import time
import os
from pathlib import Path

def test_api_http():
    """Test API using direct HTTP requests"""
    print("=" * 70)
    print(" OpenVoice API Test (HTTP Direct)")
    print("=" * 70)
    
    base_url = "http://localhost:7860"
    
    # Check if server is running
    print("\n[1] Checking server...")
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("  [OK] Server is running")
        else:
            print(f"  [ERROR] Server returned {response.status_code}")
            return False
    except Exception as e:
        print(f"  [ERROR] Cannot connect: {e}")
        return False
    
    # Get API info - try different endpoints
    print("\n[2] Getting API info...")
    api_info = None
    api_endpoints = [
        f"{base_url}/api",
        f"{base_url}/api/",
        f"{base_url}/api/predict",
    ]
    
    for api_url in api_endpoints:
        try:
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                try:
                    api_info = response.json()
                    print(f"  [OK] Found API at {api_url}")
                    if isinstance(api_info, list):
                        print(f"  [OK] Found {len(api_info)} endpoints")
                    break
                except:
                    print(f"  [INFO] {api_url} returned non-JSON, trying next...")
        except Exception as e:
            continue
    
    if not api_info:
        print("  [WARNING] Could not get API info, will try direct predict endpoint")
        # We'll proceed anyway and try the predict endpoint directly
    
    # Prepare test data
    print("\n[3] Preparing test data...")
    audio_path = Path("openvoice_deploy/resources/demo_speaker2.mp3")
    if not audio_path.exists():
        print(f"  [ERROR] Audio file not found: {audio_path}")
        return False
    
    print(f"  [OK] Using reference audio: {audio_path.name}")
    
    # Upload audio file
    print("\n[4] Uploading audio file...")
    try:
        upload_url = f"{base_url}/upload"
        with open(audio_path, 'rb') as f:
            files = {'files': (audio_path.name, f, 'audio/mpeg')}
            response = requests.post(upload_url, files=files, timeout=30)
        
        if response.status_code == 200:
            upload_result = response.json()
            audio_file_path = upload_result[0] if isinstance(upload_result, list) else upload_result.get('file', str(audio_path))
            print(f"  [OK] Audio uploaded: {audio_file_path}")
        else:
            # Fallback: use direct path
            audio_file_path = str(audio_path.resolve())
            print(f"  [WARNING] Upload failed, using direct path: {audio_file_path}")
    except Exception as e:
        print(f"  [WARNING] Upload error: {e}, using direct path")
        audio_file_path = str(audio_path.resolve())
    
    # Make prediction
    print("\n[5] Making prediction...")
    print("  Text: 'Hello, this is a test of the OpenVoice API.'")
    print("  Style: 'default'")
    print("  Reference: demo_speaker2.mp3")
    
    try:
        # Try different predict endpoint formats
        predict_endpoints = [
            f"{base_url}/api/predict/",
            f"{base_url}/api/predict",
            f"{base_url}/run/predict",
        ]
        
        # Prepare data - Gradio 3.48.0 format
        data = {
            "data": [
                "Hello, this is a test of the OpenVoice API.",
                "default",
                audio_file_path,
                True
            ],
            "fn_index": 1
        }
        
        print("  Sending request...")
        start_time = time.time()
        response = None
        
        for predict_url in predict_endpoints:
            try:
                response = requests.post(predict_url, json=data, timeout=300)
                if response.status_code == 200:
                    print(f"  [OK] Connected to {predict_url}")
                    break
                elif response.status_code != 404:
                    print(f"  [INFO] {predict_url} returned {response.status_code}, trying next...")
            except Exception as e:
                print(f"  [INFO] {predict_url} failed: {e}, trying next...")
                continue
        
        if not response or response.status_code != 200:
            print(f"  [ERROR] All predict endpoints failed")
            if response:
                print(f"  Last response: {response.status_code} - {response.text[:200]}")
            return False
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"  [OK] Request completed in {elapsed:.1f}s")
            
            if "data" in result:
                output_data = result["data"]
                info_text = output_data[0] if len(output_data) > 0 else ""
                audio_output = output_data[1] if len(output_data) > 1 else None
                
                print(f"\n  Result:")
                print(f"    Info: {info_text[:100]}...")
                if audio_output:
                    print(f"    Audio: {audio_output}")
                    print(f"  [SUCCESS] Audio generated successfully!")
                    return True
                else:
                    print(f"  [ERROR] No audio output")
                    return False
            else:
                print(f"  [ERROR] Unexpected response format: {result}")
                return False
        else:
            print(f"  [ERROR] Request failed: {response.status_code}")
            print(f"  Response: {response.text[:500]}")
            return False
    except Exception as e:
        print(f"  [ERROR] Prediction failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_api_http()
    if success:
        print("\n" + "=" * 70)
        print(" [SUCCESS] API test passed!")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print(" [FAILED] API test failed")
        print("=" * 70)
        exit(1)

