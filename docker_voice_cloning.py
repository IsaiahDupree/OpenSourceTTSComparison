#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Docker-based voice cloning solution - No build issues!
Uses pre-built Docker images to avoid all installation problems.
"""

import subprocess
import sys
import json
import time
import io
from pathlib import Path
from datetime import datetime
import logging

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


class DockerVoiceCloning:
    """Manage Docker-based voice cloning solutions."""
    
    def __init__(self):
        self.docker_available = False
        self.check_docker()
    
    def log(self, message, level="INFO"):
        """Log message."""
        getattr(logger, level.lower())(message)
    
    def check_docker(self):
        """Check if Docker is available."""
        self.log("Checking Docker availability...")
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                self.docker_available = True
                self.log(f"✅ Docker is available: {result.stdout.strip()}")
                return True
            else:
                self.log("❌ Docker command failed")
                return False
        except FileNotFoundError:
            self.log("❌ Docker not found. Please install Docker Desktop:")
            self.log("   Windows: https://www.docker.com/products/docker-desktop/")
            self.log("   Mac: https://www.docker.com/products/docker-desktop/")
            self.log("   Linux: https://docs.docker.com/engine/install/")
            return False
        except Exception as e:
            self.log(f"❌ Error checking Docker: {e}")
            return False
    
    def pull_coqui_tts_image(self):
        """Pull Coqui TTS Docker image."""
        if not self.docker_available:
            return False
        
        self.log("Pulling Coqui TTS Docker image...")
        self.log("This may take a few minutes (downloading ~2-3GB)...")
        
        try:
            process = subprocess.Popen(
                ["docker", "pull", "coqui/tts:latest"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            for line in process.stdout:
                line = line.strip()
                if line:
                    # Show progress
                    if "Downloading" in line or "Extracting" in line or "Pulling" in line:
                        self.log(f"  → {line[:80]}")
            
            return_code = process.wait()
            
            if return_code == 0:
                self.log("✅ Coqui TTS image pulled successfully!")
                return True
            else:
                self.log("❌ Failed to pull image")
                return False
                
        except Exception as e:
            self.log(f"❌ Error pulling image: {e}")
            return False
    
    def test_coqui_tts_docker(self):
        """Test Coqui TTS in Docker."""
        if not self.docker_available:
            return False
        
        self.log("Testing Coqui TTS in Docker...")
        
        try:
            # Test import
            test_command = 'python -c "from TTS.api import TTS; print(\'✅ Coqui TTS imported successfully!\')"'
            
            result = subprocess.run(
                ["docker", "run", "--rm", "coqui/tts:latest", "sh", "-c", test_command],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                self.log("✅ Coqui TTS works in Docker!")
                self.log(result.stdout.strip())
                return True
            else:
                self.log("❌ Test failed")
                self.log(result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            self.log("❌ Test timed out")
            return False
        except Exception as e:
            self.log(f"❌ Error: {e}")
            return False
    
    def create_docker_usage_script(self):
        """Create a script showing how to use Docker for voice cloning."""
        script_content = '''#!/usr/bin/env python3
"""
Example: Using Coqui TTS in Docker for voice cloning
"""

# Method 1: Run directly with docker run
# docker run --rm -v "$(pwd):/workspace" coqui/tts:latest python -c "
# from TTS.api import TTS
# model = TTS('tts_models/multilingual/multi-dataset/xtts_v2')
# model.tts_to_file(text='Hello, this is a test', speaker_wav='reference.wav', file_path='output.wav')
# "

# Method 2: Interactive shell
# docker run -it --rm -v "$(pwd):/workspace" coqui/tts:latest bash

# Method 3: Create a Python script and run it
# docker run --rm -v "$(pwd):/workspace" coqui/tts:latest python your_script.py

import subprocess
import sys

def run_coqui_tts_docker(text, speaker_wav, output_file):
    """Run Coqui TTS voice cloning in Docker."""
    
    # Create a temporary Python script
    script = f"""
from TTS.api import TTS
import sys

model = TTS('tts_models/multilingual/multi-dataset/xtts_v2')
model.tts_to_file(
    text='{text}',
    speaker_wav='{speaker_wav}',
    file_path='{output_file}'
)
print(f'✅ Generated: {output_file}')
"""
    
    # Write script to file
    script_path = "temp_docker_script.py"
    with open(script_path, 'w') as f:
        f.write(script)
    
    # Run in Docker
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{Path.cwd()}:/workspace",
        "-w", "/workspace",
        "coqui/tts:latest",
        "python", script_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Cleanup
    Path(script_path).unlink(missing_ok=True)
    
    if result.returncode == 0:
        print(result.stdout)
        return True
    else:
        print(f"Error: {result.stderr}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python docker_voice_cloning_example.py <text> <speaker_wav> <output_file>")
        sys.exit(1)
    
    text = sys.argv[1]
    speaker_wav = sys.argv[2]
    output_file = sys.argv[3]
    
    run_coqui_tts_docker(text, speaker_wav, output_file)
'''
        
        script_path = Path("docker_voice_cloning_example.py")
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        self.log(f"✅ Created usage script: {script_path}")
        return script_path
    
    def create_docker_compose(self):
        """Create docker-compose.yml for easier management."""
        compose_content = '''version: '3.8'

services:
  coqui-tts:
    image: coqui/tts:latest
    container_name: voice-cloning-coqui
    volumes:
      - ./:/workspace
      - ./models_cache:/root/.local/share/tts  # Cache models
    working_dir: /workspace
    command: tail -f /dev/null  # Keep container running
    # Uncomment for GPU support:
    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - driver: nvidia
    #           count: 1
    #           capabilities: [gpu]
'''
        
        compose_path = Path("docker-compose.yml")
        with open(compose_path, 'w') as f:
            f.write(compose_content)
        
        self.log(f"✅ Created docker-compose.yml")
        return compose_path
    
    def setup_docker_solution(self):
        """Complete Docker setup."""
        self.log("=" * 70)
        self.log("Docker Voice Cloning Setup")
        self.log("=" * 70)
        
        if not self.docker_available:
            self.log("\n❌ Docker is not available. Please install Docker Desktop first.")
            return False
        
        # Pull image
        if not self.pull_coqui_tts_image():
            self.log("\n❌ Failed to pull Docker image")
            return False
        
        # Test
        if not self.test_coqui_tts_docker():
            self.log("\n⚠️  Image pulled but test failed")
        
        # Create helper files
        self.create_docker_usage_script()
        self.create_docker_compose()
        
        # Create README
        readme_content = '''# Docker Voice Cloning Setup

## Quick Start

### 1. Pull the image (if not already done):
```bash
docker pull coqui/tts:latest
```

### 2. Test it works:
```bash
docker run --rm coqui/tts:latest python -c "from TTS.api import TTS; print('Working!')"
```

### 3. Run voice cloning:
```bash
# Make sure you have a reference audio file
docker run --rm -v "$(pwd):/workspace" -w /workspace coqui/tts:latest python -c "
from TTS.api import TTS
model = TTS('tts_models/multilingual/multi-dataset/xtts_v2')
model.tts_to_file(
    text='Hello, this is a test',
    speaker_wav='reference.wav',
    file_path='output.wav'
)
"
```

## Using docker-compose

### Start container:
```bash
docker-compose up -d
```

### Run commands in container:
```bash
docker-compose exec coqui-tts python your_script.py
```

### Stop container:
```bash
docker-compose down
```

## Advantages

✅ No build issues - everything is pre-built
✅ No dependency conflicts
✅ Works on any system with Docker
✅ Easy to update (just pull new image)
✅ Isolated environment

## GPU Support

For GPU acceleration, you need:
1. NVIDIA GPU
2. NVIDIA Docker runtime installed
3. Uncomment GPU section in docker-compose.yml

## Troubleshooting

### Container won't start:
- Check Docker is running: `docker ps`
- Check disk space: `docker system df`

### Permission issues:
- On Linux, may need to use `sudo` or add user to docker group
- On Windows/Mac, Docker Desktop handles permissions

### Out of memory:
- Increase Docker Desktop memory limit in settings
- Use CPU mode (slower but uses less memory)
'''
        
        readme_path = Path("DOCKER_README.md")
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        
        self.log(f"\n✅ Docker setup complete!")
        self.log(f"📄 See DOCKER_README.md for usage instructions")
        
        return True


def main():
    """Main function."""
    docker_setup = DockerVoiceCloning()
    
    if not docker_setup.docker_available:
        print("\n" + "=" * 70)
        print("DOCKER NOT FOUND")
        print("=" * 70)
        print("\nPlease install Docker Desktop:")
        print("  Windows: https://www.docker.com/products/docker-desktop/")
        print("  Mac: https://www.docker.com/products/docker-desktop/")
        print("  Linux: https://docs.docker.com/engine/install/")
        print("\nAfter installing, restart this script.")
        return
    
    print("\n" + "=" * 70)
    print("DOCKER VOICE CLONING SETUP")
    print("=" * 70)
    print("\nThis will:")
    print("  1. Pull Coqui TTS Docker image (~2-3GB download)")
    print("  2. Test that it works")
    print("  3. Create helper scripts for easy usage")
    print("\nThis avoids ALL build issues!")
    print("\nProceed? (This will take a few minutes to download)")
    
    try:
        response = input("\nPress Enter to continue or Ctrl+C to cancel: ")
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        return
    
    success = docker_setup.setup_docker_solution()
    
    if success:
        print("\n" + "=" * 70)
        print("✅ SETUP COMPLETE!")
        print("=" * 70)
        print("\nYou can now use voice cloning without any build issues!")
        print("See DOCKER_README.md for usage instructions.")
    else:
        print("\n" + "=" * 70)
        print("⚠️  SETUP INCOMPLETE")
        print("=" * 70)
        print("\nCheck the logs above for issues.")


if __name__ == "__main__":
    main()

