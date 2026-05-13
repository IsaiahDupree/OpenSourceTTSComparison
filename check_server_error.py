#!/usr/bin/env python3
"""
Check what error the server is actually returning
"""

import requests
import json
import sys

def check_server_error():
    """Check the actual error from the server"""
    print("=" * 70)
    print(" Checking Server Error Details")
    print("=" * 70)
    
    base_url = "http://localhost:7860"
    
    # Check if server is running
    print("\n[1] Checking if server is running...")
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("  [OK] Server is running")
        else:
            print(f"  [ERROR] Server returned {response.status_code}")
            return
    except Exception as e:
        print(f"  [ERROR] Cannot connect: {e}")
        return
    
    # Try to make a prediction and capture the full error
    print("\n[2] Attempting prediction to capture error...")
    
    # Get a test audio file
    import os
    from pathlib import Path
    audio_path = Path("openvoice_deploy/resources/demo_speaker2.mp3")
    if not audio_path.exists():
        print(f"  [ERROR] Test audio not found: {audio_path}")
        return
    
    # Try different API endpoints
    endpoints = [
        f"{base_url}/api/predict/",
        f"{base_url}/api/predict",
        f"{base_url}/run/predict",
    ]
    
    data = {
        "data": [
            "Hello, this is a test.",
            "default",
            str(audio_path.resolve()),
            True
        ],
        "fn_index": 1
    }
    
    for endpoint in endpoints:
        print(f"\n  Trying: {endpoint}")
        try:
            response = requests.post(endpoint, json=data, timeout=30)
            print(f"    Status: {response.status_code}")
            print(f"    Headers: {dict(response.headers)}")
            
            if response.status_code == 500:
                print(f"    Error Response:")
                try:
                    error_data = response.json()
                    print(f"      JSON: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"      Text: {response.text[:500]}")
            
            if response.status_code == 200:
                print(f"    [SUCCESS] Request succeeded!")
                result = response.json()
                print(f"    Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
                return True
                
        except Exception as e:
            print(f"    [ERROR] {e}")
            import traceback
            traceback.print_exc()
    
    print("\n[3] Checking server logs location...")
    print("  Note: Server logs should be visible in the server window")
    print("  Look for error messages starting with [ERROR] or tracebacks")
    
    return False

if __name__ == "__main__":
    success = check_server_error()
    if not success:
        print("\n" + "=" * 70)
        print(" [INFO] Check the server window for detailed error messages")
        print("=" * 70)
        print("\nThe server window should show:")
        print("  - Python tracebacks")
        print("  - [ERROR] messages")
        print("  - [WARNING] messages")
        print("\nPlease check the server window and share any error messages you see.")

