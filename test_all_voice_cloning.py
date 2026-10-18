#!/usr/bin/env python3
"""
Comprehensive test script to determine which open-source voice cloning software works best.

This script attempts to install and test each voice cloning model to determine:
1. Which models can be successfully installed
2. Which models actually work for voice cloning
3. Performance characteristics of each working model
"""

import sys
import subprocess
import importlib
import traceback
from pathlib import Path
import json
import time
import numpy as np
import soundfile as sf
import librosa
from typing import Dict, List, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test configuration
TEST_TEXT = "Hello, this is a test of the voice cloning system. How does it sound?"
REFERENCE_AUDIO_DURATION = 3.0  # seconds
SAMPLE_RATE = 22050


class ModelTester:
    """Test individual voice cloning models."""
    
    def __init__(self):
        self.results = {}
        self.test_audio_path = None
        self._create_test_audio()
    
    def _create_test_audio(self):
        """Create a test reference audio file."""
        try:
            # Generate a simple sine wave as test audio
            duration = REFERENCE_AUDIO_DURATION
            t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
            # Mix of frequencies to make it more voice-like
            audio = 0.3 * np.sin(2 * np.pi * 200 * t) + 0.2 * np.sin(2 * np.pi * 400 * t)
            audio = audio.astype(np.float32)
            
            self.test_audio_path = "temp_test_reference.wav"
            sf.write(self.test_audio_path, audio, SAMPLE_RATE)
            logger.info(f"Created test reference audio: {self.test_audio_path}")
        except Exception as e:
            logger.error(f"Failed to create test audio: {e}")
    
    def test_chatterbox(self) -> Dict:
        """Test Chatterbox voice cloning."""
        result = {
            "name": "Chatterbox",
            "status": "unknown",
            "installation": False,
            "basic_tts": False,
            "voice_cloning": False,
            "error": None,
            "performance": {}
        }
        
        try:
            # Test import
            logger.info("Testing Chatterbox...")
            import chatterbox
            
            result["installation"] = True
            logger.info("✅ Chatterbox installed")
            
            # Test basic TTS
            try:
                import torch
                device = "cuda" if torch.cuda.is_available() else "cpu"
                model = chatterbox.ChatterboxTTS.from_pretrained(device)
                
                start_time = time.time()
                audio_tensor = model.generate(TEST_TEXT)
                inference_time = time.time() - start_time
                
                audio = audio_tensor.squeeze(0).detach().cpu().numpy()
                result["basic_tts"] = True
                result["performance"]["basic_tts_time"] = inference_time
                result["performance"]["audio_length"] = len(audio) / 24000  # Chatterbox uses 24kHz
                logger.info(f"✅ Chatterbox basic TTS works (time: {inference_time:.2f}s)")
                
                # Test voice cloning
                try:
                    start_time = time.time()
                    audio_tensor = model.generate(TEST_TEXT, audio_prompt_path=self.test_audio_path)
                    cloning_time = time.time() - start_time
                    
                    result["voice_cloning"] = True
                    result["performance"]["cloning_time"] = cloning_time
                    logger.info(f"✅ Chatterbox voice cloning works (time: {cloning_time:.2f}s)")
                except Exception as e:
                    logger.warning(f"⚠️ Chatterbox voice cloning failed: {e}")
                    result["error"] = str(e)
                
            except Exception as e:
                logger.error(f"❌ Chatterbox TTS failed: {e}")
                result["error"] = str(e)
                traceback.print_exc()
            
            result["status"] = "working" if result["voice_cloning"] else "partial"
            
        except ImportError:
            logger.warning("⚠️ Chatterbox not installed")
            result["status"] = "not_installed"
            result["error"] = "Package not found"
        except Exception as e:
            logger.error(f"❌ Chatterbox test failed: {e}")
            result["status"] = "error"
            result["error"] = str(e)
            traceback.print_exc()
        
        return result
    
    def test_coqui_tts(self) -> Dict:
        """Test Coqui TTS (XTTS-v2) voice cloning."""
        result = {
            "name": "Coqui TTS (XTTS-v2)",
            "status": "unknown",
            "installation": False,
            "basic_tts": False,
            "voice_cloning": False,
            "error": None,
            "performance": {}
        }
        
        try:
            # Test import
            logger.info("Testing Coqui TTS...")
            from TTS.api import TTS
            
            result["installation"] = True
            logger.info("✅ Coqui TTS installed")
            
            # Test basic TTS
            try:
                model = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
                
                start_time = time.time()
                audio = model.tts(text=TEST_TEXT)
                inference_time = time.time() - start_time
                
                result["basic_tts"] = True
                result["performance"]["basic_tts_time"] = inference_time
                result["performance"]["audio_length"] = len(audio) / 22050
                logger.info(f"✅ Coqui TTS basic TTS works (time: {inference_time:.2f}s)")
                
                # Test voice cloning
                try:
                    start_time = time.time()
                    audio = model.tts(text=TEST_TEXT, speaker_wav=self.test_audio_path)
                    cloning_time = time.time() - start_time
                    
                    result["voice_cloning"] = True
                    result["performance"]["cloning_time"] = cloning_time
                    logger.info(f"✅ Coqui TTS voice cloning works (time: {cloning_time:.2f}s)")
                except Exception as e:
                    logger.warning(f"⚠️ Coqui TTS voice cloning failed: {e}")
                    result["error"] = str(e)
                
            except Exception as e:
                logger.error(f"❌ Coqui TTS synthesis failed: {e}")
                result["error"] = str(e)
                traceback.print_exc()
            
            result["status"] = "working" if result["voice_cloning"] else "partial"
            
        except ImportError:
            logger.warning("⚠️ Coqui TTS not installed")
            result["status"] = "not_installed"
            result["error"] = "Package not found"
        except Exception as e:
            logger.error(f"❌ Coqui TTS test failed: {e}")
            result["status"] = "error"
            result["error"] = str(e)
            traceback.print_exc()
        
        return result
    
    def test_openvoice(self) -> Dict:
        """Test OpenVoice."""
        result = {
            "name": "OpenVoice",
            "status": "unknown",
            "installation": False,
            "basic_tts": False,
            "voice_cloning": False,
            "error": None,
            "performance": {}
        }
        
        try:
            # Check if OpenVoice directory exists
            openvoice_path = Path("models/OpenVoice")
            if not openvoice_path.exists():
                logger.warning("⚠️ OpenVoice not found in models/ directory")
                result["status"] = "not_installed"
                result["error"] = "OpenVoice directory not found. Clone from: https://github.com/myshell-ai/OpenVoice"
                return result
            
            # Try to import
            sys.path.insert(0, str(openvoice_path))
            from openvoice import se_extractor
            from openvoice.api import ToneColorConverter
            
            result["installation"] = True
            logger.info("✅ OpenVoice found")
            
            # Note: OpenVoice requires specific model files
            # This is a placeholder - actual implementation would need model files
            result["status"] = "needs_setup"
            result["error"] = "OpenVoice requires model files to be downloaded separately"
            logger.info("⚠️ OpenVoice requires additional setup (model files)")
            
        except ImportError as e:
            logger.warning(f"⚠️ OpenVoice import failed: {e}")
            result["status"] = "not_installed"
            result["error"] = f"Import error: {str(e)}"
        except Exception as e:
            logger.error(f"❌ OpenVoice test failed: {e}")
            result["status"] = "error"
            result["error"] = str(e)
        
        return result
    
    def test_fish_speech(self) -> Dict:
        """Test Fish-Speech."""
        result = {
            "name": "Fish-Speech",
            "status": "unknown",
            "installation": False,
            "basic_tts": False,
            "voice_cloning": False,
            "error": None,
            "performance": {}
        }
        
        try:
            # Check if Fish-Speech directory exists
            fish_speech_path = Path("models/fish-speech")
            if not fish_speech_path.exists():
                logger.warning("⚠️ Fish-Speech not found in models/ directory")
                result["status"] = "not_installed"
                result["error"] = "Fish-Speech directory not found. Clone from: https://github.com/fishaudio/fish-speech"
                return result
            
            # Try to import (this would need actual implementation)
            result["status"] = "needs_setup"
            result["error"] = "Fish-Speech requires complex setup and model downloads"
            logger.info("⚠️ Fish-Speech requires additional setup")
            
        except Exception as e:
            logger.error(f"❌ Fish-Speech test failed: {e}")
            result["status"] = "error"
            result["error"] = str(e)
        
        return result
    
    def test_gpt_sovits(self) -> Dict:
        """Test GPT-SoVITS."""
        result = {
            "name": "GPT-SoVITS",
            "status": "unknown",
            "installation": False,
            "basic_tts": False,
            "voice_cloning": False,
            "error": None,
            "performance": {}
        }
        
        try:
            # Check if GPT-SoVITS directory exists
            gpt_sovits_path = Path("models/GPT-SoVITS")
            if not gpt_sovits_path.exists():
                logger.warning("⚠️ GPT-SoVITS not found in models/ directory")
                result["status"] = "not_installed"
                result["error"] = "GPT-SoVITS directory not found. Clone from: https://github.com/RVC-Boss/GPT-SoVITS"
                return result
            
            # Try to import (this would need actual implementation)
            result["status"] = "needs_setup"
            result["error"] = "GPT-SoVITS requires model training/fine-tuning setup"
            logger.info("⚠️ GPT-SoVITS requires additional setup")
            
        except Exception as e:
            logger.error(f"❌ GPT-SoVITS test failed: {e}")
            result["status"] = "error"
            result["error"] = str(e)
        
        return result
    
    def test_cosyvoice(self) -> Dict:
        """Test CosyVoice."""
        result = {
            "name": "CosyVoice",
            "status": "unknown",
            "installation": False,
            "basic_tts": False,
            "voice_cloning": False,
            "error": None,
            "performance": {}
        }
        
        try:
            # Check if CosyVoice directory exists
            cosyvoice_path = Path("models/CosyVoice")
            if not cosyvoice_path.exists():
                logger.warning("⚠️ CosyVoice not found in models/ directory")
                result["status"] = "not_installed"
                result["error"] = "CosyVoice directory not found. Clone from: https://github.com/FunAudioLLM/CosyVoice"
                return result
            
            # Try to import (this would need actual implementation)
            result["status"] = "needs_setup"
            result["error"] = "CosyVoice requires model files and setup"
            logger.info("⚠️ CosyVoice requires additional setup")
            
        except Exception as e:
            logger.error(f"❌ CosyVoice test failed: {e}")
            result["status"] = "error"
            result["error"] = str(e)
        
        return result
    
    def run_all_tests(self) -> Dict:
        """Run tests on all models."""
        logger.info("=" * 60)
        logger.info("Starting comprehensive voice cloning model tests")
        logger.info("=" * 60)
        
        all_results = {}
        
        # Test each model
        test_functions = [
            ("chatterbox", self.test_chatterbox),
            ("coqui_tts", self.test_coqui_tts),
            ("openvoice", self.test_openvoice),
            ("fish_speech", self.test_fish_speech),
            ("gpt_sovits", self.test_gpt_sovits),
            ("cosyvoice", self.test_cosyvoice),
        ]
        
        for model_key, test_func in test_functions:
            logger.info(f"\n{'='*60}")
            logger.info(f"Testing {model_key.upper()}")
            logger.info(f"{'='*60}")
            try:
                result = test_func()
                all_results[model_key] = result
            except Exception as e:
                logger.error(f"Unexpected error testing {model_key}: {e}")
                all_results[model_key] = {
                    "name": model_key,
                    "status": "error",
                    "error": str(e)
                }
        
        # Cleanup
        if self.test_audio_path and Path(self.test_audio_path).exists():
            try:
                Path(self.test_audio_path).unlink()
            except:
                pass
        
        return all_results
    
    def generate_report(self, results: Dict) -> str:
        """Generate a markdown report from test results."""
        report_lines = [
            "# Voice Cloning Software Test Results",
            "",
            f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            ""
        ]
        
        # Count working models
        working = [k for k, v in results.items() if v.get("voice_cloning") == True]
        partial = [k for k, v in results.items() if v.get("basic_tts") == True and not v.get("voice_cloning")]
        not_working = [k for k, v in results.items() if not v.get("basic_tts")]
        
        report_lines.append(f"- **Working (Voice Cloning)**: {len(working)} models")
        report_lines.append(f"- **Partial (Basic TTS only)**: {len(partial)} models")
        report_lines.append(f"- **Not Working/Not Installed**: {len(not_working)} models")
        report_lines.append("")
        
        # Detailed results
        report_lines.extend([
            "## Detailed Results",
            ""
        ])
        
        for model_key, result in results.items():
            name = result.get("name", model_key)
            status = result.get("status", "unknown")
            
            report_lines.extend([
                f"### {name}",
                "",
                f"- **Status**: {status}",
                f"- **Installation**: {'✅' if result.get('installation') else '❌'}",
                f"- **Basic TTS**: {'✅' if result.get('basic_tts') else '❌'}",
                f"- **Voice Cloning**: {'✅' if result.get('voice_cloning') else '❌'}",
                ""
            ])
            
            if result.get("performance"):
                report_lines.append("**Performance:**")
                for metric, value in result["performance"].items():
                    report_lines.append(f"- {metric}: {value:.3f}")
                report_lines.append("")
            
            if result.get("error"):
                report_lines.append(f"**Error/Note**: {result['error']}")
                report_lines.append("")
        
        # Recommendations
        report_lines.extend([
            "## Recommendations",
            ""
        ])
        
        if working:
            report_lines.append("### ✅ Working Voice Cloning Models")
            for model_key in working:
                name = results[model_key].get("name", model_key)
                perf = results[model_key].get("performance", {})
                cloning_time = perf.get("cloning_time", "N/A")
                report_lines.append(f"- **{name}**: Voice cloning works (cloning time: {cloning_time})")
            report_lines.append("")
        
        if partial:
            report_lines.append("### ⚠️ Partial Support (TTS only)")
            for model_key in partial:
                name = results[model_key].get("name", model_key)
                report_lines.append(f"- **{name}**: Basic TTS works but voice cloning not tested/working")
            report_lines.append("")
        
        if not_working:
            report_lines.append("### ❌ Not Working / Needs Setup")
            for model_key in not_working:
                name = results[model_key].get("name", model_key)
                error = results[model_key].get("error", "Unknown error")
                report_lines.append(f"- **{name}**: {error}")
            report_lines.append("")
        
        # Best overall
        if working:
            report_lines.extend([
                "## 🏆 Best Overall",
                "",
                "Based on the tests, the best working open-source voice cloning software is:",
                ""
            ])
            
            # Find fastest working model
            best_model = None
            best_time = float('inf')
            for model_key in working:
                perf = results[model_key].get("performance", {})
                cloning_time = perf.get("cloning_time", float('inf'))
                if cloning_time < best_time:
                    best_time = cloning_time
                    best_model = model_key
            
            if best_model:
                name = results[best_model].get("name", best_model)
                report_lines.append(f"**{name}** - Fastest voice cloning ({best_time:.2f}s)")
            report_lines.append("")
        
        return "\n".join(report_lines)


def main():
    """Main function to run all tests."""
    tester = ModelTester()
    
    try:
        results = tester.run_all_tests()
        
        # Save results to JSON
        output_dir = Path("results_voice_cloning")
        output_dir.mkdir(exist_ok=True)
        
        results_file = output_dir / "test_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"Results saved to {results_file}")
        
        # Generate report
        report = tester.generate_report(results)
        report_file = output_dir / "test_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Report saved to {report_file}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        working = [k for k, v in results.items() if v.get("voice_cloning") == True]
        print(f"✅ Working voice cloning models: {len(working)}")
        for model_key in working:
            name = results[model_key].get("name", model_key)
            print(f"   - {name}")
        
        print(f"\n📊 Full results: {results_file}")
        print(f"📄 Full report: {report_file}")
        
    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

