#!/usr/bin/env python3
"""
Check Hugging Face Token Permissions
====================================
Verify token has Read and API access enabled.
"""

import os
import requests
import json

def check_token_permissions():
    """Check HF token permissions"""
    token = os.getenv("HF_TOKEN", __import__('os').environ['HF_TOKEN'])
    
    if not token:
        print("[ERROR] HF_TOKEN not set")
        return
    
    print("=" * 70)
    print(" Hugging Face Token Permissions Check")
    print("=" * 70)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Check 1: Basic token validity
    print("\n[1] Checking token validity...")
    try:
        response = requests.get("https://huggingface.co/api/whoami", headers=headers)
        if response.status_code == 200:
            user_info = response.json()
            print("  [OK] Token is valid")
            print(f"  Username: {user_info.get('name', 'N/A')}")
            print(f"  Type: {user_info.get('type', 'N/A')}")
            print(f"  Email: {user_info.get('email', 'N/A')}")
            is_pro = user_info.get('pro', False)
            print(f"  Account: {'PRO' if is_pro else 'Free'}")
        else:
            print(f"  [ERROR] Token invalid: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return
    except Exception as e:
        print(f"  [ERROR] Exception: {e}")
        return
    
    # Check 2: Token details (if available via API)
    print("\n[2] Checking token details...")
    try:
        # Try to get token info
        tokens_response = requests.get("https://huggingface.co/api/tokens", headers=headers)
        if tokens_response.status_code == 200:
            tokens = tokens_response.json()
            print(f"  [OK] Found {len(tokens)} token(s)")
            
            # Find our token (by matching first few chars)
            token_prefix = token[:10]
            for t in tokens:
                if t.get('token', '').startswith(token_prefix):
                    print(f"  Token name: {t.get('name', 'N/A')}")
                    print(f"  Created: {t.get('createdAt', 'N/A')}")
                    print(f"  Last used: {t.get('lastUsedAt', 'N/A')}")
                    # Check permissions
                    permissions = t.get('permissions', [])
                    print(f"  Permissions: {permissions}")
                    
                    # Check if Read is enabled
                    if 'read' in permissions or 'READ' in [p.upper() for p in permissions]:
                        print("  [OK] Read permission: Enabled")
                    else:
                        print("  [WARNING] Read permission: Not found")
        else:
            print(f"  [INFO] Cannot fetch token details: {tokens_response.status_code}")
            print("  (This is normal - token details may not be accessible via API)")
    except Exception as e:
        print(f"  [INFO] Could not check token details: {e}")
    
    # Check 3: Test API access to a public resource
    print("\n[3] Testing API access...")
    try:
        # Try accessing a public model info
        test_response = requests.get(
            "https://huggingface.co/api/models/myshell-ai/OpenVoiceV2",
            headers=headers
        )
        if test_response.status_code == 200:
            print("  [OK] Can access model information via API")
        else:
            print(f"  [WARNING] Model access returned: {test_response.status_code}")
    except Exception as e:
        print(f"  [ERROR] API test failed: {e}")
    
    # Check 4: Test Space API access
    print("\n[4] Testing Space API access...")
    try:
        from gradio_client import Client
        client = Client("myshell-ai/OpenVoiceV2", hf_token=token)
        api_info = client.view_api()
        print("  [OK] Can connect to Space API")
        print("  [OK] API endpoints available")
    except Exception as e:
        print(f"  [ERROR] Space API connection failed: {e}")
    
    # Recommendations
    print("\n" + "-" * 70)
    print(" Recommendations")
    print("-" * 70)
    print("\nTo verify token permissions manually:")
    print("  1. Visit: https://huggingface.co/settings/tokens")
    print("  2. Find your token (starts with: " + token[:10] + "...)")
    print("  3. Ensure it has:")
    print("     - Read permission (required)")
    print("     - API access enabled")
    print("\nTo create a new token with proper permissions:")
    print("  1. Go to: https://huggingface.co/settings/tokens")
    print("  2. Click 'New token'")
    print("  3. Select 'Read' permission")
    print("  4. Copy the token and set: $env:HF_TOKEN='your_new_token'")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    check_token_permissions()

