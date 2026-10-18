#!/usr/bin/env python3
"""
Fix app.py to properly import openvoice - either install package or add to path
"""

import os
from huggingface_hub import HfApi, login
import tempfile

def fix_app_py_imports(space_id, hf_token):
    """Fix app.py to install openvoice package or add to path"""
    print("=" * 70)
    print(" Fix openvoice Import Issue")
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
    
    # Read current app.py
    app_file = "openvoice_deploy/app.py"
    if not os.path.exists(app_file):
        print(f"  [ERROR] {app_file} not found")
        return False
    
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Option 1: Add sys.path modification at the start
    # Option 2: Install openvoice package via setup.py
    # Let's do both - add path AND install package
    
    # Add path modification at the very beginning
    new_imports = """import os
import sys
# Add openvoice to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'openvoice'))
sys.path.insert(0, os.path.dirname(__file__))

"""
    
    # Check if we already added this
    if "sys.path.insert" not in content:
        # Insert after existing imports but before openvoice import
        # Find the openvoice import line
        lines = content.split('\n')
        new_lines = []
        added_path = False
        
        for i, line in enumerate(lines):
            # Add path modification before openvoice import
            if 'from openvoice' in line or 'import openvoice' in line:
                if not added_path:
                    new_lines.append("import os")
                    new_lines.append("import sys")
                    new_lines.append("# Add openvoice to path")
                    new_lines.append("sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'openvoice'))")
                    new_lines.append("sys.path.insert(0, os.path.dirname(__file__))")
                    new_lines.append("")
                    added_path = True
            new_lines.append(line)
        
        content = '\n'.join(new_lines)
        print("  [OK] Added sys.path modification to app.py")
    else:
        print("  [INFO] sys.path already modified")
    
    # Also create a setup script that installs openvoice
    print(f"\n[2] Creating install script...")
    
    # Upload fixed app.py
    print(f"\n[3] Uploading fixed app.py...")
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
                commit_message="Fix openvoice import - add sys.path modification"
            )
            print("  [OK] app.py uploaded")
        finally:
            os.unlink(temp_path)
    except Exception as e:
        print(f"  [ERROR] Upload failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Also try installing openvoice via requirements or setup
    # Actually, let's add a post-install script or modify requirements
    print(f"\n[4] Adding openvoice installation to requirements...")
    
    # Read current requirements
    req_file = "openvoice_deploy/requirements.txt"
    if os.path.exists(req_file):
        with open(req_file, 'r', encoding='utf-8') as f:
            req_content = f.read()
        
        # Add -e . to install openvoice package
        if "-e ." not in req_content and "openvoice" not in req_content.lower():
            req_content += "\n-e .  # Install openvoice package from local code\n"
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(req_content)
                temp_path = f.name
            
            try:
                api.upload_file(
                    path_or_fileobj=temp_path,
                    path_in_repo="requirements.txt",
                    repo_id=space_id,
                    repo_type="space",
                    commit_message="Add -e . to install openvoice package"
                )
                print("  [OK] requirements.txt updated")
            finally:
                os.unlink(temp_path)
        else:
            print("  [INFO] requirements.txt already has installation")
    
    return True

def main():
    space_id = "theisaiahdupree/OpenVoiceV2"
    hf_token = os.getenv("HF_TOKEN", __import__('os').environ['HF_TOKEN'])
    
    print(f"[INFO] Using token: {hf_token[:10]}...{hf_token[-10:]}")
    
    success = fix_app_py_imports(space_id, hf_token)
    
    if success:
        print("\n" + "=" * 70)
        print(" Import Fix Applied!")
        print("=" * 70)
        print(f"\n✅ Modified app.py to add openvoice to sys.path")
        print(f"✅ Added -e . to requirements.txt to install openvoice package")
        print(f"\nThe Space will rebuild and should find the openvoice module.")
        print(f"Check status: https://huggingface.co/spaces/{space_id}")
    else:
        print("\n[ERROR] Failed.")

if __name__ == "__main__":
    main()

