#!/usr/bin/env python3
"""
Complete local setup for OpenVoice - checks Python version and installs all dependencies
"""

import os
import sys
import subprocess
from pathlib import Path
import importlib

def check_python_version():
    """Check if Python version is compatible"""
    print("=" * 70)
    print(" Python Version Check")
    print("=" * 70)
    
    version = sys.version_info
    print(f"Current Python: {version.major}.{version.minor}.{version.micro}")
    print(f"Python executable: {sys.executable}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"\n[ERROR] Python 3.8+ required. Found: {version.major}.{version.minor}")
        print("\nPlease install Python 3.8 or higher from: https://www.python.org/downloads/")
        return False
    
    print(f"[OK] Python version is compatible")
    return True

def check_and_install_package(package_name, import_name=None, version_check=None):
    """Check if package is installed, install if missing"""
    if import_name is None:
        import_name = package_name
    
    try:
        mod = importlib.import_module(import_name)
        if version_check:
            # Try to get version
            try:
                ver = mod.__version__
                print(f"  [OK] {package_name} (version {ver})")
            except:
                print(f"  [OK] {package_name} (installed)")
        else:
            print(f"  [OK] {package_name}")
        return True
    except ImportError:
        print(f"  [MISSING] {package_name} - installing...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package_name
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"  [OK] {package_name} installed")
            return True
        except subprocess.CalledProcessError:
            print(f"  [ERROR] Failed to install {package_name}")
            return False

def install_dependencies():
    """Install all required dependencies"""
    print("\n" + "=" * 70)
    print(" Installing Dependencies")
    print("=" * 70)
    
    requirements_file = Path("openvoice_deploy/requirements.txt")
    if not requirements_file.exists():
        print(f"[ERROR] {requirements_file} not found")
        return False
    
    # Read requirements
    with open(requirements_file, 'r') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    print(f"\n[1] Installing from requirements.txt...")
    print(f"Found {len(requirements)} packages")
    
    # First, upgrade pip
    print("\n[2] Upgrading pip...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip"
        ], stdout=subprocess.DEVNULL)
        print("  [OK] pip upgraded")
    except:
        print("  [WARNING] Could not upgrade pip, continuing...")
    
    # Install core dependencies first (torch, numpy, etc.)
    print("\n[3] Installing core dependencies...")
    core_packages = [
        ("torch", "torch", ">=2.0.0"),
        ("torchaudio", "torchaudio", ">=2.0.0"),
        ("numpy", "numpy", "==1.22.0"),
        ("gradio", "gradio", "==3.48.0"),
    ]
    
    for package, import_name, version in core_packages:
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", f"{package}{version}"
            ])
            print(f"  [OK] {package}")
        except:
            print(f"  [WARNING] {package} installation had issues")
    
    # Install other dependencies
    print("\n[4] Installing other dependencies...")
    try:
        # Skip faster-whisper and whisper-timestamped (optional)
        filtered_requirements = []
        for req in requirements:
            if "faster-whisper" not in req and "whisper-timestamped" not in req:
                filtered_requirements.append(req)
        
        # Write temporary requirements file
        temp_req = Path("temp_requirements.txt")
        with open(temp_req, 'w') as f:
            f.write('\n'.join(filtered_requirements))
        
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(temp_req)
        ])
        
        temp_req.unlink()
        print("  [OK] Dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"  [WARNING] Some dependencies may have failed: {e}")
        print("  Continuing with verification...")
    
    return True

def verify_installations():
    """Verify all critical packages are installed"""
    print("\n" + "=" * 70)
    print(" Verifying Installations")
    print("=" * 70)
    
    critical_packages = [
        ("torch", "torch"),
        ("torchaudio", "torchaudio"),
        ("numpy", "numpy"),
        ("gradio", "gradio"),
        ("librosa", "librosa"),
        ("pydub", "pydub"),
        ("langid", "langid"),
    ]
    
    optional_packages = [
        ("faster-whisper", "faster_whisper"),
        ("whisper-timestamped", "whisper_timestamped"),
    ]
    
    print("\n[1] Critical packages:")
    all_ok = True
    for package, import_name in critical_packages:
        try:
            mod = importlib.import_module(import_name)
            try:
                ver = mod.__version__
                print(f"  [OK] {package} (v{ver})")
            except:
                print(f"  [OK] {package}")
        except ImportError:
            print(f"  [MISSING] {package}")
            all_ok = False
    
    print("\n[2] Optional packages:")
    for package, import_name in optional_packages:
        try:
            mod = importlib.import_module(import_name)
            print(f"  [OK] {package} (optional, installed)")
        except ImportError:
            print(f"  [SKIP] {package} (optional, not installed - will use VAD method)")
    
    return all_ok

def check_checkpoints():
    """Check if checkpoints exist"""
    print("\n" + "=" * 70)
    print(" Checking Checkpoints")
    print("=" * 70)
    
    checkpoints_dir = Path("openvoice_deploy/checkpoints")
    required_files = [
        "base_speakers/EN/checkpoint.pth",
        "base_speakers/EN/config.json",
        "base_speakers/EN/en_default_se.pth",
        "base_speakers/EN/en_style_se.pth",
        "base_speakers/ZH/checkpoint.pth",
        "base_speakers/ZH/config.json",
        "base_speakers/ZH/zh_default_se.pth",
        "converter/checkpoint.pth",
        "converter/config.json",
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = checkpoints_dir / file_path
        if full_path.exists():
            size = full_path.stat().st_size / (1024 * 1024)  # MB
            print(f"  [OK] {file_path} ({size:.1f} MB)")
        else:
            print(f"  [MISSING] {file_path}")
            all_exist = False
    
    if not all_exist:
        print("\n[WARNING] Some checkpoints are missing!")
        print("Download from: https://myshell-public-repo-host.s3.amazonaws.com/openvoice/checkpoints_1226.zip")
        print("Extract to: openvoice_deploy/checkpoints/")
    
    return all_exist

def main():
    print("=" * 70)
    print(" OpenVoice Complete Local Setup")
    print("=" * 70)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install dependencies
    if not install_dependencies():
        print("\n[WARNING] Dependency installation had issues")
        response = input("Continue with verification? (y/n): ").lower()
        if response != 'y':
            return False
    
    # Verify installations
    if not verify_installations():
        print("\n[ERROR] Some critical packages are missing!")
        print("Please install them manually:")
        print("  pip install torch torchaudio numpy gradio librosa pydub langid")
        return False
    
    # Check checkpoints
    checkpoints_ok = check_checkpoints()
    
    print("\n" + "=" * 70)
    print(" Setup Summary")
    print("=" * 70)
    print("\n✅ Python version: OK")
    print("✅ Dependencies: Installed")
    if checkpoints_ok:
        print("✅ Checkpoints: Found")
    else:
        print("⚠️  Checkpoints: Some missing (download if needed)")
    
    print("\n" + "=" * 70)
    print(" Ready to Run!")
    print("=" * 70)
    print("\nTo start OpenVoice:")
    print("  python run_openvoice_local.py")
    print("\nOr:")
    print("  cd openvoice_deploy")
    print("  python app.py")
    print("\nThen open: http://localhost:7860")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

