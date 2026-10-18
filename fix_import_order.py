#!/usr/bin/env python3
"""
Fix app.py - ensure sys.path modification happens BEFORE imports
"""

import os
from huggingface_hub import HfApi, login
import tempfile

def fix_import_order(space_id, hf_token):
    """Fix app.py to add sys.path before any imports"""
    print("=" * 70)
    print(" Fix Import Order in app.py")
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
    
    # Read app.py
    app_file = "openvoice_deploy/app.py"
    if not os.path.exists(app_file):
        print(f"  [ERROR] {app_file} not found")
        return False
    
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The sys.path modification MUST be at the very top, before ANY imports
    # Current structure has imports first, then sys.path - that's wrong!
    
    # Find where imports start
    lines = content.split('\n')
    new_lines = []
    
    # Add sys.path modification at the VERY beginning
    new_lines.append("import os")
    new_lines.append("import sys")
    new_lines.append("# Add openvoice to Python path BEFORE any other imports")
    new_lines.append("sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'openvoice'))")
    new_lines.append("sys.path.insert(0, os.path.dirname(__file__))")
    new_lines.append("")
    
    # Now add all the original imports
    for line in lines:
        # Skip duplicate sys/os imports if we already added them
        if line.strip().startswith("import os") and "os" in [l.strip() for l in new_lines if l.strip().startswith("import")]:
            # Check if it's the first import os
            if "import os" in [l.strip() for l in new_lines]:
                continue
        if line.strip().startswith("import sys") and "sys" in [l.strip() for l in new_lines if l.strip().startswith("import")]:
            if "import sys" in [l.strip() for l in new_lines]:
                continue
        new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    # Verify the fix
    if "sys.path.insert" in content.split('\n')[0:10]:
        print("  [OK] sys.path modification moved to top of file")
    else:
        print("  [WARNING] sys.path modification may not be at top")
    
    # Upload fixed app.py
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
                commit_message="Fix import order - sys.path must be before all imports"
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
    
    success = fix_import_order(space_id, hf_token)
    
    if success:
        print("\n" + "=" * 70)
        print(" Import Order Fixed!")
        print("=" * 70)
        print(f"\n✅ sys.path modification moved to top of file")
        print(f"✅ Will execute BEFORE any imports")
        print(f"✅ Python will find openvoice module")
        print(f"\nThe Space will rebuild and should work now.")
        print(f"Check status: https://huggingface.co/spaces/{space_id}")
    else:
        print("\n[ERROR] Failed.")

if __name__ == "__main__":
    main()

