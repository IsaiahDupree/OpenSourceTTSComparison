#!/usr/bin/env python3
"""
Directly fix the Hugging Face Space by uploading the fixed app.py
This bypasses GitHub and directly updates the Space files.
"""

import os
from pathlib import Path
from huggingface_hub import HfApi, login
import tempfile

def fix_space_direct(space_id, hf_token):
    """Directly upload fixed app.py to the Space"""
    print("=" * 70)
    print(" Direct Space Fix via Hugging Face API")
    print("=" * 70)
    
    # Login with explicit token
    print(f"\n[1] Logging in to Hugging Face...")
    try:
        # Clear any existing login
        os.environ["HF_TOKEN"] = hf_token
        login(token=hf_token, write_permission=True)
        print("  [OK] Logged in with write token")
    except Exception as e:
        print(f"  [ERROR] Login failed: {e}")
        return False
    
    # Read the fixed app.py
    print(f"\n[2] Reading fixed app.py...")
    app_file = Path("openvoice_deploy/app.py")
    
    if not app_file.exists():
        print(f"  [ERROR] {app_file} not found")
        print("  Please run deploy_fixed_fork.py first")
        return False
    
    content = app_file.read_text(encoding='utf-8')
    print(f"  [OK] Read {app_file} ({len(content)} characters)")
    
    # Verify no info= in gr.Audio
    if 'info=' in content and 'gr.Audio' in content:
        # Check if it's in gr.Audio context
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'gr.Audio(' in line:
                # Check next few lines
                context = '\n'.join(lines[i:i+5])
                if 'info=' in context:
                    print(f"  [WARNING] Found 'info=' near gr.Audio at line {i+1}")
                    print(f"    Context: {context[:200]}")
                    return False
    
    print("  [OK] Verified: No info= parameter in gr.Audio() calls")
    
    # Upload to Space
    print(f"\n[3] Uploading fixed app.py to Space...")
    print(f"    Space: {space_id}")
    
    try:
        api = HfApi()
        
        # Upload the file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            api.upload_file(
                path_or_fileobj=temp_path,
                path_in_repo="app.py",
                repo_id=space_id,
                repo_type="space",
                commit_message="Fix Gradio compatibility - remove info parameter from gr.Audio"
            )
            print("  [OK] File uploaded successfully")
            print("  [INFO] Space will rebuild automatically")
            return True
        finally:
            # Clean up temp file
            os.unlink(temp_path)
            
    except Exception as e:
        print(f"  [ERROR] Upload failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    space_id = "theisaiahdupree/OpenVoiceV2"
    # Use provided write token or fallback to environment variable
    hf_token = os.getenv("HF_TOKEN", __import__('os').environ['HF_TOKEN'])
    
    if not hf_token:
        print("[ERROR] HF_TOKEN not set")
        print("  Set with: $env:HF_TOKEN='your_token'")
        return
    
    print(f"[INFO] Using token: {hf_token[:10]}...{hf_token[-10:]}")
    
    success = fix_space_direct(space_id, hf_token)
    
    if success:
        print("\n" + "=" * 70)
        print(" Fix Applied!")
        print("=" * 70)
        print(f"\nThe Space will rebuild automatically.")
        print(f"Check status at: https://huggingface.co/spaces/{space_id}")
        print("\nWait 1-2 minutes for the rebuild to complete.")
    else:
        print("\n[ERROR] Fix failed. Please check the errors above.")

if __name__ == "__main__":
    main()

