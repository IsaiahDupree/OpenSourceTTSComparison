#!/usr/bin/env python3
"""
Upload complete requirements.txt to the Space with all necessary dependencies
"""

import os
from pathlib import Path
from huggingface_hub import HfApi, login
import tempfile

def upload_requirements(space_id, hf_token):
    """Upload complete requirements.txt to the Space"""
    print("=" * 70)
    print(" Upload Requirements.txt to Space")
    print("=" * 70)
    
    # Login
    print(f"\n[1] Logging in to Hugging Face...")
    try:
        os.environ["HF_TOKEN"] = hf_token
        login(token=hf_token, write_permission=True)
        print("  [OK] Logged in")
    except Exception as e:
        print(f"  [ERROR] Login failed: {e}")
        return False
    
    # Create complete requirements.txt
    print(f"\n[2] Creating complete requirements.txt...")
    
    requirements_content = """torch>=2.0.0
torchaudio>=2.0.0
librosa==0.9.1
faster-whisper==0.9.0
pydub==0.25.1
wavmark==0.0.3
numpy==1.22.0
eng_to_ipa==0.0.2
inflect==7.0.0
unidecode==1.3.7
whisper-timestamped==1.14.2
openai
python-dotenv
pypinyin==0.50.0
cn2an==0.5.22
jieba==0.42.1
gradio>=4.0.0
langid==1.1.6
scipy
soundfile
"""
    
    print(f"  [OK] Created requirements.txt ({len(requirements_content)} characters)")
    print("  [INFO] Includes: torch, torchaudio, gradio, and all OpenVoice dependencies")
    
    # Upload to Space
    print(f"\n[3] Uploading requirements.txt to Space...")
    print(f"    Space: {space_id}")
    
    try:
        api = HfApi()
        
        # Upload the file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(requirements_content)
            temp_path = f.name
        
        try:
            api.upload_file(
                path_or_fileobj=temp_path,
                path_in_repo="requirements.txt",
                repo_id=space_id,
                repo_type="space",
                commit_message="Add complete requirements.txt with torch and all dependencies"
            )
            print("  [OK] requirements.txt uploaded successfully")
            print("  [INFO] Space will rebuild automatically with all dependencies")
            return True
        finally:
            # Clean up temp file
            os.unlink(temp_path)
            
    except Exception as e:
        print(f"  [ERROR] Upload failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    space_id = "theisaiahdupree/OpenVoiceV2"
    hf_token = os.getenv("HF_TOKEN", __import__('os').environ['HF_TOKEN'])
    
    if not hf_token:
        print("[ERROR] HF_TOKEN not set")
        return
    
    print(f"[INFO] Using token: {hf_token[:10]}...{hf_token[-10:]}")
    
    success = upload_requirements(space_id, hf_token)
    
    if success:
        print("\n" + "=" * 70)
        print(" Requirements Uploaded!")
        print("=" * 70)
        print(f"\nThe Space will rebuild automatically with all dependencies.")
        print(f"Check status at: https://huggingface.co/spaces/{space_id}")
        print("\nWait 2-3 minutes for the rebuild to complete (installing dependencies).")
    else:
        print("\n[ERROR] Upload failed. Please check the errors above.")

if __name__ == "__main__":
    main()

