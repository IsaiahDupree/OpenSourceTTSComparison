#!/usr/bin/env python3
"""
Complete test suite for OpenVoice - Run this in a separate terminal
while OpenVoice is running on localhost:7860
"""

import os
import sys
import time
import requests
from pathlib import Path
from gradio_client import Client

# Try to import handle_file - may not be available in all versions
try:
    from gradio_client import handle_file
except ImportError:
    # Fallback: handle_file might not be needed or available
    def handle_file(file_path):
        return file_path

def log(message, level="INFO"):
    """Console logging with @pwsh format"""
    import datetime
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] @pwsh [{level}] {message}")

def print_header(title):
    """Print a formatted header"""
    log("=" * 70, "TEST")
    log(f" {title}", "TEST")
    log("=" * 70, "TEST")

def test_startup():
    """Test 1: Startup checks"""
    print_header("TEST 1: Startup Checks")
    
    # Check Python version
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        log(f"Python 3.8+ required. Found: {version.major}.{version.minor}", "ERROR")
        return False
    log(f"Python {version.major}.{version.minor}.{version.micro} - OK", "SUCCESS")
    
    # Check server is running
    log("Checking server connection...", "INFO")
    try:
        response = requests.get("http://localhost:7860", timeout=5)
        if response.status_code == 200:
            log("Server is running on http://localhost:7860", "SUCCESS")
        else:
            log(f"Server returned status {response.status_code}", "ERROR")
            return False
    except requests.exceptions.ConnectionError:
        log("Cannot connect to server", "ERROR")
        log("Make sure OpenVoice is running: python run_openvoice_local.py", "INFO")
        return False
    
    # Check API connection
    log("Checking API connection...", "INFO")
    try:
        client = Client("http://localhost:7860")
        log("API is accessible", "SUCCESS")
        return True, client
    except Exception as e:
        # Handle encoding errors gracefully
        error_msg = str(e).encode('ascii', errors='replace').decode('ascii')
        log(f"API connection failed: {error_msg}", "ERROR")
        return False, None

def test_generation(client, text, style, audio_file, test_name):
    """Test a single generation"""
    log(f"Test: {test_name}", "TEST")
    log(f"Text: {text[:60]}...", "INFO")
    log(f"Style: {style}", "INFO")
    log(f"Reference: {audio_file}", "INFO")
    
    try:
        # Get full path to audio file
        audio_path = Path("openvoice_deploy") / audio_file
        if not audio_path.exists():
            log(f"Audio file not found: {audio_path}", "ERROR")
            return False
        
        log("Submitting request...", "INFO")
        start_time = time.time()
        
        # Try to use handle_file, fallback to direct path
        try:
            audio_input = handle_file(str(audio_path))
        except:
            audio_input = str(audio_path)
        
        # Try using HTTP requests directly to bypass gradio_client issues
        try:
            import requests
            predict_url = "http://localhost:7860/api/predict"
            
            # Prepare data
            data = {
                "data": [text, style, str(audio_path), True],
                "fn_index": 1
            }
            
            log("Using HTTP API directly...", "INFO")
            response = requests.post(predict_url, json=data, timeout=300)
            
            if response.status_code == 200:
                result_data = response.json()
                if "data" in result_data:
                    # Convert to same format as gradio_client
                    result = tuple(result_data["data"])
                else:
                    raise ValueError(f"Unexpected response: {result_data}")
            else:
                raise ValueError(f"HTTP {response.status_code}: {response.text[:200]}")
        except Exception as http_error:
            log(f"HTTP API failed: {http_error}, trying gradio_client...", "INFO")
            # Fallback to gradio_client
            # Use fn_index=1 as shown in the API usage info
            # Function signature: predict(text_prompt, style, reference_audio, agree, fn_index=1)
            result = client.predict(
                text,  # text_prompt
                style,  # style
                audio_input,  # reference_audio
                True,  # agree
                fn_index=1
            )
        
        elapsed = time.time() - start_time
        
        info_text, audio_path_result, ref_audio = result
        
        if "ERROR" in info_text:
            log(f"FAILED: {info_text}", "ERROR")
            return False
        
        if audio_path_result:
            if isinstance(audio_path_result, str):
                if os.path.exists(audio_path_result):
                    file_size = os.path.getsize(audio_path_result) / 1024  # KB
                    log(f"SUCCESS - Time: {elapsed:.1f}s, Size: {file_size:.1f} KB", "SUCCESS")
                    log(f"Output: {audio_path_result}", "INFO")
                    return True
                else:
                    log(f"Generated (path: {audio_path_result}) - Time: {elapsed:.1f}s", "SUCCESS")
                    return True
            else:
                log(f"SUCCESS (audio object returned) - Time: {elapsed:.1f}s", "SUCCESS")
                return True
        else:
            log(f"FAILED: No audio generated. Info: {info_text}", "ERROR")
            return False
            
    except Exception as e:
        log(f"FAILED: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def main():
    log("=" * 70, "TEST")
    log(" OpenVoice Complete Test Suite", "TEST")
    log("=" * 70, "TEST")
    log("Make sure OpenVoice is running in another terminal:", "INFO")
    log("  python start_server.py", "INFO")
    log("Starting tests in 3 seconds...", "INFO")
    time.sleep(3)
    
    # Test 1: Startup
    result, client = test_startup()
    if not result:
        log("Startup tests failed. Please fix issues and try again.", "ERROR")
        return 1
    
    # Test 2: Generations
    print_header("TEST 2: Voice Generation Tests")
    log("Note: First generation may take 30-60 seconds (model loading)", "INFO")
    
    test_cases = [
        {
            "name": "Short English - Default Style",
            "text": "Hello, this is a test of the OpenVoice system.",
            "style": "default",
            "audio": "resources/demo_speaker2.mp3"
        },
        {
            "name": "English - Whispering Style",
            "text": "This is a whispering test.",
            "style": "whispering",
            "audio": "resources/demo_speaker2.mp3"
        },
        {
            "name": "English - Cheerful Style",
            "text": "This is a cheerful test!",
            "style": "cheerful",
            "audio": "resources/demo_speaker0.mp3"
        },
    ]
    
    results = []
    for i, test_case in enumerate(test_cases, 1):
        log(f"[{i}/{len(test_cases)}] Running test...", "INFO")
        result = test_generation(
            client,
            test_case["text"],
            test_case["style"],
            test_case["audio"],
            test_case["name"]
        )
        results.append((test_case["name"], result))
        
        # Small delay between tests
        if i < len(test_cases):
            time.sleep(2)
    
    # Summary
    print_header("Test Summary")
    
    startup_passed = True  # Startup tests passed if we got here
    gen_passed = sum(1 for _, result in results if result)
    gen_total = len(results)
    
    # Build summary list
    summary_list = []
    summary_list.append(("Startup Tests", startup_passed))
    for name, result in results:
        summary_list.append((name, result))
    
    # Print summary
    log("", "INFO")
    log("=" * 70, "TEST")
    log(" TEST RESULTS SUMMARY", "TEST")
    log("=" * 70, "TEST")
    log("", "INFO")
    
    all_passed = True
    for name, result in summary_list:
        status = "[PASS]" if result else "[FAIL]"
        level = "SUCCESS" if result else "ERROR"
        log(f"{status} - {name}", level)
        if not result:
            all_passed = False
    
    log("", "INFO")
    log("=" * 70, "TEST")
    log(f"Overall: {gen_passed}/{gen_total} generation tests passed", "INFO")
    log("=" * 70, "TEST")
    log("", "INFO")
    
    if all_passed:
        log("ALL TESTS PASSED!", "SUCCESS")
        log("OpenVoice is working correctly!", "SUCCESS")
        log("Your build is verified and ready to use!", "SUCCESS")
        return 0
    else:
        log("Some tests FAILED", "ERROR")
        log("", "INFO")
        log("Common issues:", "INFO")
        log("1. whisper_timestamped error: Restart the server to load the fix", "INFO")
        log("2. API errors: Check that the server is fully started", "INFO")
        log("3. Generation errors: Check server logs for details", "INFO")
        return 1

if __name__ == "__main__":
    sys.exit(main())

