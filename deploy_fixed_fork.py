#!/usr/bin/env python3
"""
Automated deployment script for fixed OpenVoice fork to Hugging Face Space
This script fixes the Gradio compatibility issue and prepares for deployment.
"""

import os
import subprocess
import sys
from pathlib import Path

def check_requirements():
    """Check if required tools are available"""
    requirements = {
        "git": False,
        "hf_token": False,
    }
    
    # Check Git
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        requirements["git"] = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Check HF Token
    hf_token = os.getenv("HF_TOKEN")
    if hf_token:
        requirements["hf_token"] = True
    
    return requirements

def fix_openvoice_app(repo_path):
    """Fix the openvoice_app.py file"""
    app_file = repo_path / "openvoice" / "openvoice_app.py"
    
    if not app_file.exists():
        print(f"  [ERROR] {app_file} not found")
        return False
    
    print(f"  [INFO] Reading {app_file}")
    content = app_file.read_text(encoding='utf-8')
    original_content = content
    
    # Remove info parameter from gr.Audio
    if 'info="Click on the ✎ button to upload your own target speaker audio"' in content:
        content = content.replace(
            '                info="Click on the ✎ button to upload your own target speaker audio",\n',
            ''
        )
        print("  [FIX] Removed info parameter from gr.Audio")
    
    if content != original_content:
        app_file.write_text(content, encoding='utf-8')
        print(f"  [OK] Fixed {app_file}")
        return True
    else:
        print("  [INFO] No fixes needed")
        return False

def commit_and_push(repo_path, commit_message="Fix Gradio compatibility - remove info parameter"):
    """Commit and push changes to GitHub"""
    print(f"\n[3] Committing and pushing changes...")
    
    try:
        # Check if there are changes
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        
        if not result.stdout.strip():
            print("  [INFO] No changes to commit")
            return True
        
        # Add changes
        print("  [INFO] Staging changes...")
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
        
        # Commit
        print(f"  [INFO] Committing: {commit_message}")
        subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=repo_path,
            check=True
        )
        
        # Push
        print("  [INFO] Pushing to GitHub...")
        subprocess.run(["git", "push", "origin", "main"], cwd=repo_path, check=True)
        
        print("  [OK] Changes pushed to GitHub")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] Git operation failed: {e}")
        print(f"  [INFO] Stderr: {e.stderr.decode() if e.stderr else 'N/A'}")
        return False

def create_space_app_py(repo_path):
    """Create app.py at root for Hugging Face Space compatibility"""
    app_file = repo_path / "app.py"
    openvoice_app = repo_path / "openvoice" / "openvoice_app.py"
    
    if app_file.exists():
        print(f"  [INFO] {app_file} already exists")
        return True
    
    if not openvoice_app.exists():
        print(f"  [ERROR] Source file {openvoice_app} not found")
        return False
    
    print(f"  [INFO] Creating {app_file} from {openvoice_app}")
    
    # Read the openvoice_app.py content
    content = openvoice_app.read_text(encoding='utf-8')
    
    # Modify imports to work from root
    content = content.replace(
        "from openvoice import se_extractor",
        "from openvoice.openvoice import se_extractor"
    )
    content = content.replace(
        "from openvoice.api import BaseSpeakerTTS, ToneColorConverter",
        "from openvoice.openvoice.api import BaseSpeakerTTS, ToneColorConverter"
    )
    
    # Write to root app.py
    app_file.write_text(content, encoding='utf-8')
    print(f"  [OK] Created {app_file}")
    return True

def main():
    print("=" * 70)
    print(" Deploy Fixed OpenVoice Fork to Hugging Face")
    print("=" * 70)
    
    # Check requirements
    print("\n[0] Checking requirements...")
    reqs = check_requirements()
    
    if not reqs["git"]:
        print("  [ERROR] Git is not installed")
        print("  Install Git: https://git-scm.com/downloads")
        return
    
    print("  [OK] Git installed")
    
    if not reqs["hf_token"]:
        print("  [WARNING] HF_TOKEN not set")
        print("  Set with: $env:HF_TOKEN='your_token'")
        print("  Continuing with GitHub push only...")
    else:
        print("  [OK] HF_TOKEN found")
    
    # Repository path
    repo_path = Path("openvoice_deploy")
    
    if not repo_path.exists():
        print(f"\n[ERROR] Repository not found at {repo_path}")
        print("  Please clone your fork first:")
        print("  git clone https://github.com/IsaiahDupree/OpenVoice.git openvoice_deploy")
        return
    
    print(f"\n[1] Repository found at {repo_path}")
    
    # Fix the app file
    print(f"\n[2] Fixing Gradio compatibility...")
    fixed = fix_openvoice_app(repo_path)
    
    if not fixed:
        print("  [WARNING] No fixes applied - file might already be fixed")
    
    # Create root app.py for Space compatibility
    print(f"\n[2.5] Creating Space-compatible app.py...")
    create_space_app_py(repo_path)
    
    # Commit and push
    success = commit_and_push(repo_path)
    
    if success:
        print("\n" + "=" * 70)
        print(" Next Steps:")
        print("=" * 70)
        print("\n1. Go to: https://huggingface.co/spaces/theisaiahdupree/OpenVoiceV2")
        print("2. Click 'Settings' tab")
        print("3. Scroll to 'Repository' section")
        print("4. Click 'Connect to GitHub'")
        print("5. Select: IsaiahDupree/OpenVoice")
        print("6. Set branch: main")
        print("7. Set root directory: (leave empty or set to root)")
        print("8. Space will auto-deploy!")
        print("\n" + "=" * 70)
    else:
        print("\n[ERROR] Failed to push changes")
        print("  Please check git status and push manually")

if __name__ == "__main__":
    main()

