#!/usr/bin/env python3
"""
Upload all missing openvoice files to the Space
"""

import os
from huggingface_hub import HfApi, login
from pathlib import Path

def upload_openvoice_files(space_id, hf_token, source_dir):
    """Upload all files from openvoice directory to the Space"""
    print("=" * 70)
    print(" Upload Missing OpenVoice Files")
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
    
    # Get all files in openvoice directory
    openvoice_dir = Path(source_dir) / "openvoice"
    if not openvoice_dir.exists():
        print(f"  [ERROR] {openvoice_dir} not found")
        return False
    
    files_to_upload = []
    for file_path in openvoice_dir.rglob("*"):
        if file_path.is_file():
            # Get relative path from openvoice directory
            rel_path = file_path.relative_to(openvoice_dir)
            files_to_upload.append((file_path, rel_path))
    
    print(f"\n[2] Found {len(files_to_upload)} files to upload:")
    for _, rel_path in files_to_upload[:10]:
        print(f"    - openvoice/{rel_path}")
    if len(files_to_upload) > 10:
        print(f"    ... and {len(files_to_upload) - 10} more")
    
    # Upload files
    print(f"\n[3] Uploading files...")
    api = HfApi()
    uploaded = 0
    failed = 0
    
    for file_path, rel_path in files_to_upload:
        try:
            repo_path = f"openvoice/{rel_path}"
            api.upload_file(
                path_or_fileobj=str(file_path),
                path_in_repo=repo_path,
                repo_id=space_id,
                repo_type="space",
                commit_message=f"Add missing openvoice files: {rel_path}"
            )
            uploaded += 1
            if uploaded % 5 == 0:
                print(f"  [OK] Uploaded {uploaded}/{len(files_to_upload)} files...")
        except Exception as e:
            print(f"  [ERROR] Failed to upload {rel_path}: {e}")
            failed += 1
    
    print(f"\n[4] Upload complete:")
    print(f"  ✅ Uploaded: {uploaded}")
    print(f"  ❌ Failed: {failed}")
    
    return failed == 0

def main():
    space_id = "theisaiahdupree/OpenVoiceV2"
    hf_token = os.getenv("HF_TOKEN", __import__('os').environ['HF_TOKEN'])
    source_dir = "openvoice_deploy"
    
    print(f"[INFO] Using token: {hf_token[:10]}...{hf_token[-10:]}")
    print(f"[INFO] Source directory: {source_dir}")
    
    success = upload_openvoice_files(space_id, hf_token, source_dir)
    
    if success:
        print("\n" + "=" * 70)
        print(" All OpenVoice Files Uploaded!")
        print("=" * 70)
        print(f"\n✅ All files from openvoice/ directory uploaded")
        print(f"✅ api.py and all dependencies should now be available")
        print(f"\nThe Space will rebuild and should work now.")
        print(f"Check status: https://huggingface.co/spaces/{space_id}")
    else:
        print("\n[ERROR] Some files failed to upload. Check errors above.")

if __name__ == "__main__":
    main()

