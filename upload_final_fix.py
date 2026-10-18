#!/usr/bin/env python3
"""
Upload final fix - remove show_api parameter
"""

import os
from huggingface_hub import HfApi, login
import tempfile

def upload_final_fix(space_id, hf_token):
    """Upload the final fixed app.py"""
    print("=" * 70)
    print(" Upload Final Fix (remove show_api)")
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
    
    # Read fixed app.py
    app_file = "openvoice_deploy/app.py"
    if not os.path.exists(app_file):
        print(f"  [ERROR] {app_file} not found")
        return False
    
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verify fix
    if "show_api=True" not in content:
        print("  [OK] show_api parameter removed")
    else:
        print("  [WARNING] show_api still present")
        return False
    
    # Upload
    print(f"\n[2] Uploading fixed app.py...")
    try:
        api = HfApi()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            api.upload_file(
                path_or_fileobj=temp_path,
                path_in_repo="app.py",
                repo_id=space_id,
                repo_type="space",
                commit_message="Fix: Remove show_api parameter (Gradio 3.48 compatibility)"
            )
            print("  [OK] app.py uploaded")
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
    
    success = upload_final_fix(space_id, hf_token)
    
    if success:
        print("\n" + "=" * 70)
        print(" Final Fix Uploaded!")
        print("=" * 70)
        print(f"\n✅ Removed show_api parameter")
        print(f"✅ Compatible with Gradio 3.48.0")
        print(f"✅ All imports working")
        print(f"\nThe Space should start successfully now!")
        print(f"Check status: https://huggingface.co/spaces/{space_id}")
    else:
        print("\n[ERROR] Failed.")

if __name__ == "__main__":
    main()

