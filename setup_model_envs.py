#!/usr/bin/env python3
"""
Setup isolated environments for TTS models with proper dependency management
"""

import subprocess
import sys
import os
from pathlib import Path
import json

class ModelEnvironmentSetup:
    """Setup isolated environments for each TTS model."""
    
    def __init__(self):
        self.base_dir = Path("envs")
        self.base_dir.mkdir(exist_ok=True)
        
    def create_venv(self, model_name: str) -> bool:
        """Create virtual environment for a model."""
        venv_path = self.base_dir / f"venv_{model_name}"
        
        if venv_path.exists():
            print(f"✅ Environment already exists: {venv_path}")
            return True
            
        try:
            print(f"Creating environment for {model_name}...")
            subprocess.run([sys.executable, "-m", "venv", str(venv_path)], 
                         check=True, timeout=300)
            print(f"✅ Created environment: {venv_path}")
            return True
        except subprocess.TimeoutExpired:
            print(f"⏰ Timeout creating {model_name} environment")
            return False
        except Exception as e:
            print(f"❌ Failed to create {model_name} environment: {e}")
            return False
    
    def install_in_venv(self, model_name: str, packages: list) -> bool:
        """Install packages in the model's virtual environment."""
        venv_path = self.base_dir / f"venv_{model_name}"
        
        if os.name == 'nt':  # Windows
            pip_exe = venv_path / "Scripts" / "pip.exe"
        else:  # Unix-like
            pip_exe = venv_path / "bin" / "pip"
            
        if not pip_exe.exists():
            print(f"❌ pip not found in {model_name} environment")
            return False
        
        try:
            # Upgrade pip first
            subprocess.run([str(pip_exe), "install", "--upgrade", "pip"], 
                         check=True, timeout=300)
            
            # Install packages
            for package in packages:
                print(f"Installing {package} in {model_name} environment...")
                subprocess.run([str(pip_exe), "install", package], 
                             check=True, timeout=600)
                print(f"✅ Installed {package}")
            
            return True
            
        except subprocess.TimeoutExpired:
            print(f"⏰ Timeout installing packages in {model_name}")
            return False
        except Exception as e:
            print(f"❌ Failed to install packages in {model_name}: {e}")
            return False
    
    def setup_chatterbox(self) -> bool:
        """Setup Chatterbox with compatible dependencies."""
        print("\n🎤 Setting up Chatterbox TTS")
        print("=" * 40)
        
        if not self.create_venv("chatterbox"):
            return False
        
        # Install compatible torch versions first
        torch_packages = [
            "torch==1.13.1",
            "torchvision==0.14.1", 
            "torchaudio==0.13.1"
        ]
        
        other_packages = [
            "transformers==4.21.3",  # Compatible version
            "numpy>=1.21.0",
            "soundfile>=0.10.0",
            "chatterbox-tts"
        ]
        
        # Install torch first
        if not self.install_in_venv("chatterbox", torch_packages):
            return False
            
        # Then install other packages
        if not self.install_in_venv("chatterbox", other_packages):
            return False
            
        return True
    
    def setup_coqui_tts(self) -> bool:
        """Setup Coqui TTS."""
        print("\n🎵 Setting up Coqui TTS")
        print("=" * 40)
        
        if not self.create_venv("coqui_tts"):
            return False
        
        packages = [
            "torch>=1.11.0",
            "torchaudio>=0.11.0",
            "numpy>=1.21.0",
            "librosa>=0.9.0",
            "soundfile>=0.10.0",
            "TTS"
        ]
        
        return self.install_in_venv("coqui_tts", packages)
    
    def test_model_in_env(self, model_name: str, test_script: str) -> bool:
        """Test a model in its isolated environment."""
        venv_path = self.base_dir / f"venv_{model_name}"
        
        if os.name == 'nt':  # Windows
            python_exe = venv_path / "Scripts" / "python.exe"
        else:  # Unix-like
            python_exe = venv_path / "bin" / "python"
            
        if not python_exe.exists():
            print(f"❌ Python not found in {model_name} environment")
            return False
        
        try:
            # Write test script to temp file
            test_file = f"test_{model_name}_temp.py"
            with open(test_file, 'w') as f:
                f.write(test_script)
            
            # Run test
            result = subprocess.run([str(python_exe), test_file], 
                                  capture_output=True, text=True, timeout=60)
            
            # Clean up
            os.unlink(test_file)
            
            if result.returncode == 0:
                print(f"✅ {model_name} test passed")
                return True
            else:
                print(f"❌ {model_name} test failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing {model_name}: {e}")
            return False
    
    def setup_all_models(self):
        """Setup all TTS models."""
        results = {}
        
        # Setup Chatterbox
        results["chatterbox"] = self.setup_chatterbox()
        
        # Setup Coqui TTS
        results["coqui_tts"] = self.setup_coqui_tts()
        
        # Save results
        with open(self.base_dir / "setup_results.json", 'w') as f:
            json.dump(results, f, indent=2)
        
        # Print summary
        print(f"\n📊 Setup Summary:")
        for model, success in results.items():
            status = "✅" if success else "❌"
            print(f"{status} {model}")
        
        return results

def main():
    setup = ModelEnvironmentSetup()
    results = setup.setup_all_models()
    
    # Test models if setup was successful
    if results.get("chatterbox", False):
        print(f"\n🧪 Testing Chatterbox...")
        chatterbox_test = """
try:
    import chatterbox
    print("Chatterbox imported successfully")
except Exception as e:
    print(f"Chatterbox import failed: {e}")
"""
        setup.test_model_in_env("chatterbox", chatterbox_test)
    
    if results.get("coqui_tts", False):
        print(f"\n🧪 Testing Coqui TTS...")
        coqui_test = """
try:
    from TTS.api import TTS
    print("Coqui TTS imported successfully")
except Exception as e:
    print(f"Coqui TTS import failed: {e}")
"""
        setup.test_model_in_env("coqui_tts", coqui_test)

if __name__ == "__main__":
    main()
