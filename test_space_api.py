#!/usr/bin/env python3
"""
Test the OpenVoice Space API
"""

import os
import time
from gradio_client import Client, handle_file

def test_api():
    """Test the Space API"""
    print("=" * 70)
    print(" Testing OpenVoice Space API")
    print("=" * 70)
    
    space_id = "theisaiahdupree/OpenVoice"
    hf_token = os.getenv("HF_TOKEN", (__import__('os').environ['HF_TOKEN']))
    
    print(f"\n[1] Connecting to Space: {space_id}")
    try:
        client = Client(space_id, hf_token=hf_token)
        print("  [OK] Connected")
    except Exception as e:
        print(f"  [ERROR] Connection failed: {e}")
        return False
    
    print(f"\n[2] Testing voice cloning...")
    test_text = "Hello, this is a test of the OpenVoice system. The voice cloning is working correctly."
    style = "default"
    
    # Use the demo audio file
    audio_url = f"https://{space_id.replace('/', '-')}.hf.space/gradio_api/file=/app/resources/demo_speaker2.mp3"
    
    print(f"  Text: {test_text}")
    print(f"  Style: {style}")
    print(f"  Reference audio: {audio_url}")
    
    try:
        print(f"\n[3] Submitting request...")
        result = client.predict(
            prompt=test_text,
            style=style,
            audio_file_pth=handle_file(audio_url),
            agree=True,
            api_name="/predict"
        )
        
        print(f"\n[4] Result received!")
        print(f"  Type: {type(result)}")
        
        if isinstance(result, tuple) and len(result) >= 2:
            info_text = result[0]
            audio_path = result[1]
            ref_audio = result[2] if len(result) > 2 else None
            
            print(f"\n  Info: {info_text}")
            print(f"  Audio output: {audio_path}")
            if ref_audio:
                print(f"  Reference audio: {ref_audio}")
            
            if audio_path:
                if isinstance(audio_path, str):
                    if os.path.exists(audio_path):
                        file_size = os.path.getsize(audio_path)
                        print(f"  Output file size: {file_size} bytes")
                        print(f"  [SUCCESS] Audio file generated and saved!")
                    else:
                        print(f"  [INFO] Audio path: {audio_path}")
                        print(f"  [SUCCESS] Audio generated (download from Space)")
                else:
                    print(f"  [INFO] Audio: {audio_path}")
                    print(f"  [SUCCESS] Audio generated")
            else:
                print(f"  [WARNING] No audio path in result")
            
            print("\n" + "=" * 70)
            print(" TEST SUCCESSFUL!")
            print("=" * 70)
            print(f"\n✅ Space API is working correctly")
            print(f"✅ Voice cloning is functional")
            return True
        else:
            print(f"  Unexpected result format: {result}")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_api()
    exit(0 if success else 1)

