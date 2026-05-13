#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete build and test script for Docker-based voice cloning.
Pulls image, tests functionality, and verifies voice cloning works.
"""

import subprocess
import sys
import io
import time
import json
from pathlib import Path
from datetime import datetime
import logging

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configure comprehensive console logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ],
    force=True
)
logger = logging.getLogger(__name__)

# Also log to file
file_handler = logging.FileHandler('build_test.log', encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
logger.addHandler(file_handler)


class BuildAndTest:
    """Complete build and test suite."""
    
    def __init__(self):
        self.results = {
            "docker_check": False,
            "image_pull": False,
            "basic_test": False,
            "voice_cloning_test": False,
            "output_verification": False,
            "errors": [],
            "timings": {}
        }
        self.start_time = time.time()
        self.image_name = "synesthesiam/coqui-tts:latest"  # Default image
    
    def log(self, message, level="INFO"):
        """Log with elapsed time."""
        elapsed = time.time() - self.start_time
        getattr(logger, level.lower())(f"[{elapsed:6.1f}s] {message}")
    
    def check_docker(self):
        """Step 1: Check Docker is available."""
        self.log("=" * 70)
        self.log("STEP 1: Checking Docker availability")
        self.log("=" * 70)
        
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                self.log(f"✅ Docker available: {result.stdout.strip()}")
                self.results["docker_check"] = True
                return True
            else:
                self.log("❌ Docker command failed")
                self.results["errors"].append("Docker command failed")
                return False
        except FileNotFoundError:
            self.log("❌ Docker not found. Please install Docker Desktop")
            self.results["errors"].append("Docker not installed")
            return False
        except Exception as e:
            self.log(f"❌ Error checking Docker: {e}")
            self.results["errors"].append(f"Docker check error: {e}")
            return False
    
    def check_image_exists(self):
        """Check if image is already pulled."""
        self.log("\nChecking if Coqui TTS image exists...")
        # Try multiple possible image names
        image_names = ["synesthesiam/coqui-tts:latest", "coqui/tts:latest"]
        
        for image_name in image_names:
            try:
                result = subprocess.run(
                    ["docker", "images", image_name, "--format", "{{.Repository}}:{{.Tag}}"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0 and result.stdout.strip():
                    self.log(f"✅ Image already exists: {image_name}")
                    self.image_name = image_name
                    return True
            except:
                continue
        
        self.log("⚠️  Image not found, will need to pull")
        self.image_name = "synesthesiam/coqui-tts:latest"  # Default to working image
        return False
    
    def pull_image(self):
        """Step 2: Pull Docker image."""
        self.log("\n" + "=" * 70)
        self.log("STEP 2: Pulling Coqui TTS Docker image")
        self.log("=" * 70)
        self.log("This may take 5-15 minutes depending on your internet speed...")
        self.log("Image size: ~2-3GB")
        
        pull_start = time.time()
        
        try:
            process = subprocess.Popen(
                ["docker", "pull", self.image_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            last_progress = ""
            for line in process.stdout:
                line = line.strip()
                if line:
                    # Show meaningful progress
                    if "Pulling" in line or "Downloading" in line or "Extracting" in line:
                        # Only show if different from last
                        if line != last_progress:
                            self.log(f"  → {line[:70]}")
                            last_progress = line
                    elif "Already exists" in line or "up to date" in line:
                        self.log(f"  → {line}")
            
            return_code = process.wait()
            pull_time = time.time() - pull_start
            self.results["timings"]["image_pull"] = pull_time
            
            if return_code == 0:
                self.log(f"✅ Image pulled successfully in {pull_time:.1f} seconds")
                self.results["image_pull"] = True
                return True
            else:
                self.log("❌ Failed to pull image")
                self.results["errors"].append("Image pull failed")
                return False
                
        except Exception as e:
            self.log(f"❌ Error pulling image: {e}")
            self.results["errors"].append(f"Pull error: {e}")
            return False
    
    def test_basic_import(self):
        """Step 3: Test basic import."""
        self.log("\n" + "=" * 70)
        self.log("STEP 3: Testing basic import")
        self.log("=" * 70)
        
        test_start = time.time()
        
        try:
            result = subprocess.run(
                [
                    "docker", "run", "--rm",
                    self.image_name,
                    "python", "-c",
                    "from TTS.api import TTS; print('SUCCESS: Coqui TTS imported successfully!')"
                ],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            test_time = time.time() - test_start
            self.results["timings"]["basic_test"] = test_time
            
            if result.returncode == 0:
                self.log("✅ Basic import test passed!")
                self.log(f"   Output: {result.stdout.strip()}")
                self.results["basic_test"] = True
                return True
            else:
                self.log("❌ Basic import test failed")
                if result.stderr:
                    self.log(f"   Error: {result.stderr[:200]}")
                self.results["errors"].append("Basic import failed")
                return False
                
        except subprocess.TimeoutExpired:
            self.log("❌ Test timed out")
            self.results["errors"].append("Basic test timeout")
            return False
        except Exception as e:
            self.log(f"❌ Error: {e}")
            self.results["errors"].append(f"Basic test error: {e}")
            return False
    
    def create_test_reference_audio(self):
        """Create a simple test reference audio file."""
        self.log("\nCreating test reference audio...")
        
        try:
            import numpy as np
            import soundfile as sf
            
            # Create a simple sine wave (simulating voice)
            duration = 3.0
            sample_rate = 22050
            t = np.linspace(0, duration, int(sample_rate * duration))
            
            # Mix of frequencies to make it more voice-like
            audio = (
                0.3 * np.sin(2 * np.pi * 200 * t) +
                0.2 * np.sin(2 * np.pi * 400 * t) +
                0.1 * np.sin(2 * np.pi * 600 * t)
            )
            audio = audio.astype(np.float32)
            
            ref_path = Path("test_reference.wav")
            sf.write(str(ref_path), audio, sample_rate)
            self.log(f"✅ Created test reference: {ref_path}")
            return str(ref_path)
            
        except ImportError:
            self.log("⚠️  numpy/soundfile not available, will use Docker to create test audio")
            return None
        except Exception as e:
            self.log(f"⚠️  Could not create test audio: {e}")
            return None
    
    def test_voice_cloning(self):
        """Step 4: Test voice cloning functionality."""
        self.log("\n" + "=" * 70)
        self.log("STEP 4: Testing voice cloning")
        self.log("=" * 70)
        
        test_start = time.time()
        
        # Create test script
        test_script = """
import sys
from TTS.api import TTS
import numpy as np
import soundfile as sf

# Create a simple test reference audio
duration = 3.0
sample_rate = 22050
t = np.linspace(0, duration, int(sample_rate * duration))
audio = 0.3 * np.sin(2 * np.pi * 200 * t) + 0.2 * np.sin(2 * np.pi * 400 * t)
audio = audio.astype(np.float32)
sf.write('test_ref.wav', audio, sample_rate)

# Test voice cloning
print('Loading XTTS-v2 model...')
model = TTS('tts_models/multilingual/multi-dataset/xtts_v2', gpu=False)

print('Generating cloned voice...')
test_text = 'Hello, this is a test of voice cloning. Does it work correctly?'
model.tts_to_file(
    text=test_text,
    speaker_wav='test_ref.wav',
    file_path='test_output.wav'
)

print('SUCCESS: Voice cloning test passed!')
print('Output file: test_output.wav')
"""
        
        script_path = Path("docker_test_script.py")
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(test_script)
        
        self.log("Created test script, running in Docker...")
        
        try:
            # Get current directory for volume mount
            current_dir = Path.cwd()
            
            result = subprocess.run(
                [
                    "docker", "run", "--rm",
                    "-v", f"{current_dir}:/workspace",
                    "-w", "/workspace",
                    self.image_name,
                    "python", "docker_test_script.py"
                ],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes for model download and generation
            )
            
            test_time = time.time() - test_start
            self.results["timings"]["voice_cloning_test"] = test_time
            
            # Cleanup script
            script_path.unlink(missing_ok=True)
            
            if result.returncode == 0:
                self.log("✅ Voice cloning test passed!")
                for line in result.stdout.split('\n'):
                    if line.strip():
                        self.log(f"   {line}")
                self.results["voice_cloning_test"] = True
                return True
            else:
                self.log("❌ Voice cloning test failed")
                if result.stderr:
                    self.log(f"   Error: {result.stderr[:300]}")
                if result.stdout:
                    self.log(f"   Output: {result.stdout[:300]}")
                self.results["errors"].append("Voice cloning test failed")
                return False
                
        except subprocess.TimeoutExpired:
            self.log("❌ Test timed out (model may be downloading)")
            self.results["errors"].append("Voice cloning test timeout")
            return False
        except Exception as e:
            self.log(f"❌ Error: {e}")
            self.results["errors"].append(f"Voice cloning error: {e}")
            return False
    
    def verify_output(self):
        """Step 5: Verify output files."""
        self.log("\n" + "=" * 70)
        self.log("STEP 5: Verifying output files")
        self.log("=" * 70)
        
        output_file = Path("test_output.wav")
        ref_file = Path("test_ref.wav")
        
        if output_file.exists():
            file_size = output_file.stat().st_size
            self.log(f"✅ Output file exists: {output_file}")
            self.log(f"   Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
            if file_size > 1000:  # At least 1KB
                self.log("✅ Output file has reasonable size")
                self.results["output_verification"] = True
                return True
            else:
                self.log("⚠️  Output file seems too small")
                return False
        else:
            self.log("❌ Output file not found")
            self.results["errors"].append("Output file not created")
            return False
    
    def generate_report(self):
        """Generate final test report."""
        total_time = time.time() - self.start_time
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_time_seconds": total_time,
            "results": self.results,
            "summary": {
                "all_passed": all([
                    self.results["docker_check"],
                    self.results["image_pull"],
                    self.results["basic_test"],
                    self.results["voice_cloning_test"],
                    self.results["output_verification"]
                ]),
                "tests_passed": sum([
                    self.results["docker_check"],
                    self.results["image_pull"],
                    self.results["basic_test"],
                    self.results["voice_cloning_test"],
                    self.results["output_verification"]
                ]),
                "tests_total": 5
            }
        }
        
        return report
    
    def run_all_tests(self):
        """Run complete build and test suite."""
        self.log("=" * 70)
        self.log("VOICE CLONING BUILD AND TEST SUITE")
        self.log(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("=" * 70)
        
        # Step 1: Check Docker
        if not self.check_docker():
            self.log("\n❌ Docker check failed. Cannot proceed.")
            return False
        
        # Step 2: Check or pull image
        image_exists = self.check_image_exists()
        if not image_exists:
            self.log(f"\nPulling image: {self.image_name}")
            if not self.pull_image():
                self.log("\n❌ Failed to pull image. Cannot proceed.")
                return False
        else:
            self.log(f"\n✅ Image already available: {self.image_name}")
            self.results["image_pull"] = True
            self.results["timings"]["image_pull"] = 0
        
        # Step 3: Basic test
        if not self.test_basic_import():
            self.log("\n❌ Basic test failed.")
            return False
        
        # Step 4: Voice cloning test
        if not self.test_voice_cloning():
            self.log("\n❌ Voice cloning test failed.")
            return False
        
        # Step 5: Verify output
        if not self.verify_output():
            self.log("\n⚠️  Output verification failed.")
        
        # Generate report
        report = self.generate_report()
        
        # Print summary
        self.log("\n" + "=" * 70)
        self.log("TEST SUMMARY")
        self.log("=" * 70)
        
        total_time = time.time() - self.start_time
        
        if report["summary"]["all_passed"]:
            self.log("✅ ALL TESTS PASSED!")
        else:
            self.log(f"⚠️  {report['summary']['tests_passed']}/{report['summary']['tests_total']} tests passed")
        
        self.log(f"\nTotal time: {total_time:.1f} seconds")
        self.log(f"  - Image pull: {self.results['timings'].get('image_pull', 0):.1f}s")
        self.log(f"  - Basic test: {self.results['timings'].get('basic_test', 0):.1f}s")
        self.log(f"  - Voice cloning: {self.results['timings'].get('voice_cloning_test', 0):.1f}s")
        
        if self.results["errors"]:
            self.log("\nErrors encountered:")
            for error in self.results["errors"]:
                self.log(f"  - {error}")
        
        # Save report
        output_dir = Path("results_voice_cloning")
        output_dir.mkdir(exist_ok=True)
        
        report_file = output_dir / "build_test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        
        self.log(f"\n📊 Full report saved: {report_file}")
        
        return report["summary"]["all_passed"]


def main():
    """Main function."""
    tester = BuildAndTest()
    
    try:
        success = tester.run_all_tests()
        
        if success:
            print("\n" + "=" * 70)
            print("🎉 BUILD AND TEST COMPLETE - ALL PASSED!")
            print("=" * 70)
            print("\nYou can now use voice cloning!")
            print("Example:")
            print("  docker run --rm -v \"${PWD}:/workspace\" -w /workspace coqui/tts:latest python -c \"...\"")
            print("\nSee QUICK_START_DOCKER.md for usage instructions.")
        else:
            print("\n" + "=" * 70)
            print("⚠️  BUILD AND TEST COMPLETE WITH ISSUES")
            print("=" * 70)
            print("\nCheck the logs above for details.")
            print("Some tests may have failed, but basic functionality might still work.")
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

