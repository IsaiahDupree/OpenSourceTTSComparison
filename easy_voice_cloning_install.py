#!/usr/bin/env python3
"""
Easy Voice Cloning Installer
============================
One-click installer with console logging, timeouts, and automatic fallbacks.

Features:
- Real-time console progress with timestamps
- Per-step timeouts to prevent hanging
- Automatic GPU/CPU detection
- Fallback chain: Chatterbox → XTTS → Docker XTTS → pyttsx3
- Rich progress indicators
- Automatic error recovery

Usage:
    python easy_voice_cloning_install.py
    python easy_voice_cloning_install.py --prefer xtts
    python easy_voice_cloning_install.py --prefer chatterbox
    python easy_voice_cloning_install.py --docker-only
"""

import sys
import os
import subprocess
import time
import argparse
import importlib
import threading
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, Dict, Any, Callable

# ============================================================================
# CONFIGURATION
# ============================================================================

TIMEOUTS = {
    "pip_install": 600,      # 10 minutes for pip install
    "model_download": 900,   # 15 minutes for model download
    "test_synthesis": 120,   # 2 minutes for test synthesis
    "docker_pull": 900,      # 15 minutes for docker pull
    "docker_test": 120,      # 2 minutes for docker test
}

TEST_TEXT = "Hello! This is a voice cloning test. The quick brown fox jumps over the lazy dog."
OUTPUT_DIR = Path("easy_install_output")
LOG_FILE = Path("easy_install.log")

# ============================================================================
# LOGGING UTILITIES
# ============================================================================

class ConsoleLogger:
    """Rich console logging with colors and timestamps."""
    
    COLORS = {
        "reset": "\033[0m",
        "bold": "\033[1m",
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
    }
    
    def __init__(self, log_file: Path = LOG_FILE):
        self.log_file = log_file
        self.start_time = time.time()
        self._setup_encoding()
        
    def _setup_encoding(self):
        """Fix Windows console encoding."""
        if sys.platform == "win32":
            try:
                sys.stdout.reconfigure(encoding='utf-8', errors='replace')
                sys.stderr.reconfigure(encoding='utf-8', errors='replace')
            except:
                pass
    
    def _timestamp(self) -> str:
        return datetime.now().strftime("%H:%M:%S")
    
    def _elapsed(self) -> str:
        elapsed = time.time() - self.start_time
        mins, secs = divmod(int(elapsed), 60)
        return f"{mins:02d}:{secs:02d}"
    
    def _colorize(self, text: str, color: str) -> str:
        if sys.platform == "win32":
            # Enable ANSI on Windows
            os.system("")
        return f"{self.COLORS.get(color, '')}{text}{self.COLORS['reset']}"
    
    def _log_to_file(self, message: str):
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"{datetime.now().isoformat()} | {message}\n")
        except:
            pass
    
    def header(self, text: str):
        border = "=" * 70
        msg = f"\n{border}\n{text}\n{border}"
        print(self._colorize(msg, "cyan"))
        self._log_to_file(msg)
    
    def step(self, step_num: int, total: int, text: str):
        prefix = f"[{self._timestamp()}] [{self._elapsed()}]"
        step_info = f"[{step_num}/{total}]"
        msg = f"{prefix} {self._colorize(step_info, 'magenta')} {text}"
        print(msg)
        self._log_to_file(f"STEP {step_num}/{total}: {text}")
    
    def info(self, text: str):
        prefix = f"[{self._timestamp()}] [{self._elapsed()}]"
        print(f"{prefix} {self._colorize('[INFO]', 'blue')} {text}")
        self._log_to_file(f"INFO: {text}")
    
    def success(self, text: str):
        prefix = f"[{self._timestamp()}] [{self._elapsed()}]"
        print(f"{prefix} {self._colorize('[OK]', 'green')} {text}")
        self._log_to_file(f"SUCCESS: {text}")
    
    def warning(self, text: str):
        prefix = f"[{self._timestamp()}] [{self._elapsed()}]"
        print(f"{prefix} {self._colorize('[WARN]', 'yellow')} {text}")
        self._log_to_file(f"WARNING: {text}")
    
    def error(self, text: str):
        prefix = f"[{self._timestamp()}] [{self._elapsed()}]"
        print(f"{prefix} {self._colorize('[ERROR]', 'red')} {text}")
        self._log_to_file(f"ERROR: {text}")
    
    def progress(self, current: int, total: int, text: str = ""):
        percent = (current / total) * 100
        bar_len = 30
        filled = int(bar_len * current / total)
        bar = "█" * filled + "░" * (bar_len - filled)
        msg = f"\r[{self._timestamp()}] [{bar}] {percent:5.1f}% {text}"
        print(msg, end="", flush=True)
        if current >= total:
            print()  # New line when complete

log = ConsoleLogger()

# ============================================================================
# TIMEOUT UTILITIES
# ============================================================================

class TimeoutError(Exception):
    pass

def run_with_timeout(func: Callable, timeout: int, description: str) -> Tuple[bool, Any]:
    """Run a function with timeout. Returns (success, result_or_error)."""
    result = [None]
    error = [None]
    completed = threading.Event()
    
    def wrapper():
        try:
            result[0] = func()
        except Exception as e:
            error[0] = e
        finally:
            completed.set()
    
    thread = threading.Thread(target=wrapper, daemon=True)
    thread.start()
    
    # Wait with progress updates
    start = time.time()
    while not completed.is_set():
        elapsed = time.time() - start
        if elapsed > timeout:
            log.error(f"Timeout after {timeout}s: {description}")
            return False, TimeoutError(f"Timeout after {timeout}s")
        
        remaining = timeout - elapsed
        log.info(f"{description}... ({int(elapsed)}s elapsed, {int(remaining)}s remaining)")
        completed.wait(timeout=10)  # Update every 10 seconds
    
    if error[0]:
        return False, error[0]
    return True, result[0]

def run_command_with_timeout(cmd: list, timeout: int, description: str, 
                              capture_output: bool = True) -> Tuple[bool, str]:
    """Run a subprocess command with timeout."""
    log.info(f"Running: {' '.join(cmd[:3])}...")
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE if capture_output else None,
            stderr=subprocess.STDOUT if capture_output else None,
            text=True,
            errors='replace'
        )
        
        output_lines = []
        start = time.time()
        
        while True:
            # Check timeout
            elapsed = time.time() - start
            if elapsed > timeout:
                process.kill()
                log.error(f"Timeout after {timeout}s: {description}")
                return False, f"Timeout after {timeout}s"
            
            # Read output
            if capture_output and process.stdout:
                line = process.stdout.readline()
                if line:
                    output_lines.append(line.rstrip())
                    # Show important lines
                    if any(kw in line.lower() for kw in ['downloading', 'installing', 'error', 'success', 'complete']):
                        log.info(f"  > {line.rstrip()[:80]}")
            
            # Check if process finished
            if process.poll() is not None:
                break
            
            time.sleep(0.1)
        
        # Get remaining output
        if capture_output and process.stdout:
            remaining = process.stdout.read()
            if remaining:
                output_lines.extend(remaining.split('\n'))
        
        output = '\n'.join(output_lines)
        
        if process.returncode == 0:
            log.success(f"{description} completed")
            return True, output
        else:
            log.error(f"{description} failed with code {process.returncode}")
            return False, output
            
    except Exception as e:
        log.error(f"{description} exception: {e}")
        return False, str(e)

# ============================================================================
# SYSTEM DETECTION
# ============================================================================

def detect_gpu() -> Dict[str, Any]:
    """Detect GPU availability."""
    log.info("Detecting GPU...")
    
    result = {
        "cuda_available": False,
        "gpu_name": None,
        "gpu_memory_gb": 0,
        "recommendation": "cpu"
    }
    
    try:
        import torch
        result["cuda_available"] = torch.cuda.is_available()
        if result["cuda_available"]:
            result["gpu_name"] = torch.cuda.get_device_name(0)
            result["gpu_memory_gb"] = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            result["recommendation"] = "cuda"
            log.success(f"GPU detected: {result['gpu_name']} ({result['gpu_memory_gb']:.1f} GB)")
        else:
            log.info("No CUDA GPU detected, will use CPU")
    except ImportError:
        log.info("PyTorch not installed yet, GPU detection deferred")
    except Exception as e:
        log.warning(f"GPU detection error: {e}")
    
    return result

def check_docker() -> bool:
    """Check if Docker is available."""
    log.info("Checking Docker availability...")
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            log.success(f"Docker available: {result.stdout.strip()}")
            return True
    except:
        pass
    log.info("Docker not available")
    return False

# ============================================================================
# INSTALLATION METHODS
# ============================================================================

def install_chatterbox() -> Tuple[bool, str]:
    """Install Chatterbox TTS."""
    log.header("INSTALLING CHATTERBOX")
    
    # Step 1: Install package
    log.step(1, 3, "Installing chatterbox package...")
    success, output = run_command_with_timeout(
        [sys.executable, "-m", "pip", "install", "chatterbox-tts", "--upgrade"],
        TIMEOUTS["pip_install"],
        "Chatterbox installation"
    )
    
    if not success:
        # Try alternative package name
        log.warning("Trying alternative package name...")
        success, output = run_command_with_timeout(
            [sys.executable, "-m", "pip", "install", "chatterbox", "--upgrade"],
            TIMEOUTS["pip_install"],
            "Chatterbox installation (alt)"
        )
    
    if not success:
        return False, f"Installation failed: {output}"
    
    # Step 2: Verify import
    log.step(2, 3, "Verifying installation...")
    try:
        import chatterbox
        log.success("Chatterbox imported successfully")
    except ImportError as e:
        return False, f"Import failed: {e}"
    
    # Step 3: Test synthesis
    log.step(3, 3, "Testing voice synthesis...")
    OUTPUT_DIR.mkdir(exist_ok=True)
    output_file = OUTPUT_DIR / "chatterbox_test.wav"
    
    def test_synthesis():
        import chatterbox
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        log.info(f"Using device: {device}")
        
        tts = chatterbox.ChatterboxTTS.from_pretrained(device)
        log.info("Model loaded, generating audio...")
        
        audio = tts.generate(TEST_TEXT)
        
        # Save audio
        import torchaudio
        torchaudio.save(str(output_file), audio.unsqueeze(0).cpu(), 24000)
        return str(output_file)
    
    success, result = run_with_timeout(
        test_synthesis,
        TIMEOUTS["test_synthesis"] + TIMEOUTS["model_download"],  # Include model download time
        "Chatterbox test synthesis"
    )
    
    if success and output_file.exists():
        log.success(f"Audio saved to: {output_file}")
        return True, str(output_file)
    else:
        return False, f"Synthesis failed: {result}"


def install_coqui_xtts() -> Tuple[bool, str]:
    """Install Coqui TTS with XTTS-v2."""
    log.header("INSTALLING COQUI TTS (XTTS-v2)")
    
    # Step 1: Install package
    log.step(1, 3, "Installing TTS package...")
    success, output = run_command_with_timeout(
        [sys.executable, "-m", "pip", "install", "TTS", "--upgrade"],
        TIMEOUTS["pip_install"],
        "Coqui TTS installation"
    )
    
    if not success:
        return False, f"Installation failed: {output}"
    
    # Step 2: Verify import
    log.step(2, 3, "Verifying installation...")
    try:
        from TTS.api import TTS
        log.success("TTS imported successfully")
    except ImportError as e:
        return False, f"Import failed: {e}"
    
    # Step 3: Test synthesis with XTTS
    log.step(3, 3, "Testing XTTS voice synthesis...")
    OUTPUT_DIR.mkdir(exist_ok=True)
    output_file = OUTPUT_DIR / "xtts_test.wav"
    
    def test_synthesis():
        from TTS.api import TTS
        import torch
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        log.info(f"Using device: {device}")
        
        # Use XTTS-v2 for voice cloning
        log.info("Loading XTTS-v2 model (this may take a few minutes on first run)...")
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        
        log.info("Model loaded, generating audio...")
        
        # For voice cloning, we need a reference audio
        # First, try basic synthesis
        tts.tts_to_file(
            text=TEST_TEXT,
            file_path=str(output_file),
            language="en"
        )
        return str(output_file)
    
    success, result = run_with_timeout(
        test_synthesis,
        TIMEOUTS["test_synthesis"] + TIMEOUTS["model_download"],
        "XTTS test synthesis"
    )
    
    if success and output_file.exists():
        log.success(f"Audio saved to: {output_file}")
        return True, str(output_file)
    else:
        return False, f"Synthesis failed: {result}"


def install_docker_xtts() -> Tuple[bool, str]:
    """Install XTTS via Docker (zero build issues)."""
    log.header("INSTALLING COQUI TTS VIA DOCKER")
    
    if not check_docker():
        return False, "Docker not available"
    
    # Step 1: Pull Docker image
    log.step(1, 3, "Pulling Coqui TTS Docker image...")
    success, output = run_command_with_timeout(
        ["docker", "pull", "ghcr.io/coqui-ai/tts:latest"],
        TIMEOUTS["docker_pull"],
        "Docker image pull"
    )
    
    if not success:
        # Try alternative image
        log.warning("Trying alternative Docker image...")
        success, output = run_command_with_timeout(
            ["docker", "pull", "coqui/tts:latest"],
            TIMEOUTS["docker_pull"],
            "Docker image pull (alt)"
        )
    
    if not success:
        return False, f"Docker pull failed: {output}"
    
    # Step 2: Test the image
    log.step(2, 3, "Testing Docker image...")
    success, output = run_command_with_timeout(
        ["docker", "run", "--rm", "ghcr.io/coqui-ai/tts:latest", 
         "python", "-c", "from TTS.api import TTS; print('TTS Ready!')"],
        TIMEOUTS["docker_test"],
        "Docker TTS test"
    )
    
    if not success:
        return False, f"Docker test failed: {output}"
    
    # Step 3: Create helper script
    log.step(3, 3, "Creating Docker helper script...")
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    helper_script = OUTPUT_DIR / "docker_tts.py"
    helper_content = '''#!/usr/bin/env python3
"""Docker-based TTS helper for voice cloning."""
import subprocess
import sys
from pathlib import Path

def synthesize(text: str, output_file: str, voice_sample: str = None):
    """Synthesize speech using Docker Coqui TTS."""
    output_path = Path(output_file).absolute()
    output_dir = output_path.parent
    
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{output_dir}:/output",
        "ghcr.io/coqui-ai/tts:latest",
        "--text", text,
        "--out_path", f"/output/{output_path.name}"
    ]
    
    if voice_sample:
        sample_path = Path(voice_sample).absolute()
        cmd.extend(["-v", f"{sample_path.parent}:/samples"])
        cmd.extend(["--speaker_wav", f"/samples/{sample_path.name}"])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stdout + result.stderr

if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else "Hello, this is a Docker TTS test."
    output = sys.argv[2] if len(sys.argv) > 2 else "docker_output.wav"
    success, msg = synthesize(text, output)
    print(f"{'Success' if success else 'Failed'}: {msg}")
'''
    helper_script.write_text(helper_content)
    log.success(f"Helper script created: {helper_script}")
    
    return True, str(helper_script)


def install_pyttsx3_fallback() -> Tuple[bool, str]:
    """Install pyttsx3 as last resort (no voice cloning, but works everywhere)."""
    log.header("INSTALLING PYTTSX3 (FALLBACK)")
    log.warning("Note: pyttsx3 does NOT support voice cloning, only basic TTS")
    
    # Step 1: Install package
    log.step(1, 2, "Installing pyttsx3...")
    success, output = run_command_with_timeout(
        [sys.executable, "-m", "pip", "install", "pyttsx3"],
        TIMEOUTS["pip_install"],
        "pyttsx3 installation"
    )
    
    if not success:
        return False, f"Installation failed: {output}"
    
    # Step 2: Test
    log.step(2, 2, "Testing pyttsx3...")
    try:
        import pyttsx3
        engine = pyttsx3.init()
        
        OUTPUT_DIR.mkdir(exist_ok=True)
        output_file = OUTPUT_DIR / "pyttsx3_test.wav"
        
        engine.save_to_file(TEST_TEXT, str(output_file))
        engine.runAndWait()
        
        if output_file.exists():
            log.success(f"Audio saved to: {output_file}")
            return True, str(output_file)
        else:
            return False, "Output file not created"
    except Exception as e:
        return False, f"Test failed: {e}"


# ============================================================================
# MAIN INSTALLATION WORKFLOW
# ============================================================================

def run_installation(prefer: str = None, docker_only: bool = False) -> Dict[str, Any]:
    """Run the installation workflow with fallbacks."""
    
    log.header("EASY VOICE CLONING INSTALLER")
    log.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.info(f"Output directory: {OUTPUT_DIR.absolute()}")
    log.info(f"Log file: {LOG_FILE.absolute()}")
    
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Detect system capabilities
    gpu_info = detect_gpu()
    docker_available = check_docker()
    
    results = {
        "gpu_info": gpu_info,
        "docker_available": docker_available,
        "installations": {},
        "working_solution": None,
        "output_file": None
    }
    
    # Define installation order based on preferences
    if docker_only:
        install_order = [("docker_xtts", install_docker_xtts)]
    elif prefer == "chatterbox":
        install_order = [
            ("chatterbox", install_chatterbox),
            ("coqui_xtts", install_coqui_xtts),
            ("docker_xtts", install_docker_xtts),
            ("pyttsx3", install_pyttsx3_fallback),
        ]
    elif prefer == "xtts":
        install_order = [
            ("coqui_xtts", install_coqui_xtts),
            ("chatterbox", install_chatterbox),
            ("docker_xtts", install_docker_xtts),
            ("pyttsx3", install_pyttsx3_fallback),
        ]
    else:
        # Default: try most likely to work first
        install_order = [
            ("chatterbox", install_chatterbox),
            ("coqui_xtts", install_coqui_xtts),
            ("docker_xtts", install_docker_xtts),
            ("pyttsx3", install_pyttsx3_fallback),
        ]
    
    # Try each installation method
    for name, install_func in install_order:
        log.info(f"\n{'='*50}")
        log.info(f"Attempting: {name.upper()}")
        log.info(f"{'='*50}\n")
        
        try:
            success, output = install_func()
            results["installations"][name] = {
                "success": success,
                "output": output
            }
            
            if success:
                results["working_solution"] = name
                results["output_file"] = output
                log.success(f"\n{'='*50}")
                log.success(f"SUCCESS! {name.upper()} is working!")
                log.success(f"{'='*50}\n")
                break
            else:
                log.warning(f"{name} failed, trying next option...")
                
        except Exception as e:
            log.error(f"Exception during {name}: {e}")
            results["installations"][name] = {
                "success": False,
                "output": str(e)
            }
    
    return results


def print_summary(results: Dict[str, Any]):
    """Print installation summary."""
    log.header("INSTALLATION SUMMARY")
    
    if results["working_solution"]:
        log.success(f"Working solution: {results['working_solution'].upper()}")
        log.success(f"Output file: {results['output_file']}")
        
        print(f"\n{'-'*50}")
        print("NEXT STEPS:")
        print(f"{'-'*50}")
        
        if results["working_solution"] == "chatterbox":
            print("""
To use Chatterbox for voice cloning:

    import chatterbox
    import torch
    import torchaudio
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tts = chatterbox.ChatterboxTTS.from_pretrained(device)
    
    # Basic TTS
    audio = tts.generate("Your text here")
    
    # Voice cloning (with reference audio)
    audio = tts.generate("Your text here", audio_prompt_path="reference.wav")
    
    # Save audio
    torchaudio.save("output.wav", audio.unsqueeze(0).cpu(), 24000)
""")
        elif results["working_solution"] == "coqui_xtts":
            print("""
To use XTTS-v2 for voice cloning:

    from TTS.api import TTS
    
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    
    # Voice cloning (only needs 6 seconds of reference audio!)
    tts.tts_to_file(
        text="Your text here",
        file_path="output.wav",
        speaker_wav="reference.wav",  # Your voice sample
        language="en"
    )
""")
        elif results["working_solution"] == "docker_xtts":
            print(f"""
To use Docker TTS:

    python {results['output_file']} "Your text here" output.wav
    
Or use Docker directly:

    docker run --rm -v $PWD:/output ghcr.io/coqui-ai/tts:latest \\
        --text "Your text here" --out_path /output/output.wav
""")
        elif results["working_solution"] == "pyttsx3":
            print("""
Note: pyttsx3 does NOT support voice cloning, only basic TTS.

    import pyttsx3
    engine = pyttsx3.init()
    engine.save_to_file("Your text here", "output.wav")
    engine.runAndWait()

For voice cloning, please try installing Chatterbox or XTTS manually.
""")
    else:
        log.error("No working solution found!")
        print("\nTroubleshooting suggestions:")
        print("1. Try installing with Docker: python easy_voice_cloning_install.py --docker-only")
        print("2. Check the log file for errors: easy_install.log")
        print("3. Install Visual C++ Build Tools for Windows")
        print("4. Try in a fresh virtual environment")
    
    # Save results to JSON
    results_file = OUTPUT_DIR / "installation_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)
    log.info(f"Results saved to: {results_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Easy Voice Cloning Installer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python easy_voice_cloning_install.py              # Auto-detect best option
    python easy_voice_cloning_install.py --prefer xtts    # Try XTTS first
    python easy_voice_cloning_install.py --prefer chatterbox  # Try Chatterbox first
    python easy_voice_cloning_install.py --docker-only    # Only use Docker
        """
    )
    parser.add_argument(
        "--prefer", 
        choices=["chatterbox", "xtts"],
        help="Preferred installation method"
    )
    parser.add_argument(
        "--docker-only",
        action="store_true",
        help="Only try Docker installation (zero build issues)"
    )
    
    args = parser.parse_args()
    
    try:
        results = run_installation(
            prefer=args.prefer,
            docker_only=args.docker_only
        )
        print_summary(results)
        
        # Exit with appropriate code
        sys.exit(0 if results["working_solution"] else 1)
        
    except KeyboardInterrupt:
        log.warning("\nInstallation interrupted by user")
        sys.exit(130)
    except Exception as e:
        log.error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
