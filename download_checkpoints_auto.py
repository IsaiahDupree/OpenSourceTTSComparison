#!/usr/bin/env python3
"""
Automatically download OpenVoice checkpoints and upload to Space
"""

import os
import requests
from pathlib import Path
from huggingface_hub import HfApi, login
import zipfile
import tempfile
import shutil

def download_checkpoints_from_url(checkpoints_dir):
    """Download checkpoints from known URLs"""
    print("=" * 70)
    print(" Download OpenVoice Checkpoints")
    print("=" * 70)
    
    # Known checkpoint URLs
    checkpoint_urls = {
        "v2": "https://myshell-public-repo-host.s3.amazonaws.com/openvoice/checkpoints_v2_0417.zip",
        "v1": "https://myshell-public-repo-host.s3.amazonaws.com/openvoice/checkpoints.zip"
    }
    
    print("\n[1] Available Checkpoint Downloads:")
    print("    V2 (Recommended): checkpoints_v2_0417.zip")
    print("    V1 (Legacy): checkpoints.zip")
    
    # Use V2 for OpenVoiceV2 Space
    url = checkpoint_urls["v2"]
    zip_name = "checkpoints_v2_0417.zip"
    
    print(f"\n[2] Downloading {zip_name}...")
    print(f"    URL: {url}")
    
    try:
        # Download with progress
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        print(f"    Size: {total_size / (1024*1024):.1f} MB")
        
        zip_path = Path(checkpoints_dir.parent) / zip_name
        
        with open(zip_path, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\r    Progress: {percent:.1f}%", end='', flush=True)
        
        print(f"\n    [OK] Downloaded to {zip_path}")
        
        # Extract
        print(f"\n[3] Extracting {zip_name}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(checkpoints_dir.parent)
        
        print(f"    [OK] Extracted to {checkpoints_dir.parent}")
        
        # Check structure
        if checkpoints_dir.exists():
            print(f"    [OK] Checkpoints directory created: {checkpoints_dir}")
            return True
        else:
            # Might be checkpoints_v2 instead
            alt_dir = checkpoints_dir.parent / "checkpoints_v2"
            if alt_dir.exists():
                print(f"    [INFO] Found checkpoints_v2, renaming to checkpoints...")
                alt_dir.rename(checkpoints_dir)
                return True
        
        return False
        
    except Exception as e:
        print(f"\n    [ERROR] Download failed: {e}")
        return False

def upload_checkpoints_to_space(space_id, hf_token, checkpoints_dir):
    """Upload checkpoints to Hugging Face Space"""
    print("\n" + "=" * 70)
    print(" Upload Checkpoints to Space")
    print("=" * 70)
    
    if not checkpoints_dir.exists():
        print(f"  [ERROR] {checkpoints_dir} not found")
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
    
    # Find all checkpoint files
    print(f"\n[2] Finding checkpoint files...")
    checkpoint_files = []
    
    for root, dirs, files in os.walk(checkpoints_dir):
        for file in files:
            if file.endswith(('.pth', '.json')):
                file_path = Path(root) / file
                rel_path = file_path.relative_to(checkpoints_dir)
                checkpoint_files.append((file_path, str(rel_path)))
    
    if not checkpoint_files:
        print("  [ERROR] No checkpoint files found")
        print(f"    Searched in: {checkpoints_dir}")
        return False
    
    print(f"  [OK] Found {len(checkpoint_files)} files")
    
    # Upload files
    print(f"\n[3] Uploading to Space: {space_id}")
    print(f"    This may take 10-30 minutes (files are large)...")
    
    try:
        api = HfApi()
        
        uploaded = 0
        failed = 0
        
        for i, (file_path, rel_path) in enumerate(checkpoint_files, 1):
            try:
                file_size_mb = file_path.stat().st_size / (1024 * 1024)
                print(f"    [{i}/{len(checkpoint_files)}] {rel_path} ({file_size_mb:.1f} MB)...", end=" ", flush=True)
                
                api.upload_file(
                    path_or_fileobj=str(file_path),
                    path_in_repo=f"checkpoints/{rel_path}",
                    repo_id=space_id,
                    repo_type="space",
                    commit_message=f"Add OpenVoice checkpoints" if i == 1 else None
                )
                uploaded += 1
                print("✅")
            except Exception as e:
                failed += 1
                print(f"❌ Error: {str(e)[:50]}")
        
        print(f"\n  [OK] Uploaded {uploaded}/{len(checkpoint_files)} files")
        if failed > 0:
            print(f"  [WARNING] {failed} files failed to upload")
        
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
    
    # Checkpoints directory
    checkpoints_dir = Path("openvoice_deploy/checkpoints")
    
    # Step 1: Check if checkpoints exist
    if checkpoints_dir.exists() and any(checkpoints_dir.rglob("*.pth")):
        print(f"\n[INFO] Found existing checkpoints at: {checkpoints_dir}")
        print(f"    Skipping download, proceeding to upload...")
    else:
        # Step 2: Download checkpoints
        print(f"\n[INFO] No checkpoints found, downloading...")
        success = download_checkpoints_from_url(checkpoints_dir)
        if not success:
            print("\n[ERROR] Failed to download checkpoints")
            print("\nManual Download Instructions:")
            print("1. Visit: https://github.com/myshell-ai/OpenVoice")
            print("2. Check README for checkpoint download links")
            print("3. Download and extract to: openvoice_deploy/checkpoints/")
            return
    
    # Step 3: Upload to Space
    print("\n" + "=" * 70)
    response = input("\nUpload checkpoints to Space? This will take 10-30 minutes. (y/n): ").strip().lower()
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
            print("\n[ERROR] Upload failed - some files may not have uploaded")
    else:
        print("\n[INFO] Skipped upload")

if __name__ == "__main__":
    main()

