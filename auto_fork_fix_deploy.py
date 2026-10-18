#!/usr/bin/env python3
"""
Fully Automated Fork, Fix, and Deploy
======================================
Agentically forks OpenVoice, fixes Gradio issues, and deploys to HF Space.
"""

import os
import sys
import subprocess
import re
from pathlib import Path
import shutil

def check_requirements():
    """Check all requirements are met"""
    requirements = {
        "git": False,
        "github_token": False,
        "hf_token": False,
        "huggingface_hub": False
    }
    
    # Check git
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        requirements["git"] = True
    except:
        print("[ERROR] Git not installed")
    
    # Check GitHub token
    github_token = os.getenv("GITHUB_TOKEN")
    if github_token:
        requirements["github_token"] = True
    else:
        print("[INFO] GITHUB_TOKEN not set (will need manual fork)")
    
    # Check HF token
    hf_token = os.getenv("HF_TOKEN")
    if hf_token:
        requirements["hf_token"] = True
    else:
        print("[ERROR] HF_TOKEN not set")
    
    # Check huggingface_hub
    try:
        import huggingface_hub
        requirements["huggingface_hub"] = True
    except ImportError:
        print("[INFO] huggingface_hub not installed (pip install huggingface_hub)")
    
    return requirements

def fix_app_py_file(file_path):
    """Fix app.py file automatically"""
    print(f"\n  Fixing: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    fixes = []
    
    # Remove info parameter from gr.Audio (multiple patterns)
    patterns_to_fix = [
        (r',\s*info\s*=\s*["\'][^"\']*["\']', ''),  # info with comma before
        (r'info\s*=\s*["\'][^"\']*["\']\s*,?\s*\n', '\n'),  # info on its own line
        (r'info\s*=\s*["\'][^"\']*["\']\s*,?\s*', ''),  # info with optional comma
    ]
    
    for pattern, replacement in patterns_to_fix:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            fixes.append("Removed 'info' parameter")
    
    # Remove max_choices when multiselect=False
    if 'max_choices' in content and 'multiselect=False' in content:
        content = re.sub(r',?\s*max_choices\s*=\s*\d+\s*,?\s*', '', content)
        fixes.append("Removed 'max_choices' parameter")
    
    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"    [OK] Applied {len(set(fixes))} fixes")
        return True
    else:
        print(f"    [INFO] No fixes needed")
        return False

def main():
    print("=" * 70)
    print(" Automated Fork, Fix, and Deploy")
    print("=" * 70)
    
    # Check requirements
    print("\n[0] Checking requirements...")
    reqs = check_requirements()
    
    if not reqs["git"]:
        print("\n[ERROR] Git is required. Install from: https://git-scm.com/downloads")
        return
    
    if not reqs["hf_token"]:
        print("\n[ERROR] HF_TOKEN is required")
        print("  Set with: $env:HF_TOKEN='your_token'")
        return
    
    # Configuration
    original_repo = "https://github.com/myshell-ai/OpenVoice.git"
    github_username = os.getenv("GITHUB_USERNAME", "theisaiahdupree")  # Your GitHub username
    fork_repo_name = "OpenVoice"  # Name for your fork
    space_id = "theisaiahdupree/OpenVoiceV2"
    work_dir = Path("openvoice_deploy")
    
    print(f"\n[1] Setting up repository...")
    print(f"    Original: {original_repo}")
    print(f"    Working directory: {work_dir}")
    
    # Clone repository
    if work_dir.exists():
        print("    [INFO] Directory exists, cleaning...")
        shutil.rmtree(work_dir)
    
    print("    [INFO] Cloning repository...")
    subprocess.run(["git", "clone", original_repo, str(work_dir)], check=True)
    print("    [OK] Repository cloned")
    
    # Find app.py
    print(f"\n[2] Finding app.py...")
    app_files = list(work_dir.rglob("app.py"))
    
    if not app_files:
        print("    [ERROR] app.py not found")
        print("    Searched in:", work_dir)
        return
    
    # Fix all app.py files found
    fixed_any = False
    for app_file in app_files:
        if "OpenVoiceV2" in str(app_file) or "space" in str(app_file).lower() or len(app_files) == 1:
            if fix_app_py_file(app_file):
                fixed_any = True
    
    if not fixed_any:
        print("    [WARNING] No fixes applied")
    
    # Commit changes
    print(f"\n[3] Committing fixes...")
    try:
        subprocess.run(["git", "add", "."], cwd=work_dir, check=True)
        subprocess.run(["git", "commit", "-m", "Fix Gradio compatibility - remove info parameter"], 
                      cwd=work_dir, check=True)
        print("    [OK] Changes committed")
    except subprocess.CalledProcessError as e:
        print(f"    [WARNING] Commit failed: {e}")
        print("    (This is OK if no changes were made)")
    
    # Instructions for next steps
    print("\n" + "=" * 70)
    print(" Next Steps")
    print("=" * 70)
    
    print("\n[Option A] Push to Your GitHub Fork")
    print("-" * 70)
    print("""
1. Fork the repo on GitHub:
   https://github.com/myshell-ai/OpenVoice
   (Click "Fork" button)

2. Add your fork as remote:
   cd openvoice_deploy
   git remote add fork https://github.com/YOUR_USERNAME/OpenVoice.git
   git push fork main

3. Connect Space to GitHub:
   - Go to: https://huggingface.co/spaces/theisaiahdupree/OpenVoiceV2
   - Settings → Repository
   - Connect to your GitHub fork
   - Space will auto-deploy!
""")
    
    print("\n[Option B] Deploy Directly to Space")
    print("-" * 70)
    if reqs["huggingface_hub"]:
        print("    [INFO] huggingface_hub available - can deploy directly")
        try:
            from huggingface_hub import HfApi
            api = HfApi(token=os.getenv("HF_TOKEN"))
            
            # Upload fixed app.py
            app_file = app_files[0]
            print(f"\n    Uploading {app_file.name} to Space...")
            api.upload_file(
                path_or_fileobj=str(app_file),
                path_in_repo="app.py",
                repo_id=space_id,
                repo_type="space"
            )
            print(f"    [SUCCESS] Deployed to: https://huggingface.co/spaces/{space_id}")
        except Exception as e:
            print(f"    [ERROR] Direct deployment failed: {e}")
            print("    Use Option A instead")
    else:
        print("    [INFO] Install huggingface_hub for direct deployment:")
        print("    pip install huggingface_hub")
    
    print("\n[Option C] Manual Upload")
    print("-" * 70)
    print(f"""
1. Go to: https://huggingface.co/spaces/{space_id}
2. Click "Files" tab
3. Click "app.py"
4. Copy the fixed content from: {app_files[0]}
5. Paste and commit
""")
    
    print("\n" + "=" * 70)
    print(" Fixed files are in: openvoice_deploy/")
    print("=" * 70)

if __name__ == "__main__":
    main()

