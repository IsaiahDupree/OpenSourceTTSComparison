#!/usr/bin/env python3
"""
Environment Setup for TTS Models

Creates isolated conda/venv environments for each TTS model to avoid dependency conflicts.
"""

import subprocess
import sys
import os
from pathlib import Path
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnvironmentManager:
    """Manages isolated environments for TTS models."""
    
    def __init__(self, base_dir: str = "envs"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        self.env_configs = self._load_env_configs()
        
    def _load_env_configs(self) -> dict:
        """Load environment configurations for each model."""
        return {
            "chatterbox": {
                "python_version": "3.10",
                "requirements": [
                    "chatterbox-tts",
                    "torch>=1.11.0",
                    "numpy>=1.21.0",
                    "soundfile>=0.10.0"
                ]
            },
            "openvoice": {
                "python_version": "3.9",
                "requirements": [
                    "torch>=1.11.0",
                    "torchaudio>=0.11.0",
                    "numpy>=1.21.0",
                    "librosa>=0.9.0",
                    "soundfile>=0.10.0",
                    "scipy>=1.7.0",
                    "transformers>=4.20.0"
                ],
                "git_repo": "https://github.com/myshell-ai/OpenVoice.git"
            },
            "fish_speech": {
                "python_version": "3.10",
                "requirements": [
                    "torch>=2.0.0",
                    "torchaudio>=2.0.0",
                    "transformers>=4.30.0",
                    "datasets>=2.0.0",
                    "librosa>=0.9.0",
                    "soundfile>=0.10.0",
                    "accelerate>=0.20.0"
                ],
                "git_repo": "https://github.com/fishaudio/fish-speech.git"
            },
            "gpt_sovits": {
                "python_version": "3.9",
                "requirements": [
                    "torch>=1.13.0",
                    "torchaudio>=0.13.0",
                    "numpy>=1.21.0",
                    "librosa>=0.9.0",
                    "soundfile>=0.10.0",
                    "scipy>=1.7.0",
                    "matplotlib>=3.5.0",
                    "gradio>=3.0.0"
                ],
                "git_repo": "https://github.com/RVC-Boss/GPT-SoVITS.git"
            },
            "cosyvoice": {
                "python_version": "3.10",
                "requirements": [
                    "torch>=2.0.0",
                    "torchaudio>=2.0.0",
                    "transformers>=4.30.0",
                    "librosa>=0.9.0",
                    "soundfile>=0.10.0",
                    "scipy>=1.7.0",
                    "numpy>=1.21.0"
                ],
                "git_repo": "https://github.com/FunAudioLLM/CosyVoice.git"
            },
            "coqui_tts": {
                "python_version": "3.10",
                "requirements": [
                    "TTS>=0.20.0",
                    "torch>=1.11.0",
                    "torchaudio>=0.11.0",
                    "numpy>=1.21.0",
                    "librosa>=0.9.0",
                    "soundfile>=0.10.0"
                ]
            }
        }
    
    def check_conda_available(self) -> bool:
        """Check if conda is available."""
        try:
            subprocess.run(["conda", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def create_conda_env(self, model_name: str) -> bool:
        """Create conda environment for model."""
        config = self.env_configs[model_name]
        env_name = f"tts_{model_name}"
        
        try:
            # Create conda environment
            cmd = [
                "conda", "create", "-n", env_name, 
                f"python={config['python_version']}", "-y"
            ]
            subprocess.run(cmd, check=True)
            logger.info(f"✅ Created conda environment: {env_name}")
            
            # Install requirements
            for req in config['requirements']:
                cmd = ["conda", "run", "-n", env_name, "pip", "install", req]
                try:
                    subprocess.run(cmd, check=True, capture_output=True)
                    logger.info(f"✅ Installed {req} in {env_name}")
                except subprocess.CalledProcessError as e:
                    logger.warning(f"⚠️ Failed to install {req}: {e}")
            
            # Clone git repo if specified
            if "git_repo" in config:
                repo_dir = self.base_dir / model_name
                if not repo_dir.exists():
                    cmd = ["git", "clone", config["git_repo"], str(repo_dir)]
                    subprocess.run(cmd, check=True)
                    logger.info(f"✅ Cloned {config['git_repo']}")
                
                # Install in development mode
                cmd = ["conda", "run", "-n", env_name, "pip", "install", "-e", str(repo_dir)]
                try:
                    subprocess.run(cmd, check=True, capture_output=True)
                    logger.info(f"✅ Installed {model_name} in development mode")
                except subprocess.CalledProcessError as e:
                    logger.warning(f"⚠️ Failed to install {model_name} in dev mode: {e}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to create environment for {model_name}: {e}")
            return False
    
    def create_venv(self, model_name: str) -> bool:
        """Create virtual environment for model."""
        config = self.env_configs[model_name]
        env_dir = self.base_dir / f"venv_{model_name}"
        
        try:
            # Create virtual environment
            subprocess.run([sys.executable, "-m", "venv", str(env_dir)], check=True)
            logger.info(f"✅ Created virtual environment: {env_dir}")
            
            # Get python executable path
            if os.name == 'nt':  # Windows
                python_exe = env_dir / "Scripts" / "python.exe"
                pip_exe = env_dir / "Scripts" / "pip.exe"
            else:  # Unix-like
                python_exe = env_dir / "bin" / "python"
                pip_exe = env_dir / "bin" / "pip"
            
            # Upgrade pip
            subprocess.run([str(pip_exe), "install", "--upgrade", "pip"], check=True)
            
            # Install requirements
            for req in config['requirements']:
                try:
                    subprocess.run([str(pip_exe), "install", req], check=True, capture_output=True)
                    logger.info(f"✅ Installed {req} in {env_dir.name}")
                except subprocess.CalledProcessError as e:
                    logger.warning(f"⚠️ Failed to install {req}: {e}")
            
            # Clone git repo if specified
            if "git_repo" in config:
                repo_dir = self.base_dir / model_name
                if not repo_dir.exists():
                    cmd = ["git", "clone", config["git_repo"], str(repo_dir)]
                    subprocess.run(cmd, check=True)
                    logger.info(f"✅ Cloned {config['git_repo']}")
                
                # Install in development mode
                try:
                    subprocess.run([str(pip_exe), "install", "-e", str(repo_dir)], 
                                 check=True, capture_output=True)
                    logger.info(f"✅ Installed {model_name} in development mode")
                except subprocess.CalledProcessError as e:
                    logger.warning(f"⚠️ Failed to install {model_name} in dev mode: {e}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to create virtual environment for {model_name}: {e}")
            return False
    
    def setup_all_environments(self) -> dict:
        """Set up environments for all models."""
        results = {}
        use_conda = self.check_conda_available()
        
        logger.info(f"Using {'conda' if use_conda else 'venv'} for environment management")
        
        for model_name in self.env_configs.keys():
            logger.info(f"\n{'='*50}")
            logger.info(f"Setting up environment for {model_name.upper()}")
            logger.info(f"{'='*50}")
            
            if use_conda:
                success = self.create_conda_env(model_name)
            else:
                success = self.create_venv(model_name)
            
            results[model_name] = {
                "success": success,
                "env_type": "conda" if use_conda else "venv",
                "env_name": f"tts_{model_name}" if use_conda else f"venv_{model_name}"
            }
        
        # Save environment info
        with open(self.base_dir / "environment_info.json", 'w') as f:
            json.dump(results, f, indent=2)
        
        return results
    
    def get_activation_commands(self) -> dict:
        """Get activation commands for each environment."""
        env_info_file = self.base_dir / "environment_info.json"
        if not env_info_file.exists():
            return {}
        
        with open(env_info_file, 'r') as f:
            env_info = json.load(f)
        
        commands = {}
        for model_name, info in env_info.items():
            if not info["success"]:
                continue
                
            if info["env_type"] == "conda":
                commands[model_name] = f"conda activate {info['env_name']}"
            else:
                if os.name == 'nt':  # Windows
                    commands[model_name] = f"{self.base_dir}\\{info['env_name']}\\Scripts\\activate"
                else:  # Unix-like
                    commands[model_name] = f"source {self.base_dir}/{info['env_name']}/bin/activate"
        
        return commands


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Set up isolated environments for TTS models')
    parser.add_argument('--models', nargs='+', help='Specific models to set up')
    parser.add_argument('--envs-dir', default='envs', help='Directory for environments')
    
    args = parser.parse_args()
    
    manager = EnvironmentManager(args.envs_dir)
    
    if args.models:
        # Set up specific models
        results = {}
        for model in args.models:
            if model in manager.env_configs:
                if manager.check_conda_available():
                    results[model] = {"success": manager.create_conda_env(model)}
                else:
                    results[model] = {"success": manager.create_venv(model)}
            else:
                logger.error(f"Unknown model: {model}")
    else:
        # Set up all models
        results = manager.setup_all_environments()
    
    # Print summary
    print(f"\n{'='*60}")
    print("ENVIRONMENT SETUP SUMMARY")
    print(f"{'='*60}")
    
    successful = [m for m, r in results.items() if r.get("success", False)]
    failed = [m for m, r in results.items() if not r.get("success", False)]
    
    print(f"✅ Successful: {len(successful)} - {successful}")
    print(f"❌ Failed: {len(failed)} - {failed}")
    
    if successful:
        print(f"\nActivation commands:")
        commands = manager.get_activation_commands()
        for model, cmd in commands.items():
            print(f"  {model}: {cmd}")
    
    print(f"\nEnvironment info saved to: {manager.base_dir}/environment_info.json")


if __name__ == "__main__":
    main()
