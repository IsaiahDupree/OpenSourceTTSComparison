#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test to verify Docker-based Coqui TTS works.
Quick check without full setup.
"""

import subprocess
import sys
import io

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def test_docker_available():
    """Check if Docker is available."""
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✅ Docker available: {result.stdout.strip()}")
            return True
        else:
            print("❌ Docker command failed")
            return False
    except FileNotFoundError:
        print("❌ Docker not found")
        print("\nInstall Docker Desktop from:")
        print("  https://www.docker.com/products/docker-desktop/")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_coqui_image_exists():
    """Check if Coqui TTS image is already pulled."""
    try:
        result = subprocess.run(
            ["docker", "images", "coqui/tts:latest", "--format", "{{.Repository}}:{{.Tag}}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            print("✅ Coqui TTS image already available")
            return True
        else:
            print("⚠️  Coqui TTS image not found (will need to pull)")
            return False
    except Exception as e:
        print(f"⚠️  Could not check images: {e}")
        return False

def quick_test():
    """Quick test of Coqui TTS in Docker."""
    print("\nTesting Coqui TTS in Docker...")
    try:
        result = subprocess.run(
            [
                "docker", "run", "--rm",
                "coqui/tts:latest",
                "python", "-c",
                "from TTS.api import TTS; print('✅ Coqui TTS works in Docker!')"
            ],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print(result.stdout.strip())
            return True
        else:
            print("❌ Test failed")
            if result.stderr:
                print(f"Error: {result.stderr[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Test timed out (image may be downloading)")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main test function."""
    print("=" * 70)
    print("Docker Voice Cloning Quick Test")
    print("=" * 70)
    
    # Check Docker
    if not test_docker_available():
        return False
    
    # Check if image exists
    image_exists = test_coqui_image_exists()
    
    if not image_exists:
        print("\n⚠️  Image not found. You'll need to pull it first:")
        print("   docker pull coqui/tts:latest")
        print("\n   Or run: python docker_voice_cloning.py")
        return False
    
    # Quick test
    return quick_test()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

