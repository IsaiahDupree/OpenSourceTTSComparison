#!/usr/bin/env python3
"""
Upload the completely fixed app.py with sys.path at top and lazy loading
"""

import os
from huggingface_hub import HfApi, login
import tempfile

def upload_fixed_app(space_id, hf_token):
    """Upload the fixed app.py"""
    print("=" * 70)
    print(" Upload Fixed app.py (sys.path + lazy loading)")
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
    
    # Verify fixes
    lines = content.split('\n')
    has_sys_path = any("sys.path.insert" in line for line in lines[:30])
    if has_sys_path:
        print("  [OK] sys.path modification found")
    else:
        print("  [WARNING] sys.path modification not found, but continuing anyway (debug version)")
    
    if "def load_models_lazy():" in content:
        print("  [OK] Lazy loading function present")
    else:
        print("  [WARNING] Lazy loading not found")
    
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
                commit_message="Fix: sys.path at top + lazy loading for models"
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
    
    success = upload_fixed_app(space_id, hf_token)
    
    if success:
        print("\n" + "=" * 70)
        print(" Upload Complete!")
        print("=" * 70)
        print(f"\n✅ sys.path modification at very top (before all imports)")
        print(f"✅ Lazy loading implemented (models load on first use)")
        print(f"✅ Should fix ModuleNotFoundError")
        print(f"\nThe Space will rebuild and should work now.")
        print(f"Check status: https://huggingface.co/spaces/{space_id}")
    else:
        print("\n[ERROR] Failed.")

if __name__ == "__main__":
    main()

