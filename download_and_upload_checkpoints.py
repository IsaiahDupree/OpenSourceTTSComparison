#!/usr/bin/env python3
"""
Download OpenVoice checkpoints and upload them to Hugging Face Space
"""

import os
import requests
from pathlib import Path
from huggingface_hub import HfApi, login
import tempfile
import zipfile
import shutil

def download_checkpoints():
    """Download checkpoints from OpenVoice repository"""
    print("=" * 70)
    print(" Download OpenVoice Checkpoints")
    print("=" * 70)
    
    # Checkpoints are typically downloaded from Hugging Face or GitHub releases
    # Let's check the OpenVoice repository for download instructions
    
    print("\n[1] Checking checkpoint download options...")
    
    # Option 1: Hugging Face model repository
    hf_model_repo = "myshell-ai/OpenVoice"
    
    # Option 2: GitHub releases
    github_releases = "https://github.com/myshell-ai/OpenVoice/releases"
    
    print(f"    Hugging Face Model: https://huggingface.co/{hf_model_repo}")
    print(f"    GitHub Releases: {github_releases}")
    
    # Check if checkpoints directory exists locally
    checkpoints_dir = Path("openvoice_deploy/checkpoints")
    if checkpoints_dir.exists():
        print(f"\n[2] Found local checkpoints at: {checkpoints_dir}")
        print(f"    [INFO] Checking what's there...")
        
        # List what's in checkpoints
        if (checkpoints_dir / "base_speakers").exists():
            print(f"    ✅ base_speakers directory exists")
        if (checkpoints_dir / "converter").exists():
            print(f"    ✅ converter directory exists")
        
        return checkpoints_dir
    
    print(f"\n[2] No local checkpoints found")
    print(f"    [INFO] Checkpoints need to be downloaded")
    print(f"\n    Instructions:")
    print(f"    1. Visit: https://github.com/myshell-ai/OpenVoice#checkpoint-download")
    print(f"    2. Download checkpoints.zip or individual checkpoint files")
    print(f"    3. Extract to: openvoice_deploy/checkpoints/")
    print(f"    4. Structure should be:")
    print(f"       checkpoints/")
    print(f"         base_speakers/")
    print(f"           EN/")
    print(f"             config.json")
    print(f"             checkpoint.pth")
    print(f"             en_default_se.pth")
    print(f"             en_style_se.pth")
    print(f"           ZH/")
    print(f"             config.json")
    print(f"             checkpoint.pth")
    print(f"             zh_default_se.pth")
    print(f"         converter/")
    print(f"           config.json")
    print(f"           checkpoint.pth")
    
    return None

def upload_checkpoints_to_space(space_id, hf_token, checkpoints_dir):
    """Upload checkpoints to Hugging Face Space"""
    print("\n" + "=" * 70)
    print(" Upload Checkpoints to Space")
    print("=" * 70)
    
    if not checkpoints_dir or not checkpoints_dir.exists():
        print("\n[ERROR] Checkpoints directory not found")
        print("    Please download checkpoints first")
        return False
    
    # Login
    print(f"\n[1] Logging in...")
    try:
        os.environ["HF_TOKEN"] = hf_token
        login(token=hf_token, write_permission=True)
        print("  [OK] Logged in")
    except Exception as e:
        print(f"  [ERROR] Login failed: {e}")
        return False
    
    # Upload checkpoints
    print(f"\n[2] Uploading checkpoints...")
    print(f"    Space: {space_id}")
    print(f"    Source: {checkpoints_dir}")
    
    try:
        api = HfApi()
        
        # Upload each checkpoint file
        checkpoint_files = []
        
        # Find all checkpoint files
        for root, dirs, files in os.walk(checkpoints_dir):
            for file in files:
                if file.endswith(('.pth', '.json')):
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(checkpoints_dir)
                    checkpoint_files.append((file_path, str(rel_path)))
        
        if not checkpoint_files:
            print("  [ERROR] No checkpoint files found")
            return False
        
        print(f"    [INFO] Found {len(checkpoint_files)} checkpoint files")
        
        # Upload files (in batches to avoid overwhelming)
        uploaded = 0
        for i, (file_path, rel_path) in enumerate(checkpoint_files, 1):
            try:
                print(f"    [{i}/{len(checkpoint_files)}] Uploading {rel_path}...", end=" ")
                
                api.upload_file(
                    path_or_fileobj=str(file_path),
                    path_in_repo=f"checkpoints/{rel_path}",
                    repo_id=space_id,
                    repo_type="space",
                    commit_message=f"Add checkpoint: {rel_path}" if i == 1 else None
                )
                uploaded += 1
                print("✅")
            except Exception as e:
                print(f"❌ Error: {e}")
                # Continue with other files
        
        print(f"\n  [OK] Uploaded {uploaded}/{len(checkpoint_files)} files")
        return uploaded > 0
        
    except Exception as e:
        print(f"  [ERROR] Upload failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    space_id = "theisaiahdupree/OpenVoiceV2"
    hf_token = os.getenv("HF_TOKEN", __import__('os').environ['HF_TOKEN'])
    
    print(f"[INFO] Using token: {hf_token[:10]}...{hf_token[-10:]}")
    
    # Step 1: Check for local checkpoints
    checkpoints_dir = download_checkpoints()
    
    if checkpoints_dir and checkpoints_dir.exists():
        # Step 2: Upload to Space
        print("\n" + "=" * 70)
        response = input("\nUpload checkpoints to Space? (y/n): ").strip().lower()
        if response == 'y':
            success = upload_checkpoints_to_space(space_id, hf_token, checkpoints_dir)
            if success:
                print("\n" + "=" * 70)
                print(" Checkpoints Uploaded!")
                print("=" * 70)
                print(f"\n✅ Checkpoints uploaded to Space")
                print(f"✅ Space will need to rebuild to recognize them")
                print(f"\nCheck status: https://huggingface.co/spaces/{space_id}")
            else:
                print("\n[ERROR] Upload failed")
        else:
            print("\n[INFO] Skipped upload")
    else:
        print("\n" + "=" * 70)
        print(" Next Steps:")
        print("=" * 70)
        print("\n1. Download checkpoints from:")
        print("   https://github.com/myshell-ai/OpenVoice#checkpoint-download")
        print("\n2. Extract to: openvoice_deploy/checkpoints/")
        print("\n3. Run this script again to upload them")

if __name__ == "__main__":
    main()

