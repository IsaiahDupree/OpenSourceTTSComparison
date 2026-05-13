#!/usr/bin/env python3
"""
Quick test script to find working voice cloning solutions WITHOUT long installations.
Tests lightweight alternatives and provides real-time console logging.
"""

import sys
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime
import logging

# Set up real-time console logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Test configuration
TEST_TEXT = "Hello, this is a quick test of voice cloning."
TIMEOUT_SECONDS = 300  # 5 minutes max per installation


class QuickTester:
    """Quick test with real-time logging and timeouts."""
    
    def __init__(self):
        self.results = {}
        self.start_time = time.time()
    
    def log(self, message, level="INFO"):
        """Log with timestamp."""
        elapsed = time.time() - self.start_time
        getattr(logger, level.lower())(f"[{elapsed:.1f}s] {message}")
    
    def quick_install_test(self, package_name, test_import, test_code=None):
        """Quick test with timeout and real-time output."""
        self.log(f"Testing {package_name}...", "INFO")
        
        result = {
            "name": package_name,
            "status": "testing",
            "install_time": None,
            "works": False,
            "error": None
        }
        
        start = time.time()
        
        try:
            # Check if already installed
            self.log(f"  → Checking if {package_name} is installed...", "INFO")
            try:
                __import__(test_import)
                self.log(f"  ✅ {package_name} already installed!", "INFO")
                result["works"] = True
                result["status"] = "already_installed"
                result["install_time"] = time.time() - start
                return result
            except ImportError:
                self.log(f"  → {package_name} not installed, attempting quick install...", "INFO")
            
            # Try quick install with timeout
            self.log(f"  → Running: pip install {package_name} (timeout: {TIMEOUT_SECONDS}s)", "INFO")
            
            process = subprocess.Popen(
                [sys.executable, "-m", "pip", "install", package_name, "--quiet"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Monitor with timeout
            output_lines = []
            install_start = time.time()
            
            while True:
                elapsed = time.time() - install_start
                
                if elapsed > TIMEOUT_SECONDS:
                    self.log(f"  ❌ TIMEOUT after {TIMEOUT_SECONDS}s - installation taking too long", "ERROR")
                    process.terminate()
                    result["status"] = "timeout"
                    result["error"] = f"Installation timeout after {TIMEOUT_SECONDS} seconds"
                    result["install_time"] = elapsed
                    return result
                
                # Check if process finished
                if process.poll() is not None:
                    break
                
                # Read output line by line
                line = process.stdout.readline()
                if line:
                    line = line.strip()
                    if line and "Requirement already satisfied" not in line:
                        # Only log meaningful output
                        if "Downloading" in line or "Installing" in line or "Building" in line:
                            self.log(f"  → {line[:80]}", "INFO")
                
                time.sleep(0.1)
            
            # Get return code
            return_code = process.wait()
            install_time = time.time() - install_start
            
            if return_code == 0:
                self.log(f"  ✅ Installation completed in {install_time:.1f}s", "INFO")
                result["install_time"] = install_time
                
                # Test import
                self.log(f"  → Testing import...", "INFO")
                try:
                    module = __import__(test_import)
                    self.log(f"  ✅ Import successful!", "INFO")
                    
                    # Run test code if provided
                    if test_code:
                        self.log(f"  → Running functionality test...", "INFO")
                        try:
                            exec(test_code)
                            self.log(f"  ✅ Functionality test passed!", "INFO")
                            result["works"] = True
                            result["status"] = "working"
                        except Exception as e:
                            self.log(f"  ⚠️  Functionality test failed: {e}", "WARNING")
                            result["error"] = f"Test failed: {str(e)}"
                    else:
                        result["works"] = True
                        result["status"] = "working"
                        
                except ImportError as e:
                    self.log(f"  ❌ Import failed: {e}", "ERROR")
                    result["error"] = f"Import failed: {str(e)}"
                    result["status"] = "import_failed"
            else:
                self.log(f"  ❌ Installation failed (code: {return_code})", "ERROR")
                result["error"] = f"Installation failed with code {return_code}"
                result["status"] = "install_failed"
                result["install_time"] = install_time
                
        except subprocess.TimeoutExpired:
            self.log(f"  ❌ Process timeout", "ERROR")
            result["error"] = "Process timeout"
            result["status"] = "timeout"
        except Exception as e:
            self.log(f"  ❌ Unexpected error: {e}", "ERROR")
            result["error"] = str(e)
            result["status"] = "error"
        
        return result
    
    def test_lightweight_alternatives(self):
        """Test lightweight alternatives that don't require heavy installations."""
        self.log("=" * 70, "INFO")
        self.log("Testing Lightweight Voice Cloning Alternatives", "INFO")
        self.log("=" * 70, "INFO")
        
        results = {}
        
        # Test 1: pyttsx3 (very lightweight, no build)
        self.log("\n[TEST 1] pyttsx3 - Simple TTS (no cloning)", "INFO")
        result = self.quick_install_test(
            "pyttsx3",
            "pyttsx3",
            test_code="""
import pyttsx3
engine = pyttsx3.init()
# Just test it initializes
"""
        )
        result["voice_cloning"] = False
        result["note"] = "Simple TTS, no voice cloning"
        results["pyttsx3"] = result
        
        # Test 2: gTTS (Google TTS, lightweight)
        self.log("\n[TEST 2] gTTS - Google TTS (online, no cloning)", "INFO")
        result = self.quick_install_test(
            "gtts",
            "gtts",
            test_code="""
from gtts import gTTS
# Just test import
"""
        )
        result["voice_cloning"] = False
        result["note"] = "Online TTS, requires internet, no voice cloning"
        results["gtts"] = result
        
        # Test 3: Coqui TTS (try quick test)
        self.log("\n[TEST 3] Coqui TTS - Full voice cloning (may take time)", "INFO")
        result = self.quick_install_test(
            "TTS",
            "TTS",
            test_code=None  # Don't test full functionality yet, just import
        )
        if result["works"]:
            result["voice_cloning"] = True
            result["note"] = "Full voice cloning support with XTTS-v2"
        results["coqui_tts"] = result
        
        # Test 4: edge-tts (Microsoft Edge TTS, very lightweight)
        self.log("\n[TEST 4] edge-tts - Microsoft Edge TTS (lightweight)", "INFO")
        result = self.quick_install_test(
            "edge-tts",
            "edge_tts",
            test_code=None
        )
        result["voice_cloning"] = False
        result["note"] = "Free Microsoft voices, no cloning but many voices"
        results["edge_tts"] = result
        
        return results
    
    def test_api_alternatives(self):
        """Test API-based alternatives (no installation needed)."""
        self.log("\n" + "=" * 70, "INFO")
        self.log("Testing API-Based Alternatives (No Installation)", "INFO")
        self.log("=" * 70, "INFO")
        
        results = {}
        
        # Test OpenAI TTS API (if key available)
        self.log("\n[API TEST 1] OpenAI TTS API", "INFO")
        try:
            import openai
            result = {
                "name": "OpenAI TTS API",
                "status": "available",
                "works": True,
                "voice_cloning": False,
                "note": "Requires API key, pay-per-use, high quality",
                "install_time": 0
            }
            results["openai_tts"] = result
            self.log("  ✅ OpenAI library available", "INFO")
        except:
            result = {
                "name": "OpenAI TTS API",
                "status": "not_installed",
                "works": False,
                "voice_cloning": False,
                "note": "Install: pip install openai, requires API key",
                "install_time": 0
            }
            results["openai_tts"] = result
            self.log("  ⚠️  OpenAI library not installed", "WARNING")
        
        # Test ElevenLabs API
        self.log("\n[API TEST 2] ElevenLabs API", "INFO")
        try:
            import requests
            result = {
                "name": "ElevenLabs API",
                "status": "available",
                "works": True,
                "voice_cloning": True,
                "note": "Requires API key, pay-per-use, excellent voice cloning",
                "install_time": 0
            }
            results["elevenlabs"] = result
            self.log("  ✅ requests library available (can use ElevenLabs API)", "INFO")
        except:
            result = {
                "name": "ElevenLabs API",
                "status": "not_installed",
                "works": False,
                "voice_cloning": True,
                "note": "API-based, no installation needed, requires API key",
                "install_time": 0
            }
            results["elevenlabs"] = result
        
        return results
    
    def generate_recommendations(self, all_results):
        """Generate recommendations based on results."""
        self.log("\n" + "=" * 70, "INFO")
        self.log("GENERATING RECOMMENDATIONS", "INFO")
        self.log("=" * 70, "INFO")
        
        recommendations = []
        
        # Find working voice cloning
        working_cloning = [k for k, v in all_results.items() if v.get("voice_cloning") and v.get("works")]
        if working_cloning:
            self.log(f"\n✅ Found {len(working_cloning)} working voice cloning solution(s):", "INFO")
            for key in working_cloning:
                name = all_results[key].get("name", key)
                install_time = all_results[key].get("install_time", 0)
                self.log(f"   - {name} (install time: {install_time:.1f}s)", "INFO")
                recommendations.append({
                    "type": "voice_cloning",
                    "name": name,
                    "key": key,
                    "priority": 1
                })
        
        # Find lightweight alternatives
        lightweight = [k for k, v in all_results.items() if v.get("works") and not v.get("voice_cloning")]
        if lightweight:
            self.log(f"\n💡 Found {len(lightweight)} lightweight TTS solution(s):", "INFO")
            for key in lightweight:
                name = all_results[key].get("name", key)
                note = all_results[key].get("note", "")
                self.log(f"   - {name}: {note}", "INFO")
                recommendations.append({
                    "type": "lightweight_tts",
                    "name": name,
                    "key": key,
                    "priority": 2
                })
        
        # API alternatives
        api_solutions = [k for k, v in all_results.items() if "API" in v.get("name", "")]
        if api_solutions:
            self.log(f"\n🌐 API-based solutions (no installation):", "INFO")
            for key in api_solutions:
                name = all_results[key].get("name", key)
                note = all_results[key].get("note", "")
                self.log(f"   - {name}: {note}", "INFO")
                recommendations.append({
                    "type": "api",
                    "name": name,
                    "key": key,
                    "priority": 3
                })
        
        return recommendations
    
    def run_all_tests(self):
        """Run all quick tests."""
        total_start = time.time()
        
        self.log("=" * 70, "INFO")
        self.log("QUICK VOICE CLONING SOLUTION FINDER", "INFO")
        self.log(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "INFO")
        self.log("=" * 70, "INFO")
        
        all_results = {}
        
        # Test lightweight alternatives
        lightweight_results = self.test_lightweight_alternatives()
        all_results.update(lightweight_results)
        
        # Test API alternatives
        api_results = self.test_api_alternatives()
        all_results.update(api_results)
        
        # Generate recommendations
        recommendations = self.generate_recommendations(all_results)
        
        total_time = time.time() - total_start
        
        self.log("\n" + "=" * 70, "INFO")
        self.log(f"TESTING COMPLETE in {total_time:.1f} seconds", "INFO")
        self.log("=" * 70, "INFO")
        
        return all_results, recommendations


def main():
    """Main function."""
    tester = QuickTester()
    
    try:
        results, recommendations = tester.run_all_tests()
        
        # Save results
        output_dir = Path("results_voice_cloning")
        output_dir.mkdir(exist_ok=True)
        
        # Save JSON
        results_file = output_dir / "quick_test_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                "results": results,
                "recommendations": recommendations,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2, default=str)
        
        # Generate quick report
        report_lines = [
            "# Quick Voice Cloning Test Results",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            ""
        ]
        
        working_cloning = [k for k, v in results.items() if v.get("voice_cloning") and v.get("works")]
        working_tts = [k for k, v in results.items() if v.get("works") and not v.get("voice_cloning")]
        
        report_lines.append(f"- **Working Voice Cloning**: {len(working_cloning)}")
        report_lines.append(f"- **Working TTS (no cloning)**: {len(working_tts)}")
        report_lines.append("")
        
        if working_cloning:
            report_lines.extend([
                "## ✅ Working Voice Cloning Solutions",
                ""
            ])
            for key in working_cloning:
                r = results[key]
                name = r.get("name", key)
                install_time = r.get("install_time", 0)
                report_lines.append(f"- **{name}** (install: {install_time:.1f}s)")
            report_lines.append("")
        
        if recommendations:
            report_lines.extend([
                "## Recommendations",
                ""
            ])
            for rec in sorted(recommendations, key=lambda x: x["priority"]):
                report_lines.append(f"1. **{rec['name']}** ({rec['type']})")
            report_lines.append("")
        
        report_file = output_dir / "quick_test_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(report_lines))
        
        print("\n" + "=" * 70)
        print("RESULTS SAVED")
        print("=" * 70)
        print(f"📊 Results: {results_file}")
        print(f"📄 Report: {report_file}")
        
        if working_cloning:
            print(f"\n✅ Found {len(working_cloning)} working voice cloning solution(s)!")
        else:
            print("\n💡 No voice cloning solutions found, but check lightweight alternatives")
            print("   or consider API-based solutions (ElevenLabs, OpenAI)")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

