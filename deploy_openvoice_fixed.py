#!/usr/bin/env python3
"""
Agentic Deployment of Fixed OpenVoice to Hugging Face
======================================================
Fork, fix, and deploy OpenVoiceV2 with Gradio compatibility fixes.
"""

import os
import sys
import subprocess
import re
from pathlib import Path
import shutil

def check_git_installed():
    """Check if git is installed"""
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        return True
    except:
        return False

def check_huggingface_hub():
    """Check if huggingface_hub is installed"""
    try:
        import huggingface_hub
        return True
    except ImportError:
        return False

def fix_app_py(app_py_path):
    """Fix Gradio compatibility issues in app.py"""
    print(f"\n[2] Fixing app.py: {app_py_path}")
    
    if not app_py_path.exists():
        print(f"  [ERROR] app.py not found at {app_py_path}")
        return False
    
    # Read the file
    with open(app_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    fixes_applied = []
    
    # Fix 1: Remove 'info' parameter from gr.Audio
    # Pattern: gr.Audio(..., info="...", ...)
    audio_pattern = r'gr\.Audio\s*\(([^)]*info\s*=\s*["\'][^"\']*["\'][^)]*)\)'
    
    def remove_info_param(match):
        params = match.group(1)
        # Remove info parameter and its value
        params = re.sub(r',\s*info\s*=\s*["\'][^"\']*["\']', '', params)
        params = re.sub(r'info\s*=\s*["\'][^"\']*["\']\s*,?\s*', '', params)
        fixes_applied.append("Removed 'info' parameter from gr.Audio")
        return f'gr.Audio({params})'
    
    content = re.sub(audio_pattern, remove_info_param, content)
    
    # Fix 2: Remove max_choices when multiselect=False
    # Pattern: max_choices=X with multiselect=False
    dropdown_pattern = r'(gr\.Dropdown\s*\([^)]*?)(max_choices\s*=\s*\d+\s*,?\s*)([^)]*?multiselect\s*=\s*False[^)]*?\))'
    
    def remove_max_choices(match):
        before = match.group(1)
        max_choices = match.group(2)
        after = match.group(3)
        fixes_applied.append("Removed 'max_choices' from Dropdown with multiselect=False")
        return before + after
    
    content = re.sub(dropdown_pattern, remove_max_choices, content, flags=re.DOTALL)
    
    # More specific fix for Audio components
    # Find all gr.Audio calls and remove info parameter
    lines = content.split('\n')
    fixed_lines = []
    in_audio = False
    audio_indent = 0
    
    for i, line in enumerate(lines):
        if 'gr.Audio(' in line:
            in_audio = True
            audio_indent = len(line) - len(line.lstrip())
            # Check if info is on same line
            if 'info=' in line:
                line = re.sub(r',?\s*info\s*=\s*["\'][^"\']*["\']', '', line)
                fixes_applied.append(f"Removed 'info' from gr.Audio at line {i+1}")
        elif in_audio:
            # Check if we're still in the Audio call
            current_indent = len(line) - len(line.lstrip())
            if line.strip() and current_indent <= audio_indent and ')' in line:
                in_audio = False
            elif 'info=' in line:
                # Remove this line if it's just the info parameter
                if re.match(r'^\s*info\s*=\s*["\'][^"\']*["\']\s*,?\s*$', line):
                    fixes_applied.append(f"Removed 'info' line at {i+1}")
                    continue
        
        fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    # Write fixed content
    if content != original_content:
        with open(app_py_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  [OK] Applied {len(fixes_applied)} fixes:")
        for fix in fixes_applied:
            print(f"      - {fix}")
        return True
    else:
        print("  [INFO] No fixes needed (or pattern didn't match)")
        return False

def setup_repo(repo_dir, fork_url=None):
    """Setup the repository"""
    print(f"\n[1] Setting up repository in: {repo_dir}")
    
    repo_path = Path(repo_dir)
    
    # Clone or update
    if repo_path.exists() and (repo_path / ".git").exists():
        print("  [INFO] Repository exists, pulling latest...")
        subprocess.run(["git", "pull"], cwd=repo_path, check=False)
    else:
        if repo_path.exists():
            shutil.rmtree(repo_path)
        
        if fork_url:
            print(f"  [INFO] Cloning from fork: {fork_url}")
            subprocess.run(["git", "clone", fork_url, str(repo_path)], check=True)
        else:
            print("  [INFO] Cloning from original: https://github.com/myshell-ai/OpenVoice.git")
            subprocess.run(["git", "clone", "https://github.com/myshell-ai/OpenVoice.git", str(repo_path)], check=True)
    
    return repo_path

def find_app_py(repo_path):
    """Find app.py in the repository"""
    # Check common locations
    possible_locations = [
        repo_path / "app.py",
        repo_path / "openvoice" / "app.py",
        repo_path / "spaces" / "OpenVoiceV2" / "app.py",
    ]
    
    # Also search recursively
    for app_file in repo_path.rglob("app.py"):
        if "OpenVoiceV2" in str(app_file) or "space" in str(app_file).lower():
            return app_file
    
    # Return first found
    for loc in possible_locations:
        if loc.exists():
            return loc
    
    return None

def commit_and_push(repo_path, commit_message="Fix Gradio compatibility - remove info parameter"):
    """Commit and push changes"""
    print(f"\n[3] Committing changes...")
    
    try:
        # Add changes
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
        
        # Commit
        subprocess.run(["git", "commit", "-m", commit_message], cwd=repo_path, check=True)
        print("  [OK] Changes committed")
        
        # Push (if remote is set)
        try:
            subprocess.run(["git", "push"], cwd=repo_path, check=True)
            print("  [OK] Changes pushed to remote")
            return True
        except subprocess.CalledProcessError:
            print("  [INFO] Could not push (no remote or not authenticated)")
            print("  [INFO] You can push manually later")
            return False
    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] Git operation failed: {e}")
        return False

def deploy_to_huggingface(repo_path, space_id, hf_token):
    """Deploy to Hugging Face Space using huggingface_hub"""
    print(f"\n[4] Deploying to Hugging Face Space: {space_id}")
    
    try:
        from huggingface_hub import HfApi, Repository
        
        api = HfApi(token=hf_token)
        
        # Check if space exists
        try:
            api.space_info(space_id)
            print(f"  [OK] Space exists: {space_id}")
        except:
            print(f"  [INFO] Creating new Space: {space_id}")
            api.create_repo(
                repo_id=space_id,
                repo_type="space",
                space_sdk="gradio",
                exist_ok=True
            )
        
        # Push files to Space
        print("  [INFO] Uploading files to Space...")
        
        # Get all files to upload
        files_to_upload = []
        for file_path in repo_path.rglob("*"):
            if file_path.is_file():
                # Skip git files
                if ".git" in str(file_path):
                    continue
                # Skip __pycache__
                if "__pycache__" in str(file_path):
                    continue
                files_to_upload.append(file_path)
        
        # Upload files
        for file_path in files_to_upload[:10]:  # Limit for now
            rel_path = file_path.relative_to(repo_path)
            print(f"    Uploading: {rel_path}")
            api.upload_file(
                path_or_fileobj=str(file_path),
                path_in_repo=str(rel_path),
                repo_id=space_id,
                repo_type="space"
            )
        
        print("  [OK] Files uploaded")
        print(f"  [SUCCESS] Space deployed: https://huggingface.co/spaces/{space_id}")
        return True
        
    except ImportError:
        print("  [ERROR] huggingface_hub not installed")
        print("  Install with: pip install huggingface_hub")
        return False
    except Exception as e:
        print(f"  [ERROR] Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 70)
    print(" Agentic OpenVoice Deployment to Hugging Face")
    print("=" * 70)
    
    # Configuration
    repo_dir = "openvoice_fork"
    space_id = "theisaiahdupree/OpenVoiceV2"  # Your Space ID
    hf_token = os.getenv("HF_TOKEN", __import__('os').environ['HF_TOKEN'])
    fork_url = None  # Set if you've already forked: "https://github.com/yourusername/OpenVoice.git"
    
    # Checks
    print("\n[0] Pre-flight checks...")
    
    if not check_git_installed():
        print("  [ERROR] Git is not installed")
        print("  Install Git: https://git-scm.com/downloads")
        return
    
    print("  [OK] Git installed")
    
    if not hf_token:
        print("  [ERROR] HF_TOKEN not set")
        print("  Set with: $env:HF_TOKEN='your_token'")
        return
    
    print("  [OK] HF_TOKEN found")
    
    # Setup repository
    repo_path = setup_repo(repo_dir, fork_url)
    
    # Find and fix app.py
    app_py = find_app_py(repo_path)
    if not app_py:
        print("\n[ERROR] Could not find app.py in repository")
        print("  Searched in:")
        for loc in [repo_path / "app.py", repo_path / "openvoice" / "app.py"]:
            print(f"    - {loc}")
        print("\n  Please check the repository structure")
        return
    
    print(f"  [OK] Found app.py at: {app_py}")
    
    # Fix the file
    fixed = fix_app_py(app_py)
    
    if not fixed:
        print("  [WARNING] No fixes applied - file might already be fixed")
    
    # Commit changes
    commit_and_push(repo_path)
    
    # Deploy to Hugging Face
    if check_huggingface_hub():
        deploy_to_huggingface(repo_path, space_id, hf_token)
    else:
        print("\n[INFO] huggingface_hub not installed")
        print("  Install with: pip install huggingface_hub")
        print("  Then run this script again, or deploy manually")
    
    print("\n" + "=" * 70)
    print(" Deployment process complete!")
    print("=" * 70)
    print(f"\nNext steps:")
    print(f"1. Check your Space: https://huggingface.co/spaces/{space_id}")
    print(f"2. Wait for deployment to complete (1-2 minutes)")
    print(f"3. Test the Space in the UI")
    print(f"4. Use with pub/sub system!")

if __name__ == "__main__":
    main()

