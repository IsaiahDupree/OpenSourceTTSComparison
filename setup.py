#!/usr/bin/env python3
"""
Setup script for TTS Comparison Study
"""

import subprocess
import sys
from pathlib import Path

def install_requirements():
    """Install basic requirements."""
    requirements = [
        "numpy>=1.21.0",
        "scipy>=1.7.0", 
        "librosa>=0.9.0",
        "soundfile>=0.10.0",
        "pydub>=0.25.0",
        "matplotlib>=3.5.0",
        "seaborn>=0.11.0",
        "pandas>=1.3.0",
        "torch>=1.11.0",
        "torchaudio>=0.11.0",
        "transformers>=4.20.0",
        "tqdm>=4.64.0",
        "click>=8.0.0",
        "colorama>=0.4.4",
        "tabulate>=0.8.9",
        "requests>=2.28.0",
        "PyYAML>=6.0",
        "psutil>=5.9.0"
    ]
    
    print("Installing basic requirements...")
    for req in requirements:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", req])
            print(f"✅ Installed {req}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {req}")

def main():
    print("🚀 Setting up TTS Comparison Study")
    print("=" * 50)
    
    # Create directories
    dirs = ["models", "data", "results", "audio_samples", "processed"]
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"📁 Created directory: {dir_name}")
    
    # Install requirements
    install_requirements()
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Run: python scripts/install_models.py")
    print("2. Add audio samples to audio_samples/ directory")
    print("3. Run: python tools/audio_processor.py --input audio_samples/")
    print("4. Run: python benchmark/run_all_tests.py")

if __name__ == "__main__":
    main()
