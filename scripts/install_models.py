#!/usr/bin/env python3
"""
Model Installation and Setup Script for TTS Comparison Study

This script handles the installation and configuration of all 6 TTS models
with proper error handling and dependency management.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
import argparse
import logging
from typing import Dict, List, Tuple
import json

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ModelInstaller:
    """Handles installation of TTS models."""
    
    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        self.installation_log = []
        
    def run_command(self, cmd: List[str], cwd: str = None) -> Tuple[bool, str]:
        """Run shell command and return success status and output."""
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=cwd,
                check=False
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Command succeeded: {' '.join(cmd)}")
                return True, result.stdout
            else:
                logger.error(f"❌ Command failed: {' '.join(cmd)}")
                logger.error(f"Error output: {result.stderr}")
                return False, result.stderr
                
        except Exception as e:
            logger.error(f"❌ Exception running command {' '.join(cmd)}: {e}")
            return False, str(e)
    
    def install_chatterbox(self) -> bool:
        """Install Chatterbox TTS."""
        logger.info("Installing Chatterbox TTS...")
        
        # Simple pip install
        success, output = self.run_command([sys.executable, "-m", "pip", "install", "chatterbox-tts"])
        
        if success:
            # Test import
            try:
                import chatterbox
                logger.info("✅ Chatterbox installation verified")
                self.installation_log.append({"model": "chatterbox", "status": "success", "method": "pip"})
                return True
            except ImportError as e:
                logger.error(f"❌ Chatterbox import failed: {e}")
                self.installation_log.append({"model": "chatterbox", "status": "failed", "error": str(e)})
                return False
        else:
            self.installation_log.append({"model": "chatterbox", "status": "failed", "error": output})
            return False
    
    def install_openvoice(self) -> bool:
        """Install OpenVoice."""
        logger.info("Installing OpenVoice...")
        
        repo_dir = self.models_dir / "OpenVoice"
        
        # Clone repository
        if not repo_dir.exists():
            success, output = self.run_command([
                "git", "clone", "https://github.com/myshell-ai/OpenVoice.git", str(repo_dir)
            ])
            if not success:
                self.installation_log.append({"model": "openvoice", "status": "failed", "error": "git clone failed"})
                return False
        
        # Install dependencies
        success, output = self.run_command([
            sys.executable, "-m", "pip", "install", "-e", "."
        ], cwd=str(repo_dir))
        
        if success:
            # Install additional requirements if they exist
            requirements_file = repo_dir / "requirements.txt"
            if requirements_file.exists():
                self.run_command([
                    sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
                ], cwd=str(repo_dir))
            
            logger.info("✅ OpenVoice installation completed")
            self.installation_log.append({"model": "openvoice", "status": "success", "method": "git+pip"})
            return True
        else:
            self.installation_log.append({"model": "openvoice", "status": "failed", "error": output})
            return False
    
    def install_fish_speech(self) -> bool:
        """Install Fish-Speech."""
        logger.info("Installing Fish-Speech...")
        
        repo_dir = self.models_dir / "fish-speech"
        
        # Clone repository
        if not repo_dir.exists():
            success, output = self.run_command([
                "git", "clone", "https://github.com/fishaudio/fish-speech.git", str(repo_dir)
            ])
            if not success:
                self.installation_log.append({"model": "fish-speech", "status": "failed", "error": "git clone failed"})
                return False
        
        # Install with stable extras
        success, output = self.run_command([
            sys.executable, "-m", "pip", "install", "-e", ".[stable]"
        ], cwd=str(repo_dir))
        
        if success:
            logger.info("✅ Fish-Speech installation completed")
            self.installation_log.append({"model": "fish-speech", "status": "success", "method": "git+pip"})
            return True
        else:
            # Fallback to basic installation
            success, output = self.run_command([
                sys.executable, "-m", "pip", "install", "-e", "."
            ], cwd=str(repo_dir))
            
            if success:
                logger.info("✅ Fish-Speech basic installation completed")
                self.installation_log.append({"model": "fish-speech", "status": "success", "method": "git+pip-basic"})
                return True
            else:
                self.installation_log.append({"model": "fish-speech", "status": "failed", "error": output})
                return False
    
    def install_gpt_sovits(self) -> bool:
        """Install GPT-SoVITS."""
        logger.info("Installing GPT-SoVITS...")
        
        repo_dir = self.models_dir / "GPT-SoVITS"
        
        # Clone repository
        if not repo_dir.exists():
            success, output = self.run_command([
                "git", "clone", "https://github.com/RVC-Boss/GPT-SoVITS.git", str(repo_dir)
            ])
            if not success:
                self.installation_log.append({"model": "gpt-sovits", "status": "failed", "error": "git clone failed"})
                return False
        
        # Install requirements
        requirements_file = repo_dir / "requirements.txt"
        if requirements_file.exists():
            success, output = self.run_command([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], cwd=str(repo_dir))
            
            if success:
                logger.info("✅ GPT-SoVITS installation completed")
                self.installation_log.append({"model": "gpt-sovits", "status": "success", "method": "git+requirements"})
                return True
            else:
                self.installation_log.append({"model": "gpt-sovits", "status": "failed", "error": output})
                return False
        else:
            logger.warning("No requirements.txt found for GPT-SoVITS")
            self.installation_log.append({"model": "gpt-sovits", "status": "partial", "error": "no requirements file"})
            return False
    
    def install_cosyvoice(self) -> bool:
        """Install CosyVoice."""
        logger.info("Installing CosyVoice...")
        
        repo_dir = self.models_dir / "CosyVoice"
        
        # Clone repository
        if not repo_dir.exists():
            success, output = self.run_command([
                "git", "clone", "https://github.com/FunAudioLLM/CosyVoice.git", str(repo_dir)
            ])
            if not success:
                self.installation_log.append({"model": "cosyvoice", "status": "failed", "error": "git clone failed"})
                return False
        
        # Install requirements
        requirements_file = repo_dir / "requirements.txt"
        if requirements_file.exists():
            success, output = self.run_command([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], cwd=str(repo_dir))
            
            if success:
                logger.info("✅ CosyVoice installation completed")
                self.installation_log.append({"model": "cosyvoice", "status": "success", "method": "git+requirements"})
                return True
            else:
                self.installation_log.append({"model": "cosyvoice", "status": "failed", "error": output})
                return False
        else:
            logger.warning("No requirements.txt found for CosyVoice")
            self.installation_log.append({"model": "cosyvoice", "status": "partial", "error": "no requirements file"})
            return False
    
    def install_coqui_tts(self) -> bool:
        """Install Coqui TTS."""
        logger.info("Installing Coqui TTS...")
        
        # Simple pip install
        success, output = self.run_command([sys.executable, "-m", "pip", "install", "TTS"])
        
        if success:
            # Test import
            try:
                import TTS
                logger.info("✅ Coqui TTS installation verified")
                self.installation_log.append({"model": "coqui-tts", "status": "success", "method": "pip"})
                return True
            except ImportError as e:
                logger.error(f"❌ Coqui TTS import failed: {e}")
                self.installation_log.append({"model": "coqui-tts", "status": "failed", "error": str(e)})
                return False
        else:
            self.installation_log.append({"model": "coqui-tts", "status": "failed", "error": output})
            return False
    
    def install_all_models(self, models: List[str] = None) -> Dict:
        """Install all specified models."""
        if models is None:
            models = ["chatterbox", "openvoice", "fish-speech", "gpt-sovits", "cosyvoice", "coqui-tts"]
        
        installation_methods = {
            "chatterbox": self.install_chatterbox,
            "openvoice": self.install_openvoice,
            "fish-speech": self.install_fish_speech,
            "gpt-sovits": self.install_gpt_sovits,
            "cosyvoice": self.install_cosyvoice,
            "coqui-tts": self.install_coqui_tts
        }
        
        results = {"successful": [], "failed": [], "total": len(models)}
        
        for model in models:
            if model in installation_methods:
                logger.info(f"\n{'='*50}")
                logger.info(f"Installing {model.upper()}")
                logger.info(f"{'='*50}")
                
                try:
                    success = installation_methods[model]()
                    if success:
                        results["successful"].append(model)
                    else:
                        results["failed"].append(model)
                except Exception as e:
                    logger.error(f"❌ Unexpected error installing {model}: {e}")
                    results["failed"].append(model)
                    self.installation_log.append({"model": model, "status": "failed", "error": str(e)})
            else:
                logger.error(f"❌ Unknown model: {model}")
                results["failed"].append(model)
        
        # Save installation log
        self.save_installation_log()
        
        return results
    
    def save_installation_log(self):
        """Save installation log to file."""
        log_file = self.models_dir / "installation_log.json"
        with open(log_file, 'w') as f:
            json.dump(self.installation_log, f, indent=2)
        logger.info(f"Installation log saved to {log_file}")
    
    def check_system_requirements(self) -> Dict:
        """Check system requirements for TTS models."""
        requirements = {
            "python_version": sys.version,
            "platform": platform.platform(),
            "architecture": platform.architecture(),
            "gpu_available": False,
            "cuda_available": False,
            "torch_version": None
        }
        
        # Check for PyTorch and CUDA
        try:
            import torch
            requirements["torch_version"] = torch.__version__
            requirements["cuda_available"] = torch.cuda.is_available()
            if torch.cuda.is_available():
                requirements["gpu_count"] = torch.cuda.device_count()
                requirements["gpu_names"] = [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())]
        except ImportError:
            logger.warning("PyTorch not installed - some models may not work properly")
        
        return requirements


def main():
    parser = argparse.ArgumentParser(description='Install TTS models for comparison study')
    parser.add_argument('--models', nargs='+', 
                       choices=['chatterbox', 'openvoice', 'fish-speech', 'gpt-sovits', 'cosyvoice', 'coqui-tts'],
                       help='Specific models to install (default: all)')
    parser.add_argument('--models-dir', default='models', help='Directory to install models')
    parser.add_argument('--check-requirements', action='store_true', help='Check system requirements only')
    
    args = parser.parse_args()
    
    installer = ModelInstaller(args.models_dir)
    
    if args.check_requirements:
        requirements = installer.check_system_requirements()
        print("\n" + "="*50)
        print("SYSTEM REQUIREMENTS CHECK")
        print("="*50)
        for key, value in requirements.items():
            print(f"{key}: {value}")
        return
    
    print("\n" + "="*50)
    print("TTS MODELS INSTALLATION")
    print("="*50)
    
    # Check system requirements first
    requirements = installer.check_system_requirements()
    logger.info("System requirements checked")
    
    # Install models
    results = installer.install_all_models(args.models)
    
    # Print summary
    print("\n" + "="*50)
    print("INSTALLATION SUMMARY")
    print("="*50)
    print(f"Total models: {results['total']}")
    print(f"✅ Successful: {len(results['successful'])} - {results['successful']}")
    print(f"❌ Failed: {len(results['failed'])} - {results['failed']}")
    
    if results['failed']:
        print(f"\n⚠️  Some installations failed. Check the log file for details.")
        print(f"Log file: {installer.models_dir}/installation_log.json")
    else:
        print(f"\n🎉 All models installed successfully!")


if __name__ == "__main__":
    main()
