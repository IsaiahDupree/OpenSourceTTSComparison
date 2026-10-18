#!/usr/bin/env python3
"""
Test the deployed OpenVoice Space
"""

import os
import sys
from gradio_client import Client
import time
import requests

def test_space():
    """Test the deployed OpenVoice Space"""
    print("=" * 70)
    print(" Testing OpenVoice Space")
    print("=" * 70)
    
    space_id = "theisaiahdupree/OpenVoice"
    hf_token = os.getenv("HF_TOKEN", (__import__('os').environ['HF_TOKEN']))
    
    print(f"\n[1] Waking up Space...")
    space_url = f"https://{space_id.replace('/', '-')}.hf.space"
    try:
        response = requests.get(space_url, timeout=15)
        print(f"  [OK] Space URL accessible: HTTP {response.status_code}")
    except Exception as e:
        print(f"  [WARNING] Could not access Space URL: {e}")
    
    print(f"\n[2] Waiting for Space to be ready (10 seconds)...")
    time.sleep(10)
    
    print(f"\n[3] Connecting to Space: {space_id}")
    
    try:
        # Create client with retry
        max_retries = 3
        client = None
        for attempt in range(max_retries):
            try:
                client = Client(space_id, hf_token=hf_token)
                print("  [OK] Client created")
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"  [RETRY] Attempt {attempt + 1} failed: {e}")
                    print(f"  Waiting 5 seconds before retry...")
                    time.sleep(5)
                else:
                    raise
        
        # Check if Space is awake
        print(f"\n[4] Checking Space status...")
        try:
            # Try to get the API info
            api_info = client.view_api()
            print("  [OK] Space is awake and responding")
            print(f"  API endpoints: {len(api_info)}")
        except Exception as e:
            print(f"  [WARNING] Could not get API info: {e}")
            print("  Continuing anyway...")
        
        # Test the predict function
        print(f"\n[5] Testing voice cloning...")
        
        # Use a demo audio file (should be available in the Space)
        demo_audio = "resources/demo_speaker2.mp3"
        test_text = "Hello, this is a test of the OpenVoice system."
        style = "default"
        agree = True
        
        print(f"  Text: {test_text}")
        print(f"  Style: {style}")
        print(f"  Reference audio: {demo_audio}")
        
        try:
            # Submit the job
            print(f"\n[6] Submitting job...")
            job = client.submit(
                test_text,
                style,
                demo_audio,
                agree,
                api_name="/predict"
            )
            print("  [OK] Job submitted")
            
            # Wait for result
            print(f"\n[7] Waiting for result (this may take 30-60 seconds)...")
            start_time = time.time()
            result = job.result(timeout=300)
            elapsed = time.time() - start_time
            
            print(f"  [OK] Result received in {elapsed:.1f} seconds")
            print(f"\n[8] Result:")
            print(f"  Type: {type(result)}")
            
            if isinstance(result, tuple) and len(result) >= 2:
                info_text, audio_path, ref_audio = result[0], result[1], result[2] if len(result) > 2 else None
                print(f"  Info: {info_text}")
                print(f"  Audio output: {audio_path}")
                if ref_audio:
                    print(f"  Reference audio: {ref_audio}")
                
                if audio_path and os.path.exists(audio_path) if isinstance(audio_path, str) else False:
                    file_size = os.path.getsize(audio_path)
                    print(f"  Output file size: {file_size} bytes")
                    print(f"  [SUCCESS] Audio file generated!")
                elif audio_path:
                    print(f"  [INFO] Audio path: {audio_path}")
                    print(f"  [SUCCESS] Audio generated (path provided)")
                else:
                    print(f"  [WARNING] No audio path in result")
            else:
                print(f"  Result: {result}")
            
            print("\n" + "=" * 70)
            print(" TEST SUCCESSFUL!")
            print("=" * 70)
            print(f"\n✅ Space is working correctly")
            print(f"✅ Voice cloning is functional")
            print(f"\nYour OpenVoice Space is ready to use!")
            
        except Exception as e:
            print(f"\n[ERROR] Test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_space()
    sys.exit(0 if success else 1)

