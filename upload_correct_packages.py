#!/usr/bin/env python3
"""
Upload packages.txt with correct Debian package names for FFmpeg dev libraries
"""

import os
from huggingface_hub import HfApi, login
import tempfile

def upload_correct_packages(space_id, hf_token):
    """Upload packages.txt with correct Debian package names"""
    print("=" * 70)
    print(" Upload Correct packages.txt for Debian")
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
    
    # For Debian, FFmpeg dev packages might be named differently
    # Try using libavformat-dev (standard name) or we might need to add repo
    # Actually, let's try building faster-whisper with system FFmpeg that's already installed
    # Or use a pre-built wheel approach
    
    # Alternative: Try installing from pip with system FFmpeg
    # But first, let's try the standard Debian package names
    packages_content = """pkg-config
build-essential
"""
    
    print(f"\n[2] Uploading packages.txt with build tools...")
    print(f"    Space: {space_id}")
    print(f"    [INFO] Adding build-essential for compiling faster-whisper")
    print(f"    [INFO] FFmpeg runtime is already installed in base image")
    print(f"    [INFO] Will try to build faster-whisper with system FFmpeg")
    
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
                commit_message="Add build-essential for faster-whisper compilation"
            )
            print("  [OK] packages.txt uploaded")
            
            # Now upload requirements with faster-whisper
            # We'll try to build it with the system FFmpeg
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
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f2:
                f2.write(requirements_content)
                temp_path2 = f2.name
            
            try:
                api.upload_file(
                    path_or_fileobj=temp_path2,
                    path_in_repo="requirements.txt",
                    repo_id=space_id,
                    repo_type="space",
                    commit_message="Add faster-whisper back - will try to build with system FFmpeg"
                )
                print("  [OK] requirements.txt uploaded (with faster-whisper)")
                print("  [INFO] If build fails, we may need to modify se_extractor.py")
                return True
            finally:
                os.unlink(temp_path2)
                
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
    
    success = upload_correct_packages(space_id, hf_token)
    
    if success:
        print("\n" + "=" * 70)
        print(" Packages Uploaded!")
        print("=" * 70)
        print(f"\n✅ packages.txt - build-essential for compilation")
        print(f"✅ requirements.txt - with faster-whisper")
        print(f"\nThe Space will try to build faster-whisper with system FFmpeg.")
        print(f"If this fails, we may need to modify the code to make it optional.")
        print(f"\nCheck status: https://huggingface.co/spaces/{space_id}")
    else:
        print("\n[ERROR] Upload failed.")

if __name__ == "__main__":
    main()

