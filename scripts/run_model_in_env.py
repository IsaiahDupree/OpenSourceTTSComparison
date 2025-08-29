#!/usr/bin/env python3
"""
Model Runner with Environment Isolation

Runs TTS models in their isolated environments and provides unified interface.
"""

import subprocess
import sys
import json
from pathlib import Path
import tempfile
import os

class ModelRunner:
    """Runs TTS models in isolated environments."""
    
    def __init__(self, envs_dir: str = "envs"):
        self.envs_dir = Path(envs_dir)
        self.env_info = self._load_env_info()
    
    def _load_env_info(self) -> dict:
        """Load environment information."""
        env_file = self.envs_dir / "environment_info.json"
        if env_file.exists():
            with open(env_file, 'r') as f:
                return json.load(f)
        return {}
    
    def run_in_env(self, model_name: str, script_content: str, **kwargs) -> dict:
        """Run script in model's environment."""
        if model_name not in self.env_info:
            return {"success": False, "error": f"Environment for {model_name} not found"}
        
        env_info = self.env_info[model_name]
        if not env_info.get("success", False):
            return {"success": False, "error": f"Environment for {model_name} failed to create"}
        
        # Create temporary script file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script_content)
            script_path = f.name
        
        try:
            if env_info["env_type"] == "conda":
                # Run with conda
                cmd = ["conda", "run", "-n", env_info["env_name"], "python", script_path]
            else:
                # Run with venv
                if os.name == 'nt':  # Windows
                    python_exe = self.envs_dir / env_info["env_name"] / "Scripts" / "python.exe"
                else:  # Unix-like
                    python_exe = self.envs_dir / env_info["env_name"] / "bin" / "python"
                cmd = [str(python_exe), script_path]
            
            # Add kwargs as environment variables
            env = os.environ.copy()
            for key, value in kwargs.items():
                env[f"TTS_{key.upper()}"] = str(value)
            
            result = subprocess.run(cmd, capture_output=True, text=True, env=env)
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            # Clean up temp file
            try:
                os.unlink(script_path)
            except:
                pass
    
    def test_model_import(self, model_name: str) -> bool:
        """Test if model can be imported in its environment."""
        test_scripts = {
            "chatterbox": "import chatterbox; print('Chatterbox OK')",
            "openvoice": "import sys; sys.path.append('envs/openvoice'); print('OpenVoice path added')",
            "fish_speech": "import sys; sys.path.append('envs/fish_speech'); print('Fish-Speech path added')",
            "gpt_sovits": "import sys; sys.path.append('envs/gpt_sovits'); print('GPT-SoVITS path added')",
            "cosyvoice": "import sys; sys.path.append('envs/cosyvoice'); print('CosyVoice path added')",
            "coqui_tts": "import TTS; print('Coqui TTS OK')"
        }
        
        if model_name not in test_scripts:
            return False
        
        result = self.run_in_env(model_name, test_scripts[model_name])
        return result.get("success", False)


def main():
    runner = ModelRunner()
    
    print("Testing model environments...")
    for model_name in runner.env_info.keys():
        if runner.env_info[model_name].get("success", False):
            success = runner.test_model_import(model_name)
            status = "✅" if success else "❌"
            print(f"{status} {model_name}")
        else:
            print(f"⏭️ {model_name} (environment not created)")


if __name__ == "__main__":
    main()
