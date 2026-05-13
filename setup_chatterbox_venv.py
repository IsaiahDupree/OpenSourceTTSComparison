#!/usr/bin/env python3
"""
Create virtual environment and install ChatterBox TTS with GPU support
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description="", cwd=None):
    """Run a command and return success status"""
    if description:
        print(f"🔧 {description}")
    print(f"Running: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, cwd=cwd, capture_output=True, text=True)
        if result.stdout.strip():
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed with exit code {e.returncode}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        return False

def main():
    """Setup ChatterBox in virtual environment"""
    print("🚀 Setting up ChatterBox TTS in Virtual Environment")
    print("=" * 60)
    
    project_dir = Path.cwd()
    venv_dir = project_dir / "venv_chatterbox"
    
    # Step 1: Create virtual environment
    print("\n1️⃣ Creating virtual environment...")
    if venv_dir.exists():
        print(f"⚠️ Virtual environment already exists at {venv_dir}")
        response = input("Remove existing environment? (y/n): ").lower()
        if response == 'y':
            import shutil
            shutil.rmtree(venv_dir)
            print("✅ Removed existing environment")
        else:
            print("Using existing environment...")
    
    if not venv_dir.exists():
        create_cmd = f"{sys.executable} -m venv venv_chatterbox"
        if not run_command(create_cmd, "Creating virtual environment"):
            return False
    
    # Define paths for the virtual environment
    if os.name == 'nt':  # Windows
        venv_python = venv_dir / "Scripts" / "python.exe"
        venv_pip = venv_dir / "Scripts" / "pip.exe"
        activate_script = venv_dir / "Scripts" / "activate.bat"
    else:  # Unix/Linux/Mac
        venv_python = venv_dir / "bin" / "python"
        venv_pip = venv_dir / "bin" / "pip"
        activate_script = venv_dir / "bin" / "activate"
    
    # Step 2: Upgrade pip
    print("\n2️⃣ Upgrading pip...")
    upgrade_cmd = f'"{venv_pip}" install --upgrade pip'
    run_command(upgrade_cmd, "Upgrading pip")
    
    # Step 3: Install CUDA-enabled PyTorch
    print("\n3️⃣ Installing PyTorch with CUDA support...")
    pytorch_cmd = f'"{venv_pip}" install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121'
    if not run_command(pytorch_cmd, "Installing PyTorch with CUDA"):
        print("❌ Failed to install PyTorch")
        return False
    
    # Step 4: Install audio processing libraries
    print("\n4️⃣ Installing audio processing libraries...")
    audio_deps = [
        "soundfile",
        "librosa",
        "numpy",
        "scipy",
        "matplotlib",
        "tqdm"
    ]
    
    for dep in audio_deps:
        cmd = f'"{venv_pip}" install {dep}'
        run_command(cmd, f"Installing {dep}")
    
    # Step 5: Install ML libraries
    print("\n5️⃣ Installing ML libraries...")
    ml_deps = [
        "transformers",
        "datasets",
        "accelerate",
        "tensorboard"
    ]
    
    for dep in ml_deps:
        cmd = f'"{venv_pip}" install {dep}'
        run_command(cmd, f"Installing {dep}")
    
    # Step 6: Install ChatterBox TTS
    print("\n6️⃣ Installing ChatterBox TTS...")
    chatterbox_cmd = f'"{venv_pip}" install chatterbox-tts'
    if not run_command(chatterbox_cmd, "Installing ChatterBox TTS"):
        print("❌ Failed to install ChatterBox TTS")
        return False
    
    # Step 7: Test CUDA availability
    print("\n7️⃣ Testing CUDA availability...")
    test_cmd = f'"{venv_python}" -c "import torch; print(f\'CUDA available: {{torch.cuda.is_available()}}\'); print(f\'Device count: {{torch.cuda.device_count()}}\'); print(f\'Device name: {{torch.cuda.get_device_name(0) if torch.cuda.is_available() else \'N/A\'}}\')"'
    run_command(test_cmd, "Testing CUDA functionality")
    
    # Step 8: Test ChatterBox import
    print("\n8️⃣ Testing ChatterBox import...")
    import_test = f'"{venv_python}" -c "import chatterbox; print(\'✅ ChatterBox imported successfully\')"'
    if run_command(import_test, "Testing ChatterBox import"):
        print("\n🎉 ChatterBox virtual environment setup completed successfully!")
        
        # Create activation script
        print("\n📋 Environment setup complete!")
        print(f"📁 Virtual environment location: {venv_dir}")
        print("\n🔧 To activate the environment:")
        if os.name == 'nt':
            print(f"   {activate_script}")
        else:
            print(f"   source {activate_script}")
        
        print("\n📝 Next steps:")
        print("1. Activate the environment")
        print("2. Test ChatterBox with: python test_chatterbox.py")
        print("3. Prepare voice training data")
        print("4. Train your custom voice model")
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
        print("\n✅ Virtual environment setup completed successfully!")
        sys.exit(0)
