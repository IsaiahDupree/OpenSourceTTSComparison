#!/usr/bin/env python3
"""
Fix app.py to handle missing checkpoints gracefully - make loading lazy
"""

import os
from huggingface_hub import HfApi, login
import tempfile

def fix_checkpoint_loading(space_id, hf_token):
    """Modify app.py to load checkpoints lazily or handle missing files"""
    print("=" * 70)
    print(" Fix Checkpoint Loading in app.py")
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
    
    # Read app.py
    app_file = "openvoice_deploy/app.py"
    if not os.path.exists(app_file):
        print(f"  [ERROR] {app_file} not found")
        return False
    
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Modify to load checkpoints lazily (only when predict is called)
    # Or add error handling for missing checkpoints
    
    # Find the checkpoint loading section
    old_loading = """# load models
en_base_speaker_tts = BaseSpeakerTTS(f'{en_ckpt_base}/config.json', device=device)
en_base_speaker_tts.load_ckpt(f'{en_ckpt_base}/checkpoint.pth')
zh_base_speaker_tts = BaseSpeakerTTS(f'{zh_ckpt_base}/config.json', device=device)
zh_base_speaker_tts.load_ckpt(f'{zh_ckpt_base}/checkpoint.pth')
tone_color_converter = ToneColorConverter(f'{ckpt_converter}/config.json', device=device)
tone_color_converter.load_ckpt(f'{ckpt_converter}/checkpoint.pth')

# load speaker embeddings
en_source_default_se = torch.load(f'{en_ckpt_base}/en_default_se.pth').to(device)
en_source_style_se = torch.load(f'{en_ckpt_base}/en_style_se.pth').to(device)
zh_source_se = torch.load(f'{zh_ckpt_base}/zh_default_se.pth').to(device)"""
    
    new_loading = """# Models will be loaded lazily on first use
en_base_speaker_tts = None
zh_base_speaker_tts = None
tone_color_converter = None
en_source_default_se = None
en_source_style_se = None
zh_source_se = None

def load_models():
    \"\"\"Load models on first use\"\"\"
    global en_base_speaker_tts, zh_base_speaker_tts, tone_color_converter
    global en_source_default_se, en_source_style_se, zh_source_se
    
    if en_base_speaker_tts is None:
        # Check if checkpoints exist
        if not os.path.exists(f'{en_ckpt_base}/config.json'):
            raise FileNotFoundError(
                f'Checkpoints not found at {en_ckpt_base}. '
                'Please download checkpoints from: https://github.com/myshell-ai/OpenVoice#checkpoint-download'
            )
        
        # load models
        en_base_speaker_tts = BaseSpeakerTTS(f'{en_ckpt_base}/config.json', device=device)
        en_base_speaker_tts.load_ckpt(f'{en_ckpt_base}/checkpoint.pth')
        zh_base_speaker_tts = BaseSpeakerTTS(f'{zh_ckpt_base}/config.json', device=device)
        zh_base_speaker_tts.load_ckpt(f'{zh_ckpt_base}/checkpoint.pth')
        tone_color_converter = ToneColorConverter(f'{ckpt_converter}/config.json', device=device)
        tone_color_converter.load_ckpt(f'{ckpt_converter}/checkpoint.pth')
        
        # load speaker embeddings
        en_source_default_se = torch.load(f'{en_ckpt_base}/en_default_se.pth').to(device)
        en_source_style_se = torch.load(f'{en_ckpt_base}/en_style_se.pth').to(device)
        zh_source_se = torch.load(f'{zh_ckpt_base}/zh_default_se.pth').to(device)"""
    
    if old_loading in content:
        content = content.replace(old_loading, new_loading)
        print("  [OK] Modified checkpoint loading to be lazy")
    else:
        print("  [WARNING] Could not find exact checkpoint loading pattern")
        # Try a different approach - just wrap in try/except
        return False
    
    # Modify predict function to load models on first call
    old_predict_start = """def predict(prompt, style, audio_file_pth, agree):
    # initialize a empty info
    text_hint = ''"""
    
    new_predict_start = """def predict(prompt, style, audio_file_pth, agree):
    # Load models on first use
    load_models()
    
    # initialize a empty info
    text_hint = ''"""
    
    if old_predict_start in content:
        content = content.replace(old_predict_start, new_predict_start)
        print("  [OK] Modified predict function to load models lazily")
    else:
        # Try to find the predict function
        if "def predict(" in content:
            lines = content.split('\n')
            new_lines = []
            for i, line in enumerate(lines):
                if line.strip().startswith("def predict("):
                    new_lines.append(line)
                    # Find the next non-empty line
                    for j in range(i+1, min(i+5, len(lines))):
                        if lines[j].strip() and not lines[j].strip().startswith('#'):
                            # Insert load_models() before this line
                            new_lines.append("    # Load models on first use")
                            new_lines.append("    load_models()")
                            new_lines.append("")
                            break
                    continue
                new_lines.append(line)
            content = '\n'.join(new_lines)
            print("  [OK] Added lazy loading to predict function")
    
    # Upload fixed app.py
    print(f"\n[2] Uploading fixed app.py...")
    try:
        api = HfApi()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            api.upload_file(
                path_or_fileobj=temp_path,
                path_in_repo="app.py",
                repo_id=space_id,
                repo_type="space",
                commit_message="Make checkpoint loading lazy - load on first predict call instead of at startup"
            )
            print("  [OK] app.py uploaded")
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
    
    success = fix_checkpoint_loading(space_id, hf_token)
    
    if success:
        print("\n" + "=" * 70)
        print(" Checkpoint Loading Fixed!")
        print("=" * 70)
        print(f"\n✅ Modified app.py to load checkpoints lazily")
        print(f"✅ Models will load on first predict() call, not at startup")
        print(f"✅ Will show clear error if checkpoints are missing")
        print(f"\nNote: Checkpoints still need to be uploaded to the Space.")
        print(f"Check status: https://huggingface.co/spaces/{space_id}")
    else:
        print("\n[ERROR] Failed.")

if __name__ == "__main__":
    main()

