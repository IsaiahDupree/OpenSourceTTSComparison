#!/usr/bin/env python3
"""
Check Space status and test via web interface
"""

import requests
import time

def check_space():
    """Check if Space is accessible"""
    print("=" * 70)
    print(" Checking OpenVoice Space Status")
    print("=" * 70)
    
    space_id = "theisaiahdupree/OpenVoiceV2"
    
    # Try different URL formats
    urls = [
        f"https://{space_id.replace('/', '-')}.hf.space",
        f"https://{space_id.replace('/', '-')}.hf.space/",
        f"https://huggingface.co/spaces/{space_id}",
    ]
    
    print(f"\n[1] Testing Space URLs...")
    for url in urls:
        try:
            response = requests.get(url, timeout=10, allow_redirects=True)
            print(f"  {url}")
            print(f"    Status: {response.status_code}")
            print(f"    Final URL: {response.url}")
            if response.status_code == 200:
                print(f"    [OK] Accessible")
                if "OpenVoice" in response.text or "gradio" in response.text.lower():
                    print(f"    [OK] Contains OpenVoice/Gradio content")
            print()
        except Exception as e:
            print(f"  {url}")
            print(f"    [ERROR] {e}\n")
    
    # Check API endpoint
    print(f"\n[2] Testing API endpoint...")
    api_url = f"https://{space_id.replace('/', '-')}.hf.space/api"
    try:
        response = requests.get(api_url, timeout=10)
        print(f"  {api_url}")
        print(f"    Status: {response.status_code}")
        if response.status_code == 200:
            print(f"    [OK] API endpoint accessible")
            try:
                data = response.json()
                print(f"    API info: {len(data)} endpoints")
            except:
                print(f"    Response: {response.text[:200]}")
        else:
            print(f"    Response: {response.text[:200]}")
    except Exception as e:
        print(f"  [ERROR] {e}")
    
    print(f"\n[3] Direct Space Link:")
    print(f"  https://huggingface.co/spaces/{space_id}")
    print(f"\n  You can test it manually in your browser!")

if __name__ == "__main__":
    check_space()
