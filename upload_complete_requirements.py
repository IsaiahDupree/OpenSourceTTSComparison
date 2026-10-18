#!/usr/bin/env python3
"""
Upload complete requirements.txt with all OpenVoice dependencies including torch
"""

import os
from huggingface_hub import HfApi, login
import tempfile

def upload_complete_requirements(space_id, hf_token):
    """Upload complete requirements.txt with all dependencies"""
    print("=" * 70)
    print(" Upload Complete Requirements.txt")
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
    
    # Complete requirements based on OpenVoice needs
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
    
    print(f"\n[2] Uploading requirements.txt...")
    print(f"    Space: {space_id}")
    
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
                commit_message="Add complete requirements.txt with torch and all OpenVoice dependencies"
            )
            print("  [OK] requirements.txt uploaded")
            print("  [INFO] Space will rebuild with all dependencies")
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
    
    success = upload_complete_requirements(space_id, hf_token)
    
    if success:
        print("\n" + "=" * 70)
        print(" Complete Requirements Uploaded!")
        print("=" * 70)
        print(f"\nThe Space will rebuild with all dependencies including torch.")
        print(f"Check status: https://huggingface.co/spaces/{space_id}")
        print("\nWait 2-3 minutes for rebuild (torch is large, takes time to install).")
    else:
        print("\n[ERROR] Upload failed.")

if __name__ == "__main__":
    main()

