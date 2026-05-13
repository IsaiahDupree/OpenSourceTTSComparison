#!/usr/bin/env python3
"""
Automated Chatterbox Pipeline Script

This script runs the complete Chatterbox integration pipeline:
1. Validates Chatterbox installation and basic functionality
2. Generates voice profiles from audio_samples/
3. Runs benchmarks for Chatterbox model
4. Generates reports

Usage:
    python run_chatterbox_pipeline.py [--skip-validation] [--skip-voices] [--skip-benchmark]
"""

import argparse
import subprocess
import sys
import logging
from pathlib import Path
import os

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('chatterbox_pipeline.log', encoding='utf-8')
        ]
    )
    return logging.getLogger(__name__)

def run_command(cmd, cwd=None, check=True):
    """Run a command and return the result."""
    logger = logging.getLogger(__name__)
    logger.info(f"Running: {cmd}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=check
        )
        
        if result.stdout:
            logger.info(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            logger.warning(f"STDERR:\n{result.stderr}")
            
        return result
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with exit code {e.returncode}")
        logger.error(f"STDOUT: {e.stdout}")
        logger.error(f"STDERR: {e.stderr}")
        raise

def validate_chatterbox():
    """Validate Chatterbox installation and basic functionality."""
    logger = logging.getLogger(__name__)
    logger.info("Validating Chatterbox installation...")
    
    # Use the specific Python executable from venv_chatterbox311
    python_exe = "venv_chatterbox311\\Scripts\\python.exe"
    
    # Test import
    result = run_command(f'{python_exe} -c "import chatterbox; print(\\"Chatterbox import successful\\")"')
    
    # Run the test script
    logger.info("Running Chatterbox test script...")
    result = run_command(f"{python_exe} test_chatterbox.py")
    
    logger.info("Chatterbox validation completed successfully!")
    return True

def generate_voice_profiles():
    """Generate voice profiles from audio samples."""
    logger = logging.getLogger(__name__)
    logger.info("Generating voice profiles from audio samples...")
    
    python_exe = "venv_chatterbox311\\Scripts\\python.exe"
    
    # Create output directory
    output_dir = Path("custom_output/chatterbox_voices")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Run voice profile generation
    cmd = f"{python_exe} tools/chatterbox_make_voices.py --input-dir audio_samples --output-dir custom_output/chatterbox_voices --device auto --exaggeration 0.5"
    result = run_command(cmd)
    
    # List generated profiles
    profiles = list(output_dir.glob("*.conds.pt"))
    logger.info(f"Generated {len(profiles)} voice profiles:")
    for profile in profiles:
        logger.info(f"  - {profile.name}")
    
    return profiles

def run_benchmark():
    """Run benchmark for Chatterbox model."""
    logger = logging.getLogger(__name__)
    logger.info("Running Chatterbox benchmark...")
    
    python_exe = "venv_chatterbox311\\Scripts\\python.exe"
    
    # Create results directory
    results_dir = Path("results_chatterbox")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Run benchmark
    cmd = f"{python_exe} benchmark/run_all_tests.py --models chatterbox --output-dir results_chatterbox"
    result = run_command(cmd)
    
    # List generated files
    result_files = list(results_dir.glob("*"))
    logger.info(f"Benchmark completed! Generated {len(result_files)} result files:")
    for file in result_files:
        logger.info(f"  - {file.name}")
    
    return result_files

def test_voice_profile_synthesis():
    """Test synthesis with a generated voice profile."""
    logger = logging.getLogger(__name__)
    logger.info("Testing voice profile synthesis...")
    
    python_exe = "venv_chatterbox311\\Scripts\\python.exe"
    
    # Find a voice profile to test
    voice_profiles = list(Path("custom_output/chatterbox_voices").glob("*.conds.pt"))
    if not voice_profiles:
        logger.warning("No voice profiles found, skipping synthesis test")
        return
    
    test_profile = voice_profiles[0]
    logger.info(f"Testing with profile: {test_profile.name}")
    
    # Create a simple test script
    test_script = f'''
import sys
sys.path.append("models")
from model_wrappers import ChatterboxWrapper
import soundfile as sf

# Load wrapper
wrapper = ChatterboxWrapper()
if not wrapper.load_model():
    print("Failed to load Chatterbox model")
    sys.exit(1)

# Test synthesis with voice profile
text = "Hello, this is a test of voice cloning with a custom voice profile."
audio = wrapper.synthesize(text, conds_path="{test_profile}")

# Save output
output_path = "custom_output/voice_profile_test.wav"
sf.write(output_path, audio, 22050)
print(f"Voice profile synthesis test completed! Output saved to: {{output_path}}")
print(f"Audio length: {{len(audio)}} samples @ 22050 Hz")
'''
    
    # Write and run test script
    test_file = Path("temp_voice_test.py")
    test_file.write_text(test_script)
    
    try:
        result = run_command(f"{python_exe} temp_voice_test.py")
        logger.info("Voice profile synthesis test completed successfully!")
    finally:
        # Clean up
        if test_file.exists():
            test_file.unlink()

def main():
    parser = argparse.ArgumentParser(description="Run complete Chatterbox integration pipeline")
    parser.add_argument("--skip-validation", action="store_true", help="Skip Chatterbox validation")
    parser.add_argument("--skip-voices", action="store_true", help="Skip voice profile generation")
    parser.add_argument("--skip-benchmark", action="store_true", help="Skip benchmark execution")
    parser.add_argument("--skip-voice-test", action="store_true", help="Skip voice profile synthesis test")
    
    args = parser.parse_args()
    
    logger = setup_logging()
    logger.info("Starting Chatterbox integration pipeline...")
    
    try:
        # Step 1: Validation
        if not args.skip_validation:
            validate_chatterbox()
        else:
            logger.info("Skipping validation (--skip-validation)")
        
        # Step 2: Generate voice profiles
        if not args.skip_voices:
            profiles = generate_voice_profiles()
        else:
            logger.info("Skipping voice profile generation (--skip-voices)")
            profiles = list(Path("custom_output/chatterbox_voices").glob("*.conds.pt"))
        
        # Step 3: Test voice profile synthesis
        if not args.skip_voice_test and profiles:
            test_voice_profile_synthesis()
        else:
            logger.info("Skipping voice profile synthesis test")
        
        # Step 4: Run benchmark
        if not args.skip_benchmark:
            result_files = run_benchmark()
        else:
            logger.info("Skipping benchmark (--skip-benchmark)")
        
        logger.info("Chatterbox integration pipeline completed successfully!")
        logger.info("Check the following directories for outputs:")
        logger.info("  - custom_output/chatterbox_voices/ - Voice profiles (*.conds.pt)")
        logger.info("  - custom_output/ - Test synthesis outputs")
        logger.info("  - results_chatterbox/ - Benchmark results")
        logger.info("  - chatterbox_pipeline.log - Detailed execution log")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
