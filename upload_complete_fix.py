#!/usr/bin/env python3
"""
Upload both packages.txt and requirements.txt with faster-whisper
"""

import os
from huggingface_hub import HfApi, login
import tempfile

def upload_both_files(space_id, hf_token):
    """Upload packages.txt and requirements.txt"""
    print("=" * 70)
    print(" Upload Complete Fix: packages.txt + requirements.txt")
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
    
    api = HfApi()
    
    # Upload packages.txt
    print(f"\n[2] Uploading packages.txt...")
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
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(packages_content)
            temp_path = f.name
        
        try:
            api.upload_file(
                path_or_fileobj=temp_path,
                path_in_repo="packages.txt",
                repo_id=space_id,
                repo_type="space",
                commit_message="Add packages.txt with FFmpeg dev libraries"
            )
            print("  [OK] packages.txt uploaded")
        finally:
            os.unlink(temp_path)
    except Exception as e:
        print(f"  [ERROR] Failed to upload packages.txt: {e}")
        return False
    
    # Upload requirements.txt with faster-whisper
    print(f"\n[3] Uploading requirements.txt with faster-whisper...")
    requirements_content = """# Core ML/AI
torch>=2.0.0
torchaudio>=2.0.0

# Audio processing
librosa==0.9.1
soundfile>=0.10.0
pydub==0.25.1
faster-whisper==0.9.0
wavmark==0.0.3

# Scientific computing
numpy==1.22.0
scipy>=1.7.0

# Text processing
eng_to_ipa==0.0.2
inflect==7.0.0
unidecode==1.3.7
whisper-timestamped==1.14.2
pypinyin==0.50.0
cn2an==0.5.22
jieba==0.42.1
langid==1.1.6

# Web interface
gradio>=4.0.0

# Utilities
openai
python-dotenv
"""
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(requirements_content)
            temp_path = f.name
        
        try:
            api.upload_file(
                path_or_fileobj=temp_path,
                path_in_repo="requirements.txt",
                repo_id=space_id,
                repo_type="space",
                commit_message="Add complete requirements.txt with faster-whisper (FFmpeg dev libs now available)"
            )
            print("  [OK] requirements.txt uploaded")
            return True
        finally:
            os.unlink(temp_path)
    except Exception as e:
        print(f"  [ERROR] Failed to upload requirements.txt: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    space_id = "theisaiahdupree/OpenVoiceV2"
    hf_token = os.getenv("HF_TOKEN", __import__('os').environ['HF_TOKEN'])
    
    print(f"[INFO] Using token: {hf_token[:10]}...{hf_token[-10:]}")
    
    success = upload_both_files(space_id, hf_token)
    
    if success:
        print("\n" + "=" * 70)
        print(" Complete Fix Uploaded!")
        print("=" * 70)
        print(f"\n✅ packages.txt - FFmpeg dev libraries")
        print(f"✅ requirements.txt - All dependencies including faster-whisper")
        print(f"\nThe Space will rebuild with all dependencies.")
        print(f"Check status: https://huggingface.co/spaces/{space_id}")
        print("\nWait 3-5 minutes for rebuild (torch + faster-whisper are large).")
    else:
        print("\n[ERROR] Upload failed.")

if __name__ == "__main__":
    main()

