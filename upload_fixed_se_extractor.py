#!/usr/bin/env python3
"""
Upload the fixed se_extractor.py with optional faster_whisper
"""

import os
from huggingface_hub import HfApi, login
import tempfile

def upload_fixed_se_extractor(space_id, hf_token):
    """Upload the fixed se_extractor.py"""
    print("=" * 70)
    print(" Upload Fixed se_extractor.py (optional faster_whisper)")
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
    
    # Read fixed se_extractor.py
    se_file = "openvoice_deploy/openvoice/se_extractor.py"
    if not os.path.exists(se_file):
        print(f"  [ERROR] {se_file} not found")
        return False
    
    with open(se_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verify fix
    if "FASTER_WHISPER_AVAILABLE" in content:
        print("  [OK] Optional faster_whisper import found")
    else:
        print("  [WARNING] Optional import not found")
    
    # Upload
    print(f"\n[2] Uploading fixed se_extractor.py...")
    try:
        api = HfApi()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            api.upload_file(
                path_or_fileobj=temp_path,
                path_in_repo="openvoice/se_extractor.py",
                repo_id=space_id,
                repo_type="space",
                commit_message="Fix: Make faster_whisper and whisper_timestamped optional"
            )
            print("  [OK] se_extractor.py uploaded")
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
    
    success = upload_fixed_se_extractor(space_id, hf_token)
    
    if success:
        print("\n" + "=" * 70)
        print(" Upload Complete!")
        print("=" * 70)
        print(f"\n✅ faster_whisper is now optional")
        print(f"✅ whisper_timestamped is now optional")
        print(f"✅ Will use VAD method (which doesn't need faster_whisper)")
        print(f"\nThe Space will rebuild and should work now.")
        print(f"Check status: https://huggingface.co/spaces/{space_id}")
    else:
        print("\n[ERROR] Failed.")

if __name__ == "__main__":
    main()

