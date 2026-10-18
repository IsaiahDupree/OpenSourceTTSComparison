#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direct installation and test - simpler approach.
Tests if we can install TTS directly without Docker.
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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def log(message, level="INFO"):
    """Log message."""
    getattr(logger, level.lower())(message)


def install_tts():
    """Install Coqui TTS."""
    log("=" * 70)
    log("Installing Coqui TTS via pip...")
    log("=" * 70)
    log("This may take 5-30 minutes depending on build requirements...")
    
    start = time.time()
    
    try:
        # Try installation with progress
        process = subprocess.Popen(
            [sys.executable, "-m", "pip", "install", "TTS", "--upgrade"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        last_line = ""
        for line in process.stdout:
            line = line.strip()
            if line and line != last_line:
                # Show meaningful progress
                if any(keyword in line for keyword in ["Downloading", "Installing", "Building", "Successfully", "Requirement"]):
                    if "already satisfied" not in line.lower():
                        log(f"  → {line[:80]}")
                    last_line = line
        
        return_code = process.wait()
        elapsed = time.time() - start
        
        if return_code == 0:
            log(f"✅ Installation completed in {elapsed:.1f} seconds")
            return True
        else:
            log(f"❌ Installation failed after {elapsed:.1f} seconds")
            return False
            
    except Exception as e:
        log(f"❌ Installation error: {e}")
        return False


def test_import():
    """Test that TTS can be imported."""
    log("\n" + "=" * 70)
    log("Testing TTS import...")
    log("=" * 70)
    
    try:
        from TTS.api import TTS
        log("✅ TTS.api imported successfully!")
        return True
    except ImportError as e:
        log(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        log(f"❌ Error: {e}")
        return False


def test_basic_tts():
    """Test basic TTS functionality."""
    log("\n" + "=" * 70)
    log("Testing basic TTS synthesis...")
    log("=" * 70)
    
    try:
        from TTS.api import TTS
        
        log("Loading a simple TTS model...")
        # Use a lightweight model for quick test
        model = TTS("tts_models/en/ljspeech/tacotron2-DDC", gpu=False)
        
        log("Generating speech...")
        start = time.time()
        audio = model.tts("Hello, this is a test of text to speech.")
        elapsed = time.time() - start
        
        log(f"✅ TTS synthesis works! Generated {len(audio)} samples in {elapsed:.2f}s")
        return True
        
    except Exception as e:
        log(f"❌ TTS synthesis failed: {e}")
        import traceback
        log(traceback.format_exc())
        return False


def test_voice_cloning():
    """Test voice cloning with XTTS-v2."""
    log("\n" + "=" * 70)
    log("Testing voice cloning (XTTS-v2)...")
    log("=" * 70)
    log("This will download the XTTS-v2 model (~2GB) on first run...")
    
    try:
        from TTS.api import TTS
        import numpy as np
        import soundfile as sf
        
        # Create test reference audio
        log("Creating test reference audio...")
        duration = 3.0
        sample_rate = 22050
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = 0.3 * np.sin(2 * np.pi * 200 * t) + 0.2 * np.sin(2 * np.pi * 400 * t)
        audio = audio.astype(np.float32)
        ref_path = "test_ref_clone.wav"
        sf.write(ref_path, audio, sample_rate)
        log(f"✅ Created reference: {ref_path}")
        
        # Load XTTS-v2 model
        log("Loading XTTS-v2 model (this may take a while on first run)...")
        model = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
        
        # Test voice cloning
        log("Generating cloned voice...")
        start = time.time()
        output_path = "test_output_clone.wav"
        model.tts_to_file(
            text="Hello, this is a test of voice cloning. Does it work correctly?",
            speaker_wav=ref_path,
            file_path=output_path
        )
        elapsed = time.time() - start
        
        # Verify output
        if Path(output_path).exists():
            size = Path(output_path).stat().st_size
            log(f"✅ Voice cloning works! Generated {output_path} ({size:,} bytes) in {elapsed:.2f}s")
            
            # Cleanup
            Path(ref_path).unlink(missing_ok=True)
            return True
        else:
            log("❌ Output file not created")
            return False
            
    except Exception as e:
        log(f"❌ Voice cloning failed: {e}")
        import traceback
        log(traceback.format_exc())
        return False


def main():
    """Main test function."""
    log("=" * 70)
    log("DIRECT INSTALLATION AND TEST")
    log(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 70)
    
    results = {
        "installation": False,
        "import": False,
        "basic_tts": False,
        "voice_cloning": False
    }
    
    # Step 1: Install
    if install_tts():
        results["installation"] = True
        
        # Step 2: Test import
        if test_import():
            results["import"] = True
            
            # Step 3: Test basic TTS
            if test_basic_tts():
                results["basic_tts"] = True
                
                # Step 4: Test voice cloning
                if test_voice_cloning():
                    results["voice_cloning"] = True
    
    # Summary
    log("\n" + "=" * 70)
    log("TEST SUMMARY")
    log("=" * 70)
    
    passed = sum(results.values())
    total = len(results)
    
    for test, result in results.items():
        status = "✅" if result else "❌"
        log(f"{status} {test}: {result}")
    
    log(f"\nResults: {passed}/{total} tests passed")
    
    if results["voice_cloning"]:
        log("\n🎉 SUCCESS! Voice cloning is working!")
        log("You can now use Coqui TTS for voice cloning.")
    elif results["basic_tts"]:
        log("\n✅ Basic TTS works, but voice cloning needs more setup.")
    elif results["import"]:
        log("\n⚠️  TTS installed but basic functionality needs testing.")
    else:
        log("\n❌ Installation or import failed.")
    
    # Save results
    output_dir = Path("results_voice_cloning")
    output_dir.mkdir(exist_ok=True)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "summary": f"{passed}/{total} tests passed"
    }
    
    report_file = output_dir / "direct_install_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    log(f"\n📊 Report saved: {report_file}")
    
    return results["voice_cloning"]


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        log("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        log(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

