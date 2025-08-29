#!/usr/bin/env python3
"""
Fix Chatterbox environment by properly installing compatible dependencies
"""

import subprocess
import sys
import os

def run_in_env(env_name, command):
    """Run a command in the specified virtual environment"""
    env_python = os.path.join("envs", f"venv_{env_name}", "Scripts", "python.exe")
    env_pip = os.path.join("envs", f"venv_{env_name}", "Scripts", "pip.exe")
    
    if "pip install" in command:
        cmd = command.replace("pip install", f'"{env_pip}" install')
    else:
        cmd = f'"{env_python}" -c "{command}"'
    
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    print(f"Return code: {result.returncode}")
    if result.stdout:
        print(f"STDOUT:\n{result.stdout}")
    if result.stderr:
        print(f"STDERR:\n{result.stderr}")
    
    return result.returncode == 0

def main():
    """Fix Chatterbox environment setup"""
    
    print("Fixing Chatterbox TTS environment...")
    print("=" * 50)
    
    # Step 1: Upgrade pip
    print("\n1. Upgrading pip...")
    if not run_in_env("chatterbox", "pip install --upgrade pip"):
        print("Failed to upgrade pip")
        return False
    
    # Step 2: Install compatible PyTorch (CPU version)
    print("\n2. Installing compatible PyTorch...")
    pytorch_cmd = "pip install torch==1.13.1 torchvision==0.14.1 torchaudio==0.13.1 --index-url https://download.pytorch.org/whl/cpu"
    if not run_in_env("chatterbox", pytorch_cmd):
        print("Failed to install PyTorch")
        return False
    
    # Step 3: Install other dependencies
    print("\n3. Installing other dependencies...")
    deps = [
        "transformers==4.21.3",
        "numpy",
        "soundfile",
        "librosa"
    ]
    
    for dep in deps:
        print(f"Installing {dep}...")
        if not run_in_env("chatterbox", f"pip install {dep}"):
            print(f"Failed to install {dep}")
            return False
    
    # Step 4: Install chatterbox-tts
    print("\n4. Installing chatterbox-tts...")
    if not run_in_env("chatterbox", "pip install chatterbox-tts"):
        print("Failed to install chatterbox-tts")
        return False
    
    # Step 5: Test import
    print("\n5. Testing import...")
    test_code = "import chatterbox; print('Chatterbox imported successfully')"
    if run_in_env("chatterbox", test_code):
        print("✓ Chatterbox environment setup successful!")
        return True
    else:
        print("✗ Chatterbox import test failed")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Chatterbox environment is ready!")
    else:
        print("\n❌ Chatterbox environment setup failed")
    sys.exit(0 if success else 1)
