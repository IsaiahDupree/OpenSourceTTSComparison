#!/usr/bin/env python3
"""
Remove -e . from requirements.txt - setup.py isn't available during install
We'll rely on sys.path modification in app.py instead
"""

import os
from huggingface_hub import HfApi, login
import tempfile

def remove_editable_install(space_id, hf_token):
    """Remove -e . from requirements.txt"""
    print("=" * 70)
    print(" Remove -e . from requirements.txt")
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
    
    # Read current requirements
    req_file = "openvoice_deploy/requirements.txt"
    if not os.path.exists(req_file):
        print(f"  [ERROR] {req_file} not found")
        return False
    
    with open(req_file, 'r', encoding='utf-8') as f:
        req_content = f.read()
    
    # Remove -e . line
    lines = req_content.split('\n')
    new_lines = []
    removed = False
    
    for line in lines:
        if line.strip().startswith('-e .') or line.strip() == '-e .':
            print(f"  [INFO] Removing line: {line.strip()}")
            removed = True
            continue
        if '# Install openvoice package' in line:
            continue  # Remove comment too
        new_lines.append(line)
    
    if not removed:
        print("  [INFO] -e . not found in requirements.txt")
    
    new_content = '\n'.join(new_lines)
    
    # Upload fixed requirements
    print(f"\n[2] Uploading fixed requirements.txt...")
    try:
        api = HfApi()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(new_content)
            temp_path = f.name
        
        try:
            api.upload_file(
                path_or_fileobj=temp_path,
                path_in_repo="requirements.txt",
                repo_id=space_id,
                repo_type="space",
                commit_message="Remove -e . from requirements - setup.py not available during install, using sys.path instead"
            )
            print("  [OK] requirements.txt uploaded")
            print("  [INFO] Will rely on sys.path modification in app.py")
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
    
    success = remove_editable_install(space_id, hf_token)
    
    if success:
        print("\n" + "=" * 70)
        print(" Fixed requirements.txt!")
        print("=" * 70)
        print(f"\n✅ Removed -e . from requirements.txt")
        print(f"✅ Will use sys.path modification in app.py instead")
        print(f"\nThe Space will rebuild and should work now.")
        print(f"Check status: https://huggingface.co/spaces/{space_id}")
    else:
        print("\n[ERROR] Failed.")

if __name__ == "__main__":
    main()

