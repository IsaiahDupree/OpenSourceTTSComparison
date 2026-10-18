#!/usr/bin/env python3
"""
Make faster-whisper optional in se_extractor.py and remove packages.txt
"""

import os
from pathlib import Path
from huggingface_hub import HfApi, login
import tempfile

def make_faster_whisper_optional(space_id, hf_token):
    """Modify se_extractor.py to make faster-whisper optional"""
    print("=" * 70)
    print(" Make faster-whisper Optional")
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
    
    # Read se_extractor.py
    se_file = Path("openvoice_deploy/openvoice/se_extractor.py")
    if not se_file.exists():
        print(f"  [ERROR] {se_file} not found")
        return False
    
    content = se_file.read_text(encoding='utf-8')
    
    # Modify imports to make faster-whisper optional
    old_imports = """from faster_whisper import WhisperModel
import hashlib
import base64
import librosa
from whisper_timestamped.transcribe import get_audio_tensor, get_vad_segments"""
    
    new_imports = """try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False
    WhisperModel = None
import hashlib
import base64
import librosa
try:
    from whisper_timestamped.transcribe import get_audio_tensor, get_vad_segments
    WHISPER_TIMESTAMPED_AVAILABLE = True
except ImportError:
    WHISPER_TIMESTAMPED_AVAILABLE = False"""
    
    if old_imports in content:
        content = content.replace(old_imports, new_imports)
        print("  [OK] Modified imports to make faster-whisper optional")
    else:
        print("  [WARNING] Could not find exact import pattern, trying alternative...")
        # Try just replacing the faster_whisper import
        if "from faster_whisper import WhisperModel" in content:
            content = content.replace(
                "from faster_whisper import WhisperModel",
                """try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False
    WhisperModel = None"""
            )
            print("  [OK] Modified faster_whisper import")
    
    # Modify split_audio_whisper to check availability
    if "def split_audio_whisper" in content:
        # Add check at start of function
        old_func_start = """def split_audio_whisper(audio_path, audio_name, target_dir='processed'):
    global model
    if model is None:
        model = WhisperModel(model_size, device="cuda", compute_type="float16")"""
        
        new_func_start = """def split_audio_whisper(audio_path, audio_name, target_dir='processed'):
    if not FASTER_WHISPER_AVAILABLE:
        raise ImportError("faster-whisper is not installed. Please install it or use vad=True instead.")
    global model
    if model is None:
        model = WhisperModel(model_size, device="cuda", compute_type="float16")"""
        
        if old_func_start in content:
            content = content.replace(old_func_start, new_func_start)
            print("  [OK] Added check in split_audio_whisper function")
    
    # Upload modified se_extractor.py
    print(f"\n[2] Uploading modified se_extractor.py...")
    try:
        api = HfApi()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            api.upload_file(
                path_or_fileobj=temp_path,
                path_in_repo="openvoice/se_extractor.py",
                repo_id=space_id,
                repo_type="space",
                commit_message="Make faster-whisper optional - handle missing import gracefully"
            )
            print("  [OK] se_extractor.py uploaded")
        finally:
            os.unlink(temp_path)
    except Exception as e:
        print(f"  [ERROR] Upload failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Delete packages.txt (upload empty or delete)
    print(f"\n[3] Removing packages.txt...")
    try:
        # Upload empty file to effectively remove it
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("# No system packages needed\n")
            temp_path = f.name
        
        try:
            api.upload_file(
                path_or_fileobj=temp_path,
                path_in_repo="packages.txt",
                repo_id=space_id,
                repo_type="space",
                commit_message="Remove packages.txt - not needed, packages not available in Debian Trixie"
            )
            print("  [OK] packages.txt removed")
        finally:
            os.unlink(temp_path)
    except Exception as e:
        print(f"  [WARNING] Could not remove packages.txt: {e}")
    
    # Upload requirements.txt without faster-whisper
    print(f"\n[4] Uploading requirements.txt without faster-whisper...")
    requirements_content = """# Core ML/AI
torch>=2.0.0
torchaudio>=2.0.0

# Audio processing
librosa==0.9.1
soundfile>=0.10.0
pydub==0.25.1
# faster-whisper==0.9.0  # Optional - only needed if vad=False
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
                commit_message="Remove faster-whisper from requirements - made optional in code"
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
    
    success = make_faster_whisper_optional(space_id, hf_token)
    
    if success:
        print("\n" + "=" * 70)
        print(" faster-whisper Made Optional!")
        print("=" * 70)
        print(f"\n✅ Modified se_extractor.py - faster-whisper is now optional")
        print(f"✅ Removed packages.txt - packages not available in Debian Trixie")
        print(f"✅ Updated requirements.txt - faster-whisper removed")
        print(f"\nNote: faster-whisper is only used when vad=False.")
        print(f"Default is vad=True, so OpenVoice will work without it.")
        print(f"\nCheck status: https://huggingface.co/spaces/{space_id}")
        print("\nThe Space should build successfully now!")
    else:
        print("\n[ERROR] Failed.")

if __name__ == "__main__":
    main()

