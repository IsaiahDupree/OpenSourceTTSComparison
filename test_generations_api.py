#!/usr/bin/env python3
"""
Test voice generation using Gradio API client - faster and more reliable
"""

import time
import requests
from gradio_client import Client

def test_api_connection():
    """Test if the API is accessible"""
    print("=" * 70)
    print(" OpenVoice Generation Tests (via API)")
    print("=" * 70)
    
    print("\n[1] Checking if server is running...")
    try:
        response = requests.get("http://localhost:7860", timeout=5)
        if response.status_code == 200:
            print("  ✅ Server is running")
        else:
            print(f"  ❌ Server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("  ❌ Cannot connect to server")
        print("  Make sure OpenVoice is running: python run_openvoice_local.py")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False
    
    return True

def test_generation(client, text, style, audio_file, test_name):
    """Test a single generation via API"""
    print(f"\n{'='*70}")
    print(f" Test: {test_name}")
    print(f"{'='*70}")
    print(f"  Text: {text[:60]}...")
    print(f"  Style: {style}")
    print(f"  Reference: {audio_file}")
    
    try:
        from gradio_client import handle_file
        
        # Get full path to audio file
        import os
        from pathlib import Path
        audio_path = Path("openvoice_deploy") / audio_file
        if not audio_path.exists():
            print(f"  ❌ Audio file not found: {audio_path}")
            return False
        
        print(f"  Submitting request...")
        start_time = time.time()
        
        result = client.predict(
            prompt=text,
            style=style,
            audio_file_pth=handle_file(str(audio_path)),
            agree=True,
            api_name="/predict"
        )
        
        elapsed = time.time() - start_time
        
        info_text, audio_path_result, ref_audio = result
        
        if "ERROR" in info_text:
            print(f"  ❌ FAILED")
            print(f"  Error: {info_text}")
            return False
        
        if audio_path_result:
            if isinstance(audio_path_result, str):
                if os.path.exists(audio_path_result):
                    file_size = os.path.getsize(audio_path_result) / 1024  # KB
                    print(f"  ✅ SUCCESS")
                    print(f"  ⏱️  Time: {elapsed:.1f}s")
                    print(f"  📁 Output: {audio_path_result}")
                    print(f"  📊 Size: {file_size:.1f} KB")
                    return True
                else:
                    print(f"  ⚠️  Generated (path: {audio_path_result})")
                    print(f"  ⏱️  Time: {elapsed:.1f}s")
                    return True
            else:
                print(f"  ✅ SUCCESS (audio object returned)")
                print(f"  ⏱️  Time: {elapsed:.1f}s")
                return True
        else:
            print(f"  ❌ FAILED: No audio generated")
            print(f"  Info: {info_text}")
            return False
            
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    if not test_api_connection():
        return 1
    
    print("\n[2] Connecting to Gradio API...")
    try:
        client = Client("http://localhost:7860")
        print("  ✅ Connected to API")
    except Exception as e:
        print(f"  ❌ Failed to connect: {e}")
        return 1
    
    # Test cases
    test_cases = [
        {
            "name": "Short English - Default Style",
            "text": "Hello, this is a test of the OpenVoice system.",
            "style": "default",
            "audio": "resources/demo_speaker2.mp3"
        },
        {
            "name": "English - Whispering Style",
            "text": "This is a whispering test.",
            "style": "whispering",
            "audio": "resources/demo_speaker2.mp3"
        },
        {
            "name": "English - Cheerful Style",
            "text": "This is a cheerful test!",
            "style": "cheerful",
            "audio": "resources/demo_speaker0.mp3"
        },
    ]
    
    print(f"\n[3] Running {len(test_cases)} generation tests...")
    print("     Note: First generation may take 30-60 seconds (model loading)")
    
    results = []
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[{i}/{len(test_cases)}] Running test...")
        result = test_generation(
            client,
            test_case["text"],
            test_case["style"],
            test_case["audio"],
            test_case["name"]
        )
        results.append((test_case["name"], result))
        
        # Small delay between tests
        if i < len(test_cases):
            time.sleep(2)
    
    # Summary
    print("\n" + "=" * 70)
    print(" Generation Test Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {name}: {status}")
    
    print(f"\n  Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n" + "=" * 70)
        print(" ✅ All generation tests PASSED!")
        print("=" * 70)
        print("\n🎉 OpenVoice is working correctly!")
        return 0
    else:
        print("\n" + "=" * 70)
        print(" ⚠️  Some generation tests FAILED")
        print("=" * 70)
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())

