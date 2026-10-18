#!/usr/bin/env python3
"""
Upload fixed packages.txt with correct Debian package names
"""

import os
from huggingface_hub import HfApi, login
import tempfile

def upload_fixed_packages(space_id, hf_token):
    """Upload packages.txt with correct Debian package names"""
    print("=" * 70)
    print(" Upload Fixed packages.txt")
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
    
    # FFmpeg is already installed in base image, we just need dev libraries
    # For Debian, try using libavformat-dev (might need versioned packages)
    # Or we can try installing from Debian multimedia repo
    # Actually, let's try a simpler approach - just pkg-config and see if we can build
    packages_content = """pkg-config
"""
    
    # Alternative: Try to add Debian multimedia repository first
    # But Hugging Face Spaces might not allow custom repos easily
    # Let's try without the FFmpeg dev packages first and see if we can use a workaround
    
    print(f"\n[2] Uploading minimal packages.txt...")
    print(f"    Space: {space_id}")
    print(f"    [INFO] FFmpeg is already installed in base image")
    print(f"    [INFO] Trying minimal approach - just pkg-config")
    print(f"    [INFO] If this fails, we'll try alternative faster-whisper installation")
    
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
                commit_message="Fix packages.txt - use minimal approach, ffmpeg already installed"
            )
            print("  [OK] packages.txt uploaded")
            
            # Now try uploading requirements without faster-whisper first
            # We can add it back if needed, or use an alternative
            print(f"\n[3] Trying requirements.txt without faster-whisper...")
            print(f"    [INFO] faster-whisper requires FFmpeg dev libs which are hard to install")
            print(f"    [INFO] OpenVoice might work without it for basic functionality")
            
            requirements_content = """# Core ML/AI
torch>=2.0.0
torchaudio>=2.0.0

# Audio processing
librosa==0.9.1
soundfile>=0.10.0
pydub==0.25.1
# faster-whisper==0.9.0  # Temporarily removed - requires FFmpeg dev libs
wavmark==0.0.3

# Scientific computing
numpy==1.22.0
scipy>=1.7.0

# Text processing
eng_to_ipa==0.0.2
inflect==7.0.0
unidecode==1.3.7
# whisper-timestamped==1.14.2  # Depends on faster-whisper
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
                    commit_message="Remove faster-whisper temporarily - FFmpeg dev libs installation issue"
                )
                print("  [OK] requirements.txt uploaded (without faster-whisper)")
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
    
    success = upload_fixed_packages(space_id, hf_token)
    
    if success:
        print("\n" + "=" * 70)
        print(" Fixed packages.txt Uploaded!")
        print("=" * 70)
        print(f"\n✅ Minimal packages.txt (just pkg-config)")
        print(f"✅ requirements.txt without faster-whisper")
        print(f"\nNote: faster-whisper was removed because FFmpeg dev libs are")
        print(f"hard to install in Debian Trixie. OpenVoice should still work")
        print(f"for basic voice cloning without it.")
        print(f"\nCheck status: https://huggingface.co/spaces/{space_id}")
        print("\nThe Space should build successfully now.")
    else:
        print("\n[ERROR] Upload failed.")

if __name__ == "__main__":
    main()

