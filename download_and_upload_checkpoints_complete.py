#!/usr/bin/env python3
"""
Complete script to download OpenVoice checkpoints and upload to Space
"""

import os
import requests
from pathlib import Path
from huggingface_hub import HfApi, login
import zipfile
import tempfile

def download_checkpoints_v1(checkpoints_dir):
    """Download OpenVoice V1 checkpoints (for the Space)"""
    print("=" * 70)
    print(" Download OpenVoice V1 Checkpoints")
    print("=" * 70)
    
    # V1 checkpoints URL (for the Space which uses V1 structure)
    url = "https://myshell-public-repo-host.s3.amazonaws.com/openvoice/checkpoints_1226.zip"
    zip_name = "checkpoints_1226.zip"
    
    print(f"\n[1] Downloading {zip_name}...")
    print(f"    URL: {url}")
    print(f"    Target: {checkpoints_dir}")
    
    try:
        # Create directory
        checkpoints_dir.parent.mkdir(parents=True, exist_ok=True)
        
        # Download
        print(f"    [INFO] Starting download (this may take 5-10 minutes)...")
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        print(f"    Size: {total_size / (1024*1024):.1f} MB")
        
        zip_path = checkpoints_dir.parent / zip_name
        
        with open(zip_path, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\r    Progress: {percent:.1f}% ({downloaded/(1024*1024):.1f} MB)", end='', flush=True)
        
        print(f"\n    [OK] Downloaded to {zip_path}")
        
        # Extract
        print(f"\n[2] Extracting {zip_name}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(checkpoints_dir.parent)
        
        print(f"    [OK] Extracted")
        
        # Verify structure
        if (checkpoints_dir / "base_speakers" / "EN" / "config.json").exists():
            print(f"    [OK] Checkpoints structure verified")
            return True
        else:
            print(f"    [WARNING] Checkpoints structure may be different")
            print(f"    [INFO] Checking what was extracted...")
            for item in checkpoints_dir.parent.iterdir():
                if item.is_dir():
                    print(f"      - {item.name}/")
            return False
        
    except Exception as e:
        print(f"\n    [ERROR] Download failed: {e}")
        import traceback
        traceback.print_exc()
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
    
    # Show file sizes
    total_size = sum(f.stat().st_size for f, _ in checkpoint_files)
    print(f"  Total size: {total_size / (1024*1024):.1f} MB")
    
    # Upload files
    print(f"\n[3] Uploading to Space: {space_id}")
    print(f"    [WARNING] This will take 10-30 minutes (files are large)")
    print(f"    [INFO] Uploading in batches...")
    
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
                    commit_message=f"Add OpenVoice V1 checkpoints" if i == 1 else None
                )
                uploaded += 1
                print("✅")
            except Exception as e:
                failed += 1
                error_msg = str(e)
                if len(error_msg) > 50:
                    error_msg = error_msg[:50] + "..."
                print(f"❌ {error_msg}")
        
        print(f"\n  [OK] Uploaded {uploaded}/{len(checkpoint_files)} files")
        if failed > 0:
            print(f"  [WARNING] {failed} files failed to upload")
            print(f"  [INFO] You may need to retry failed files")
        
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
    if checkpoints_dir.exists():
        has_checkpoints = any(checkpoints_dir.rglob("*.pth"))
        if has_checkpoints:
            print(f"\n[INFO] Found existing checkpoints at: {checkpoints_dir}")
            print(f"    Files found: {len(list(checkpoints_dir.rglob('*.pth')))} .pth files")
            skip_download = True
        else:
            skip_download = False
    else:
        skip_download = False
    
    if not skip_download:
        # Step 2: Download checkpoints
        print(f"\n[INFO] No checkpoints found, downloading...")
        print(f"    This will download ~500MB-1GB of files")
        response = input("    Continue? (y/n): ").strip().lower()
        if response != 'y':
            print("\n[INFO] Skipped download")
            print("\nManual Download:")
            print("1. Visit: https://github.com/myshell-ai/OpenVoice")
            print("2. Download: https://myshell-public-repo-host.s3.amazonaws.com/openvoice/checkpoints_1226.zip")
            print("3. Extract to: openvoice_deploy/checkpoints/")
            return
        
        success = download_checkpoints_from_url(checkpoints_dir)
        if not success:
            print("\n[ERROR] Failed to download checkpoints")
            return
    
    # Step 3: Upload to Space
    print("\n" + "=" * 70)
    print(" Upload Checkpoints to Space")
    print("=" * 70)
    print("\n[WARNING] This will upload large files (10-30 minutes)")
    response = input("Continue? (y/n): ").strip().lower()
    if response == 'y':
        success = upload_checkpoints_to_space(space_id, hf_token, checkpoints_dir)
        if success:
            print("\n" + "=" * 70)
            print(" Checkpoints Uploaded!")
            print("=" * 70)
            print(f"\n✅ Checkpoints uploaded to Space")
            print(f"✅ Space will automatically detect new files")
            print(f"✅ You may need to restart the Space")
            print(f"\nCheck status: https://huggingface.co/spaces/{space_id}")
        else:
            print("\n[ERROR] Upload failed - check errors above")
    else:
        print("\n[INFO] Skipped upload")

def download_checkpoints_from_url(checkpoints_dir):
    """Download checkpoints"""
    url = "https://myshell-public-repo-host.s3.amazonaws.com/openvoice/checkpoints_1226.zip"
    zip_name = "checkpoints_1226.zip"
    
    try:
        checkpoints_dir.parent.mkdir(parents=True, exist_ok=True)
        zip_path = checkpoints_dir.parent / zip_name
        
        print(f"    Downloading {zip_name}...")
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        print(f"    Size: {total_size / (1024*1024):.1f} MB")
        
        with open(zip_path, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\r    Progress: {percent:.1f}%", end='', flush=True)
        
        print(f"\n    [OK] Downloaded")
        
        print(f"    Extracting...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(checkpoints_dir.parent)
        
        print(f"    [OK] Extracted")
        
        # Check if checkpoints directory exists
        if checkpoints_dir.exists():
            return True
        # Might have extracted to a different name
        for item in checkpoints_dir.parent.iterdir():
            if item.is_dir() and 'checkpoint' in item.name.lower():
                print(f"    [INFO] Found {item.name}, renaming to checkpoints...")
                item.rename(checkpoints_dir)
                return True
        
        return False
        
    except Exception as e:
        print(f"\n    [ERROR] {e}")
        return False

if __name__ == "__main__":
    main()

