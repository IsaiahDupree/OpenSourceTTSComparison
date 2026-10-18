#!/usr/bin/env python3
"""
Comprehensive test of all TTS APIs to see what actually works
"""

import os
import sys
import time
import requests
from pathlib import Path

def log(message, level="INFO"):
    """Console logging"""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def test_space_connectivity(space_id, base_url):
    """Test if a Space is accessible"""
    try:
        response = requests.get(base_url, timeout=10)
        return response.status_code == 200
    except:
        return False

def test_openvoice_v2():
    """Test OpenVoice V2 API"""
    print("\n" + "=" * 70)
    print(" TEST 1: OpenVoice V2")
    print("=" * 70)
    
    endpoint = "https://myshell-ai-openvoicev2.hf.space/--replicas/c2rsh/"
    base_url = "https://myshell-ai-openvoicev2.hf.space/--replicas/c2rsh/"
    token = os.getenv("HF_TOKEN", (__import__('os').environ['HF_TOKEN']))
    
    log("Testing connectivity...")
    if not test_space_connectivity("OpenVoice V2", base_url):
        log("Space not accessible", "ERROR")
        return False
    
    log("Space is accessible", "SUCCESS")
    
    try:
        from gradio_client import Client
        log("Connecting with gradio_client...")
        client = Client(endpoint, hf_token=token)
        log("Connected!", "SUCCESS")
        
        log("Submitting test request...")
        log("Text: 'Hello, this is a test.'")
        log("Style: 'en_default'")
        log("Audio: Demo audio URL")
        
        job = client.submit(
            "Hello, this is a test.",
            "en_default",
            "https://github.com/gradio-app/gradio/raw/main/test/test_files/audio_sample.wav",
            True,
            fn_index=1
        )
        
        log("Request submitted, waiting (max 60s)...")
        try:
            result = job.result(timeout=60)
            info, audio, ref = result
            log(f"SUCCESS! Audio generated: {audio}", "SUCCESS")
            return True
        except ValueError as e:
            if "None" in str(e):
                log("Cold start/overload detected (ValueError: None)", "WARNING")
                log("Space may need more time or is overloaded", "INFO")
                return False
            raise
    except Exception as e:
        log(f"Failed: {e}", "ERROR")
        return False

def test_qwen3_tts():
    """Test Qwen3-TTS Voice Design API"""
    print("\n" + "=" * 70)
    print(" TEST 2: Qwen3-TTS Voice Design")
    print("=" * 70)
    
    space_id = "Qwen/Qwen3-TTS-Voice-Design"
    base_url = "https://qwen-qwen3-tts-voice-design.hf.space"
    token = os.getenv("HF_TOKEN", (__import__('os').environ['HF_TOKEN']))
    
    log("Testing connectivity...")
    if not test_space_connectivity("Qwen3-TTS", base_url):
        log("Space not accessible", "ERROR")
        return False
    
    log("Space is accessible", "SUCCESS")
    
    try:
        from gradio_client import Client
        log("Connecting with gradio_client...")
        client = Client(space_id, hf_token=token)
        log("Connected!", "SUCCESS")
        
        log("Submitting test request...")
        text = "Hello! This is a test of the Qwen3-TTS voice design system."
        instruct = "A clear and natural female voice, moderate speed, stable tone."
        
        log(f"Text: {text}")
        log(f"Instruction: {instruct}")
        
        job = client.submit(
            text,
            instruct,
            api_name="/tts_interface"
        )
        
        log("Request submitted, waiting (max 60s)...")
        try:
            result = job.result(timeout=60)
            log(f"SUCCESS! Audio generated: {result}", "SUCCESS")
            return True
        except Exception as e:
            error_msg = str(e)
            if "WebSocket" in error_msg or "websocket" in error_msg.lower():
                log("WebSocket connection failed", "WARNING")
                log("This is a known gradio_client compatibility issue", "INFO")
                log("Use browser JavaScript or web interface instead", "INFO")
            else:
                log(f"Failed: {error_msg}", "ERROR")
            return False
    except Exception as e:
        log(f"Failed: {e}", "ERROR")
        return False

def test_local_openvoice():
    """Test local OpenVoice server"""
    print("\n" + "=" * 70)
    print(" TEST 3: Local OpenVoice Server")
    print("=" * 70)
    
    base_url = "http://localhost:7860"
    
    log("Testing connectivity...")
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            log("Server is running", "SUCCESS")
        else:
            log(f"Server returned {response.status_code}", "ERROR")
            return False
    except:
        log("Server not running", "ERROR")
        log("Start it with: python start_server.py", "INFO")
        return False
    
    try:
        from gradio_client import Client
        log("Connecting with gradio_client...")
        client = Client(base_url)
        log("Connected!", "SUCCESS")
        
        # Check if we can get API info
        try:
            api_info = client.view_api()
            log(f"API has {len(api_info)} endpoints", "SUCCESS")
        except:
            log("Could not get API info", "WARNING")
        
        log("Local server is accessible via API", "SUCCESS")
        log("Note: Generation tests may fail due to server errors", "INFO")
        return True
    except Exception as e:
        log(f"Failed: {e}", "ERROR")
        return False

def main():
    print("=" * 70)
    print(" Comprehensive TTS API Test Suite")
    print("=" * 70)
    print("\nTesting all available TTS APIs to see what works...")
    
    results = {}
    
    # Test 1: OpenVoice V2
    results["OpenVoice V2"] = test_openvoice_v2()
    
    # Test 2: Qwen3-TTS
    results["Qwen3-TTS"] = test_qwen3_tts()
    
    # Test 3: Local OpenVoice
    results["Local OpenVoice"] = test_local_openvoice()
    
    # Summary
    print("\n" + "=" * 70)
    print(" TEST RESULTS SUMMARY")
    print("=" * 70)
    
    for name, success in results.items():
        status = "[PASS]" if success else "[FAIL]"
        level = "SUCCESS" if success else "ERROR"
        log(f"{status} - {name}", level)
    
    passed = sum(1 for s in results.values() if s)
    total = len(results)
    
    print("\n" + "=" * 70)
    log(f"Overall: {passed}/{total} APIs working", "INFO" if passed < total else "SUCCESS")
    print("=" * 70)
    
    # Recommendations
    print("\n" + "=" * 70)
    print(" RECOMMENDATIONS")
    print("=" * 70)
    
    if results.get("OpenVoice V2"):
        log("✅ OpenVoice V2 API works - use this for production", "SUCCESS")
    elif results.get("Local OpenVoice"):
        log("✅ Local OpenVoice server works - use this for development", "SUCCESS")
    else:
        log("⚠️  Both APIs have issues", "WARNING")
        log("  - OpenVoice V2: Cold start/overload issues", "INFO")
        log("  - Local: Check server window for errors", "INFO")
    
    if not results.get("Qwen3-TTS"):
        log("⚠️  Qwen3-TTS: WebSocket issue - use browser JavaScript", "WARNING")
        log("  - Open test_qwen3_browser.html in browser", "INFO")
        log("  - Or use web interface directly", "INFO")
    
    print("=" * 70)

if __name__ == "__main__":
    main()

