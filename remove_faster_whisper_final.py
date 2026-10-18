#!/usr/bin/env python3
"""
Remove faster-whisper from requirements.txt - we made it optional in code
"""

import os
from huggingface_hub import HfApi, login
import tempfile

def remove_faster_whisper(space_id, hf_token):
    """Remove faster-whisper and whisper-timestamped from requirements.txt"""
    print("=" * 70)
    print(" Remove faster-whisper from requirements.txt")
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
    
    # Create requirements without faster-whisper
    requirements_content = """# Core ML/AI
torch>=2.0.0
torchaudio>=2.0.0

# Audio processing
librosa==0.9.1
soundfile>=0.10.0
pydub==0.25.1
# faster-whisper==0.9.0  # Optional - only needed if vad=False, requires FFmpeg dev libs
wavmark==0.0.3

# Scientific computing
numpy==1.22.0
scipy>=1.7.0

# Text processing
eng_to_ipa==0.0.2
inflect==7.0.0
unidecode==1.3.7
# whisper-timestamped==1.14.2  # Optional - depends on faster-whisper
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
    
    print(f"\n[2] Uploading requirements.txt without faster-whisper...")
    print(f"    Space: {space_id}")
    print(f"    [INFO] faster-whisper removed (made optional in se_extractor.py)")
    print(f"    [INFO] whisper-timestamped removed (depends on faster-whisper)")
    
    try:
        api = HfApi()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(requirements_content)
            temp_path = f.name
        
        try:
            api.upload_file(
                path_or_fileobj=temp_path,
                path_in_repo="requirements.txt",
                repo_id=space_id,
                repo_type="space",
                commit_message="Remove faster-whisper from requirements - made optional in code, requires FFmpeg dev libs"
            )
            print("  [OK] requirements.txt uploaded (without faster-whisper)")
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
    
    success = remove_faster_whisper(space_id, hf_token)
    
    if success:
        print("\n" + "=" * 70)
        print(" faster-whisper Removed!")
        print("=" * 70)
        print(f"\n✅ Removed faster-whisper from requirements.txt")
        print(f"✅ Removed whisper-timestamped (depends on faster-whisper)")
        print(f"✅ faster-whisper is optional in code (se_extractor.py)")
        print(f"\nThe Space will rebuild without faster-whisper.")
        print(f"OpenVoice will use VAD (vad=True) by default, which doesn't need faster-whisper.")
        print(f"\nCheck status: https://huggingface.co/spaces/{space_id}")
    else:
        print("\n[ERROR] Failed.")

if __name__ == "__main__":
    main()

