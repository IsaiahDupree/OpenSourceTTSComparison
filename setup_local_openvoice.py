#!/usr/bin/env python3
"""
Setup script for running OpenVoice locally
"""

import os
import sys
import subprocess
from pathlib import Path
import urllib.request
import zipfile
import shutil

def check_python_version():
    """Check if Python version is compatible"""
    print("[1] Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"  [ERROR] Python 3.8+ required. Found: {version.major}.{version.minor}")
        return False
    print(f"  [OK] Python {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("\n[2] Installing Python dependencies...")
    requirements_file = Path("openvoice_deploy/requirements.txt")
    if not requirements_file.exists():
        print(f"  [ERROR] {requirements_file} not found")
        return False
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
        print("  [OK] Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] Failed to install dependencies: {e}")
        return False

def download_checkpoints():
    """Download OpenVoice checkpoints"""
    print("\n[3] Downloading checkpoints...")
    checkpoints_dir = Path("openvoice_deploy/checkpoints")
    
    # Check if checkpoints already exist
    en_checkpoint = checkpoints_dir / "base_speakers/EN/checkpoint.pth"
    if en_checkpoint.exists():
        print("  [INFO] Checkpoints already exist, skipping download")
        return True
    
    checkpoints_url = "https://myshell-public-repo-host.s3.amazonaws.com/openvoice/checkpoints_1226.zip"
    zip_path = Path("checkpoints_1226.zip")
    
    print(f"  Downloading from: {checkpoints_url}")
    print(f"  This may take a few minutes (400+ MB)...")
    
    try:
        urllib.request.urlretrieve(checkpoints_url, zip_path)
        print(f"  [OK] Downloaded {zip_path.name}")
        
        # Extract
        print(f"  Extracting to {checkpoints_dir}...")
        checkpoints_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(checkpoints_dir.parent)
        
        # Clean up
        zip_path.unlink()
        print("  [OK] Checkpoints extracted")
        return True
    except Exception as e:
        print(f"  [ERROR] Failed to download checkpoints: {e}")
        return False

def create_run_script():
    """Create a run script"""
    print("\n[4] Creating run script...")
    
    run_script = Path("run_openvoice_local.py")
    script_content = '''#!/usr/bin/env python3
"""
Run OpenVoice locally
"""

import sys
import os
from pathlib import Path

# Add openvoice_deploy to path
sys.path.insert(0, str(Path(__file__).parent / "openvoice_deploy"))

# Change to openvoice_deploy directory
os.chdir(Path(__file__).parent / "openvoice_deploy")

# Import and run
from app import demo

if __name__ == "__main__":
    print("=" * 70)
    print(" Starting OpenVoice locally...")
    print("=" * 70)
    print("\\nOpen your browser to: http://localhost:7860")
    print("Press Ctrl+C to stop\\n")
    
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
'''
    
    with open(run_script, 'w') as f:
        f.write(script_content)
    
    # Make executable on Unix
    if os.name != 'nt':
        os.chmod(run_script, 0o755)
    
    print(f"  [OK] Created {run_script}")
    return True

def main():
    print("=" * 70)
    print(" OpenVoice Local Setup")
    print("=" * 70)
    
    if not check_python_version():
        return False
    
    if not install_dependencies():
        print("\n[WARNING] Some dependencies may have failed. Continue anyway?")
        response = input("  (y/n): ").lower()
        if response != 'y':
            return False
    
    if not download_checkpoints():
        print("\n[WARNING] Checkpoint download failed. You can download manually later.")
        print("  URL: https://myshell-public-repo-host.s3.amazonaws.com/openvoice/checkpoints_1226.zip")
        print("  Extract to: openvoice_deploy/checkpoints/")
    
    if not create_run_script():
        return False
    
    print("\n" + "=" * 70)
    print(" Setup Complete!")
    print("=" * 70)
    print("\nTo run OpenVoice locally:")
    print("  python run_openvoice_local.py")
    print("\nOr run directly:")
    print("  cd openvoice_deploy")
    print("  python app.py")
    print("\nThe app will be available at: http://localhost:7860")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
