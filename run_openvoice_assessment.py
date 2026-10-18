#!/usr/bin/env python3
"""
OpenVoice Assessment Test Suite
================================
Runs OpenVoice API test and then assesses the generated audio quality.
"""

import os
import sys
import subprocess
from pathlib import Path

def set_env_token():
    """Set HF_TOKEN environment variable if not already set"""
    token = __import__('os').environ['API_KEY']
    if not os.getenv("HF_TOKEN"):
        os.environ["HF_TOKEN"] = token
        print(f"[SETUP] Set HF_TOKEN environment variable")
    else:
        print(f"[SETUP] HF_TOKEN already set")

def run_openvoice_test():
    """Run the OpenVoice API test"""
    print("=" * 70)
    print(" STEP 1: Running OpenVoice API Test")
    print("=" * 70)
    
    result = subprocess.run(
        [sys.executable, "test_openvoice_api.py"],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode != 0:
        print(f"❌ OpenVoice test failed with exit code {result.returncode}")
        return None
    
    # Check if output file was created
    output_file = Path("voice_clone_output/openvoice_cloud_test.wav")
    if output_file.exists():
        print(f"✅ Generated audio: {output_file}")
        return output_file
    else:
        print("❌ Output file not found")
        return None

def run_voice_assessment(generated_audio, reference_audio, text):
    """Run voice quality assessment"""
    print("\n" + "=" * 70)
    print(" STEP 2: Running Voice Quality Assessment")
    print("=" * 70)
    
    result = subprocess.run(
        [
            sys.executable, 
            "assess_voice_quality.py",
            "--ref", str(reference_audio),
            "--gen", str(generated_audio),
            "--text", text
        ],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0

def main():
    print("\n" + "=" * 70)
    print(" OpenVoice Assessment Test Suite")
    print("=" * 70)
    print()
    
    # Setup
    set_env_token()
    
    # Check for reference audio
    ref_voice_path = Path("processed_segments/w4sarAE9h9I_Turn YouTube Transcripts into Effective Content with Make.com_segment_0.wav")
    if not ref_voice_path.exists():
        print(f"❌ Reference file not found: {ref_voice_path}")
        print("Please run 'python expand_dataset.py --limit 5 --process' first.")
        sys.exit(1)
    
    # Expected text (must match what we send to OpenVoice)
    expected_text = "This is a test of OpenVoice V2 running on the Hugging Face cloud. We are comparing it to our local Docker solution."
    
    # Step 1: Run OpenVoice test
    generated_audio = run_openvoice_test()
    
    if not generated_audio:
        print("\n❌ Cannot proceed with assessment - OpenVoice test failed")
        sys.exit(1)
    
    # Step 2: Run assessment
    success = run_voice_assessment(generated_audio, ref_voice_path, expected_text)
    
    # Summary
    print("\n" + "=" * 70)
    print(" ASSESSMENT SUMMARY")
    print("=" * 70)
    if success:
        print("✅ Assessment completed successfully")
    else:
        print("⚠️ Assessment completed with warnings (check output above)")
    
    print(f"\nGenerated Audio: {generated_audio}")
    print(f"Reference Audio: {ref_voice_path}")
    print("=" * 70)

if __name__ == "__main__":
    main()

