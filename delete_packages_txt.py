#!/usr/bin/env python3
"""
Delete packages.txt entirely - we don't need it
"""

import os
from huggingface_hub import HfApi, login
import tempfile

def delete_packages_txt(space_id, hf_token):
    """Delete packages.txt by uploading an empty file"""
    print("=" * 70)
    print(" Delete packages.txt")
    print("=" * 70)
    
    # Login
    print(f"\n[1] Logging in...")
    try:
        os.environ["HF_TOKEN"] = hf_token
        login(token=hf_token, write_permission=True)
        print("  [OK] Logged in")
    except Exception as e:
        print(f"  [ERROR] Login failed: {e}")
        return False
    
    # Upload completely empty packages.txt
    print(f"\n[2] Uploading empty packages.txt...")
    print(f"    Space: {space_id}")
    print(f"    [INFO] Empty file will effectively skip package installation")
    
    try:
        api = HfApi()
        
        # Create completely empty file (no comments, no content)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            # Write nothing - completely empty
            temp_path = f.name
        
        try:
            # Upload empty file
            with open(temp_path, 'w') as f:
                pass  # Empty file
            
            api.upload_file(
                path_or_fileobj=temp_path,
                path_in_repo="packages.txt",
                repo_id=space_id,
                repo_type="space",
                commit_message="Delete packages.txt - empty file to skip package installation"
            )
            print("  [OK] Empty packages.txt uploaded")
            print("  [INFO] Build will skip package installation step")
            return True
        finally:
            os.unlink(temp_path)
            
    except Exception as e:
        print(f"  [ERROR] Upload failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    space_id = "theisaiahdupree/OpenVoiceV2"
    hf_token = os.getenv("HF_TOKEN", __import__('os').environ['HF_TOKEN'])
    
    print(f"[INFO] Using token: {hf_token[:10]}...{hf_token[-10:]}")
    
    success = delete_packages_txt(space_id, hf_token)
    
    if success:
        print("\n" + "=" * 70)
        print(" packages.txt Deleted!")
        print("=" * 70)
        print(f"\n✅ Empty packages.txt uploaded")
        print(f"✅ Build will skip package installation")
        print(f"\nThe Space should build successfully now!")
        print(f"Check status: https://huggingface.co/spaces/{space_id}")
    else:
        print("\n[ERROR] Failed.")

if __name__ == "__main__":
    main()

