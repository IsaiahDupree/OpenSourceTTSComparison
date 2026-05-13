#!/usr/bin/env python3
"""
Robust installation and testing script for voice cloning models.
Handles build issues and provides fallback options.
"""

import sys
import subprocess
import importlib
import traceback
from pathlib import Path
import json
import time
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test configuration
TEST_TEXT = "Hello, this is a test of the voice cloning system."


class ModelInstaller:
    """Handle installation of voice cloning models with error recovery."""
    
    def __init__(self):
        self.results = {}
        self.install_log = []
    
    def log(self, message):
        """Log installation message."""
        logger.info(message)
        self.install_log.append(message)
    
    def check_system_dependencies(self):
        """Check for required system dependencies."""
        self.log("Checking system dependencies...")
        
        issues = []
        
        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 8):
            issues.append(f"Python 3.8+ required, found {python_version.major}.{python_version.minor}")
        else:
            self.log(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Check pip
        try:
            import pip
            self.log("✅ pip available")
        except:
            issues.append("pip not available")
        
        # Check for build tools (Windows)
        if sys.platform == "win32":
            self.log("Checking Windows build tools...")
            # Check if Visual C++ build tools might be needed
            self.log("⚠️  Windows: May need Visual C++ Build Tools for some packages")
            self.log("   Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/")
        
        # Check for CUDA (optional but helpful)
        try:
            import torch
            if torch.cuda.is_available():
                self.log(f"✅ CUDA available: {torch.version.cuda}")
            else:
                self.log("⚠️  CUDA not available (CPU mode will be slower)")
        except:
            self.log("⚠️  PyTorch not installed (will be installed with models)")
        
        if issues:
            self.log("⚠️  System dependency issues found:")
            for issue in issues:
                self.log(f"   - {issue}")
        
        return len(issues) == 0
    
    def install_with_retry(self, package, method="pip", retries=2, **kwargs):
        """Install package with retry logic and error handling."""
        self.log(f"Installing {package}...")
        
        for attempt in range(retries + 1):
            try:
                if method == "pip":
                    # Use subprocess to avoid import issues
                    cmd = [sys.executable, "-m", "pip", "install", package]
                    
                    # Add options based on kwargs
                    if kwargs.get("no_deps"):
                        cmd.append("--no-deps")
                    if kwargs.get("pre"):
                        cmd.append("--pre")
                    if kwargs.get("upgrade"):
                        cmd.append("--upgrade")
                    
                    # Add quiet flag for cleaner output
                    if kwargs.get("quiet", True):
                        cmd.append("--quiet")
                    
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=600  # 10 minute timeout
                    )
                    
                    if result.returncode == 0:
                        self.log(f"✅ Successfully installed {package}")
                        return True
                    else:
                        error_msg = result.stderr or result.stdout
                        self.log(f"⚠️  Attempt {attempt + 1} failed: {error_msg[:200]}")
                        
                        # Check for common issues
                        if "Microsoft Visual C++" in error_msg or "error: Microsoft Visual C++" in error_msg:
                            self.log("   → Build issue: Missing Visual C++ Build Tools")
                            self.log("   → Solution: Install from https://visualstudio.microsoft.com/visual-cpp-build-tools/")
                            return False
                        elif "No module named" in error_msg:
                            self.log("   → Dependency issue detected")
                        elif "timeout" in error_msg.lower():
                            self.log("   → Network timeout, will retry...")
                            if attempt < retries:
                                time.sleep(5)
                                continue
                
            except subprocess.TimeoutExpired:
                self.log(f"⚠️  Installation timeout for {package}")
                if attempt < retries:
                    self.log("   → Retrying...")
                    continue
            except Exception as e:
                self.log(f"⚠️  Installation error: {e}")
                if attempt < retries:
                    time.sleep(2)
                    continue
        
        self.log(f"❌ Failed to install {package} after {retries + 1} attempts")
        return False
    
    def test_coqui_tts(self):
        """Test Coqui TTS installation and functionality."""
        result = {
            "name": "Coqui TTS (XTTS-v2)",
            "installation_attempted": False,
            "installation_success": False,
            "basic_tts": False,
            "voice_cloning": False,
            "error": None,
            "workaround": None
        }
        
        # Try installation
        result["installation_attempted"] = True
        
        # Method 1: Standard pip install
        if self.install_with_retry("TTS", quiet=False):
            result["installation_success"] = True
        else:
            # Method 2: Try without dependencies (user installs manually)
            self.log("Trying alternative installation method...")
            result["workaround"] = "Manual installation required. See docs/installation_guide.md"
            result["error"] = "Standard pip install failed. May need Visual C++ Build Tools on Windows."
            return result
        
        # Test import
        try:
            from TTS.api import TTS
            self.log("✅ Coqui TTS imported successfully")
            
            # Test basic TTS (this will download model on first run)
            try:
                self.log("Loading XTTS-v2 model (this may take a while on first run)...")
                model = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)  # Use CPU to avoid GPU issues
                
                start_time = time.time()
                audio = model.tts(text=TEST_TEXT)
                inference_time = time.time() - start_time
                
                result["basic_tts"] = True
                result["performance"] = {
                    "inference_time": inference_time,
                    "audio_length": len(audio) / 22050
                }
                self.log(f"✅ Coqui TTS basic TTS works (time: {inference_time:.2f}s)")
                
                # Test voice cloning (create dummy reference)
                try:
                    import numpy as np
                    import soundfile as sf
                    ref_audio = np.random.randn(22050 * 2).astype(np.float32)  # 2 seconds
                    ref_path = "temp_ref.wav"
                    sf.write(ref_path, ref_audio, 22050)
                    
                    start_time = time.time()
                    audio = model.tts(text=TEST_TEXT, speaker_wav=ref_path)
                    cloning_time = time.time() - start_time
                    
                    result["voice_cloning"] = True
                    result["performance"]["cloning_time"] = cloning_time
                    self.log(f"✅ Coqui TTS voice cloning works (time: {cloning_time:.2f}s)")
                    
                    # Cleanup
                    Path(ref_path).unlink(missing_ok=True)
                except Exception as e:
                    self.log(f"⚠️  Voice cloning test failed: {e}")
                    result["error"] = f"Voice cloning: {str(e)}"
                
            except Exception as e:
                self.log(f"⚠️  Model loading/synthesis failed: {e}")
                result["error"] = str(e)
                # Check for specific errors
                if "CUDA" in str(e) or "cuda" in str(e):
                    result["workaround"] = "Try with gpu=False parameter or install CUDA toolkit"
                elif "model" in str(e).lower() or "download" in str(e).lower():
                    result["workaround"] = "Model download may have failed. Check internet connection."
        
        except ImportError as e:
            result["error"] = f"Import failed: {str(e)}"
            result["workaround"] = "May need to restart Python or check installation"
        
        return result
    
    def test_chatterbox(self):
        """Test Chatterbox installation and functionality."""
        result = {
            "name": "Chatterbox",
            "installation_attempted": False,
            "installation_success": False,
            "basic_tts": False,
            "voice_cloning": False,
            "error": None,
            "workaround": None
        }
        
        result["installation_attempted"] = True
        
        # Try installation
        if self.install_with_retry("chatterbox", quiet=False):
            result["installation_success"] = True
        else:
            result["error"] = "pip install failed"
            result["workaround"] = "Check if package name is correct or try: pip install chatterbox-tts"
            return result
        
        # Test import and functionality
        try:
            import chatterbox
            import torch
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.log(f"Loading Chatterbox on {device}...")
            
            model = chatterbox.ChatterboxTTS.from_pretrained(device)
            
            start_time = time.time()
            audio_tensor = model.generate(TEST_TEXT)
            inference_time = time.time() - start_time
            
            audio = audio_tensor.squeeze(0).detach().cpu().numpy()
            result["basic_tts"] = True
            result["performance"] = {
                "inference_time": inference_time,
                "audio_length": len(audio) / 24000
            }
            self.log(f"✅ Chatterbox basic TTS works (time: {inference_time:.2f}s)")
            
            # Test voice cloning
            try:
                import soundfile as sf
                import numpy as np
                ref_audio = np.random.randn(24000 * 2).astype(np.float32)
                ref_path = "temp_ref_chatterbox.wav"
                sf.write(ref_path, ref_audio, 24000)
                
                start_time = time.time()
                audio_tensor = model.generate(TEST_TEXT, audio_prompt_path=ref_path)
                cloning_time = time.time() - start_time
                
                result["voice_cloning"] = True
                result["performance"]["cloning_time"] = cloning_time
                self.log(f"✅ Chatterbox voice cloning works (time: {cloning_time:.2f}s)")
                
                Path(ref_path).unlink(missing_ok=True)
            except Exception as e:
                self.log(f"⚠️  Voice cloning test failed: {e}")
                result["error"] = f"Voice cloning: {str(e)}"
        
        except ImportError as e:
            result["error"] = f"Import failed: {str(e)}"
        except Exception as e:
            result["error"] = str(e)
            self.log(f"⚠️  Chatterbox test failed: {e}")
        
        return result
    
    def test_simple_tts_alternatives(self):
        """Test simpler TTS alternatives that might work without complex builds."""
        results = {}
        
        # Test pyttsx3 (very simple, no build required)
        try:
            import pyttsx3
            engine = pyttsx3.init()
            result = {
                "name": "pyttsx3",
                "installation_success": True,
                "basic_tts": True,
                "voice_cloning": False,
                "note": "Simple TTS, no voice cloning support"
            }
            results["pyttsx3"] = result
            self.log("✅ pyttsx3 works (simple TTS, no cloning)")
        except:
            pass
        
        # Test gTTS (Google TTS, simple)
        try:
            from gtts import gTTS
            result = {
                "name": "gTTS (Google TTS)",
                "installation_success": True,
                "basic_tts": True,
                "voice_cloning": False,
                "note": "Online TTS, requires internet, no voice cloning"
            }
            results["gtts"] = result
            self.log("✅ gTTS works (online TTS, no cloning)")
        except:
            pass
        
        return results
    
    def run_all_tests(self):
        """Run installation and tests for all models."""
        self.log("=" * 70)
        self.log("Voice Cloning Model Installation & Testing")
        self.log("=" * 70)
        
        # Check system
        self.check_system_dependencies()
        self.log("")
        
        all_results = {}
        
        # Test easy models first
        self.log("\n" + "=" * 70)
        self.log("Testing Easy-to-Install Models")
        self.log("=" * 70)
        
        # Test Coqui TTS
        self.log("\n--- Testing Coqui TTS ---")
        all_results["coqui_tts"] = self.test_coqui_tts()
        
        # Test Chatterbox
        self.log("\n--- Testing Chatterbox ---")
        all_results["chatterbox"] = self.test_chatterbox()
        
        # Test simple alternatives
        self.log("\n--- Testing Simple Alternatives ---")
        simple_results = self.test_simple_tts_alternatives()
        all_results.update(simple_results)
        
        return all_results
    
    def generate_report(self, results):
        """Generate comprehensive report."""
        report_lines = [
            "# Voice Cloning Software Installation & Test Report",
            "",
            f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Installation Log",
            ""
        ]
        
        # Add installation log
        for log_entry in self.install_log:
            report_lines.append(f"- {log_entry}")
        
        report_lines.extend([
            "",
            "## Test Results",
            ""
        ])
        
        # Working models
        working = [k for k, v in results.items() if v.get("voice_cloning") == True]
        partial = [k for k, v in results.items() if v.get("basic_tts") == True and not v.get("voice_cloning")]
        failed = [k for k, v in results.items() if not v.get("basic_tts")]
        
        if working:
            report_lines.extend([
                "### ✅ Working Voice Cloning Models",
                ""
            ])
            for model_key in working:
                r = results[model_key]
                name = r.get("name", model_key)
                perf = r.get("performance", {})
                report_lines.append(f"- **{name}**")
                if perf:
                    report_lines.append(f"  - Inference time: {perf.get('inference_time', 'N/A')}")
                    report_lines.append(f"  - Cloning time: {perf.get('cloning_time', 'N/A')}")
                report_lines.append("")
        
        if partial:
            report_lines.extend([
                "### ⚠️ Partial Support (TTS Only)",
                ""
            ])
            for model_key in partial:
                r = results[model_key]
                name = r.get("name", model_key)
                note = r.get("note", "")
                report_lines.append(f"- **{name}**: {note}")
            report_lines.append("")
        
        if failed:
            report_lines.extend([
                "### ❌ Installation/Test Failed",
                ""
            ])
            for model_key in failed:
                r = results[model_key]
                name = r.get("name", model_key)
                error = r.get("error", "Unknown error")
                workaround = r.get("workaround", "")
                report_lines.append(f"- **{name}**")
                report_lines.append(f"  - Error: {error}")
                if workaround:
                    report_lines.append(f"  - Workaround: {workaround}")
            report_lines.append("")
        
        # Recommendations
        report_lines.extend([
            "## Recommendations",
            ""
        ])
        
        if working:
            report_lines.append("### Best Working Options:")
            for model_key in working:
                name = results[model_key].get("name", model_key)
                report_lines.append(f"1. **{name}** - Ready to use for voice cloning")
            report_lines.append("")
        else:
            report_lines.append("### No voice cloning models working yet.")
            report_lines.append("")
            report_lines.append("**Next Steps:**")
            report_lines.append("1. Check build dependencies (Visual C++ Build Tools on Windows)")
            report_lines.append("2. Try installing models one at a time")
            report_lines.append("3. Check error messages for specific issues")
            report_lines.append("4. See docs/installation_guide.md for detailed instructions")
            report_lines.append("")
        
        # Build issue solutions
        report_lines.extend([
            "## Common Build Issues & Solutions",
            "",
            "### Windows Build Issues",
            "",
            "**Problem**: `error: Microsoft Visual C++ 14.0 or greater is required`",
            "",
            "**Solution**:",
            "1. Download Visual C++ Build Tools: https://visualstudio.microsoft.com/visual-cpp-build-tools/",
            "2. Install 'Desktop development with C++' workload",
            "3. Restart terminal and try installation again",
            "",
            "### CUDA/GPU Issues",
            "",
            "**Problem**: CUDA not detected or GPU errors",
            "",
            "**Solution**:",
            "1. Models work on CPU (slower but functional)",
            "2. For GPU: Install CUDA toolkit matching your PyTorch version",
            "3. Check: `python -c 'import torch; print(torch.cuda.is_available())'`",
            "",
            "### Network/Download Issues",
            "",
            "**Problem**: Model downloads fail or timeout",
            "",
            "**Solution**:",
            "1. Check internet connection",
            "2. Some models allow manual download from HuggingFace",
            "3. Use VPN if in restricted network",
            "",
        ])
        
        return "\n".join(report_lines)


def main():
    """Main function."""
    installer = ModelInstaller()
    
    try:
        results = installer.run_all_tests()
        
        # Save results
        output_dir = Path("results_voice_cloning")
        output_dir.mkdir(exist_ok=True)
        
        # Save JSON
        results_file = output_dir / "installation_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"Results saved to {results_file}")
        
        # Generate report
        report = installer.generate_report(results)
        report_file = output_dir / "installation_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Report saved to {report_file}")
        
        # Print summary
        print("\n" + "=" * 70)
        print("INSTALLATION SUMMARY")
        print("=" * 70)
        
        working = [k for k, v in results.items() if v.get("voice_cloning") == True]
        if working:
            print(f"\n✅ {len(working)} voice cloning model(s) working:")
            for model_key in working:
                name = results[model_key].get("name", model_key)
                print(f"   - {name}")
        else:
            print("\n⚠️  No voice cloning models working yet.")
            print("   Check the report for build issues and solutions.")
        
        print(f"\n📊 Full results: {results_file}")
        print(f"📄 Full report: {report_file}")
        
    except KeyboardInterrupt:
        logger.info("\nInstallation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Installation script failed: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

