#!/usr/bin/env python3
"""
Check Hugging Face Account Status
==================================
Check if billing is needed and account status.
"""

import os
import requests

def check_hf_status():
    """Check Hugging Face account status"""
    token = os.getenv("HF_TOKEN", __import__('os').environ['HF_TOKEN'])
    
    if not token:
        print("[ERROR] HF_TOKEN not set")
        return
    
    print("=" * 70)
    print(" Hugging Face Account Status Check")
    print("=" * 70)
    
    # Check token validity and account info
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get user info
        response = requests.get("https://huggingface.co/api/whoami", headers=headers)
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"\n[OK] Token is valid")
            print(f"  Username: {user_info.get('name', 'N/A')}")
            print(f"  Type: {user_info.get('type', 'N/A')}")
            print(f"  Email: {user_info.get('email', 'N/A')}")
            
            # Check if PRO user
            is_pro = user_info.get('pro', False)
            if is_pro:
                print(f"  [PRO] Account type: PRO")
            else:
                print(f"  [FREE] Account type: Free")
        else:
            print(f"\n[ERROR] Failed to get user info: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
    
    except Exception as e:
        print(f"\n[ERROR] Exception checking account: {e}")
    
    # Check API inference status
    print("\n" + "-" * 70)
    print(" API Inference Status")
    print("-" * 70)
    
    print("\nAccording to Hugging Face documentation:")
    print("  - Free tier: $0.10/month in credits")
    print("  - PRO tier: $2.00/month in credits + pay-as-you-go")
    print("  - Free users cannot continue after credits are exhausted")
    print("  - PRO users can continue on pay-as-you-go basis")
    
    print("\n[INFO] For OpenVoiceV2 Space API:")
    print("  - Spaces API calls may consume credits")
    print("  - If you're getting errors, it could be:")
    print("    1. Credits exhausted (free tier)")
    print("    2. Rate limiting")
    print("    3. Space-specific issues")
    print("    4. Authentication problems")
    
    print("\n[RECOMMENDATION]")
    print("  If you plan to use OpenVoice frequently:")
    print("  - Consider upgrading to PRO ($9/month)")
    print("  - Or set up billing for pay-as-you-go")
    print("  - Check your usage at: https://huggingface.co/settings/billing")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    check_hf_status()

