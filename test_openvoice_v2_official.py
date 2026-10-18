#!/usr/bin/env python3
"""
Test the official OpenVoice V2 API from Hugging Face
"""

import os
from gradio_client import Client
from pathlib import Path

def test_openvoice_v2():
    """Test the official OpenVoice V2 API"""
    print("=" * 70)
    print(" Testing Official OpenVoice V2 API")
    print("=" * 70)
    
    # Use the official replica endpoint
    endpoint = "https://myshell-ai-openvoicev2.hf.space/--replicas/c2rsh/"
    hf_token = os.getenv("HF_TOKEN", (__import__('os').environ['HF_TOKEN']))
    
    print(f"\n[1] Connecting to: {endpoint}")
    try:
        client = Client(endpoint, hf_token=hf_token)
        print("  [OK] Connected successfully")
    except Exception as e:
        print(f"  [ERROR] Connection failed: {e}")
        return False
    
    # Test cases from the examples
    test_cases = [
        {
            "name": "English (US) - Folk Tale",
            "text": "Did you ever hear a folk tale about a giant turtle?",
            "style": "en_us",
            "audio_url": "https://github.com/gradio-app/gradio/raw/main/test/test_files/audio_sample.wav"
        },
        {
            "name": "English (Default) - Simple Test",
            "text": "Howdy! This is a test of OpenVoice V2.",
            "style": "en_default",
            "audio_url": "https://github.com/gradio-app/gradio/raw/main/test/test_files/audio_sample.wav"
        },
    ]
    
    print(f"\n[2] Running {len(test_cases)} test cases...")
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n  Test {i}: {test['name']}")
        print(f"    Text: {test['text']}")
        print(f"    Style: {test['style']}")
        print(f"    Audio: {test['audio_url']}")
        
        try:
            print("    Submitting request...")
            result = client.predict(
                test['text'],
                test['style'],
                test['audio_url'],
                True,  # agree
                fn_index=1
            )
            
            info, audio_output, ref_audio = result
            
            print(f"    [SUCCESS] Request completed!")
            print(f"    Info: {info[:100]}...")
            print(f"    Output Audio: {audio_output}")
            print(f"    Reference Used: {ref_audio}")
            
        except Exception as e:
            print(f"    [ERROR] Failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    print("\n" + "=" * 70)
    print(" [SUCCESS] All tests passed!")
    print("=" * 70)
    return True

if __name__ == "__main__":
    success = test_openvoice_v2()
    exit(0 if success else 1)

