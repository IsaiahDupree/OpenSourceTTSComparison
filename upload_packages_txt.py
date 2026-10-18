#!/usr/bin/env python3
"""
Upload packages.txt to install FFmpeg development libraries needed for faster-whisper
"""

import os
from huggingface_hub import HfApi, login
import tempfile

def upload_packages_txt(space_id, hf_token):
    """Upload packages.txt with FFmpeg dev libraries"""
    print("=" * 70)
    print(" Upload packages.txt for FFmpeg Dev Libraries")
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
    
    # packages.txt for system dependencies
    packages_content = """ffmpeg
libavformat-dev
libavcodec-dev
libavdevice-dev
libavutil-dev
libavfilter-dev
libswscale-dev
libswresample-dev
pkg-config
"""
    
    print(f"\n[2] Uploading packages.txt...")
    print(f"    Space: {space_id}")
    print(f"    [INFO] Adding FFmpeg development libraries for faster-whisper")
    
    try:
        api = HfApi()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(packages_content)
            temp_path = f.name
        
        try:
            api.upload_file(
                path_or_fileobj=temp_path,
                path_in_repo="packages.txt",
                repo_id=space_id,
                repo_type="space",
                commit_message="Add packages.txt with FFmpeg dev libraries for faster-whisper"
            )
            print("  [OK] packages.txt uploaded")
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
    
    success = upload_packages_txt(space_id, hf_token)
    
    if success:
        print("\n" + "=" * 70)
        print(" packages.txt Uploaded!")
        print("=" * 70)
        print(f"\nNow uploading requirements.txt with faster-whisper...")
        
        # Now upload requirements.txt with faster-whisper
        from upload_complete_requirements import upload_complete_requirements
        upload_complete_requirements(space_id, hf_token)
        
        print(f"\nCheck status: https://huggingface.co/spaces/{space_id}")
        print("\nThe Space will rebuild with FFmpeg dev libraries and faster-whisper.")
    else:
        print("\n[ERROR] Upload failed.")

if __name__ == "__main__":
    main()

