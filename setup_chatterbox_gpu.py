#!/usr/bin/env python3
"""
Setup ChatterBox TTS with GPU support for RTX 4070 (CUDA 12.8)
"""

import subprocess
import sys
import os

def run_command(cmd, description=""):
    """Run a command and return success status"""
    if description:
        print(f"🔧 {description}")
    print(f"Running: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed with exit code {e.returncode}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def check_gpu():
    """Check GPU availability"""
    print("🎮 Checking GPU availability...")
    try:
        result = subprocess.run("nvidia-smi", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ NVIDIA GPU detected")
            return True
        else:
            print("❌ NVIDIA GPU not found")
            return False
    except:
        print("❌ nvidia-smi not found")
        return False

def main():
    """Setup ChatterBox with GPU support"""
    print("🚀 Setting up ChatterBox TTS with GPU support")
    print("=" * 60)
    
    # Check GPU
    if not check_gpu():
        print("⚠️ No GPU detected, but continuing with installation...")
    
    # Step 1: Uninstall existing PyTorch (CPU version)
    print("\n1️⃣ Removing existing PyTorch installation...")
    uninstall_cmd = f"{sys.executable} -m pip uninstall torch torchvision torchaudio -y"
    run_command(uninstall_cmd, "Uninstalling existing PyTorch")
    
    # Step 2: Install CUDA-enabled PyTorch
    print("\n2️⃣ Installing CUDA-enabled PyTorch...")
    # Using PyTorch with CUDA 12.1 support (compatible with CUDA 12.8)
    pytorch_cmd = f"{sys.executable} -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121"
    if not run_command(pytorch_cmd, "Installing PyTorch with CUDA support"):
        print("❌ Failed to install CUDA PyTorch")
        return False
    
    # Step 3: Install audio processing libraries
    print("\n3️⃣ Installing audio processing libraries...")
    audio_deps = [
        "soundfile",
        "librosa",
        "numpy",
        "scipy"
    ]
    
    for dep in audio_deps:
        cmd = f"{sys.executable} -m pip install {dep}"
        if not run_command(cmd, f"Installing {dep}"):
            print(f"⚠️ Failed to install {dep}, continuing...")
    
    # Step 4: Install transformers
    print("\n4️⃣ Installing transformers...")
    transformers_cmd = f"{sys.executable} -m pip install transformers"
    run_command(transformers_cmd, "Installing transformers")
    
    # Step 5: Install ChatterBox TTS
    print("\n5️⃣ Installing ChatterBox TTS...")
    chatterbox_cmd = f"{sys.executable} -m pip install chatterbox-tts"
    if not run_command(chatterbox_cmd, "Installing ChatterBox TTS"):
        print("❌ Failed to install ChatterBox TTS")
        return False
    
    # Step 6: Test CUDA availability
    print("\n6️⃣ Testing CUDA availability...")
    test_cmd = f'{sys.executable} -c "import torch; print(f\'CUDA available: {{torch.cuda.is_available()}}\'); print(f\'Device count: {{torch.cuda.device_count()}}\'); print(f\'Current device: {{torch.cuda.current_device() if torch.cuda.is_available() else \'N/A\'}}\'); print(f\'Device name: {{torch.cuda.get_device_name(0) if torch.cuda.is_available() else \'N/A\'}}\');"'
    run_command(test_cmd, "Testing CUDA functionality")
    
    # Step 7: Test ChatterBox import
    print("\n7️⃣ Testing ChatterBox import...")
    import_test = f'{sys.executable} -c "import chatterbox; print(\'✅ ChatterBox imported successfully\')"'
    if run_command(import_test, "Testing ChatterBox import"):
        print("\n🎉 ChatterBox GPU setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Test ChatterBox functionality with: python test_chatterbox.py")
        print("2. Prepare voice training data")
        print("3. Train your custom voice model with GPU acceleration")
        return True
    else:
        print("❌ ChatterBox import failed")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)
    else:
        print("\n✅ Setup completed successfully!")
        sys.exit(0)
