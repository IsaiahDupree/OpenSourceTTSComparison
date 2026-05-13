#!/usr/bin/env python3
"""
Test what actually works and generate audio
"""

import os
import sys
import time
import requests
from pathlib import Path
from gradio_client import Client

def log(message, level="INFO"):
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def test_local_generation():
    """Test local OpenVoice with actual generation"""
    print("\n" + "=" * 70)
    print(" TEST: Local OpenVoice - Audio Generation")
    print("=" * 70)
    
    base_url = "http://localhost:7860"
    
    # Check server
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code != 200:
            log("Server not responding", "ERROR")
            return False
    except:
        log("Server not running", "ERROR")
        return False
    
    log("Server is running", "SUCCESS")
    
    # Get audio file
    audio_path = Path("openvoice_deploy/resources/demo_speaker2.mp3")
    if not audio_path.exists():
        log(f"Audio file not found: {audio_path}", "ERROR")
        return False
    
    log(f"Using reference audio: {audio_path.name}", "SUCCESS")
    
    try:
        client = Client(base_url)
        log("Connected to API", "SUCCESS")
        
        log("Generating audio...")
        log("Text: 'Hello! This is a test of the local OpenVoice system.'")
        log("Style: 'default'")
        log("(This may take 30-60 seconds for first generation - model loading)")
        
        start_time = time.time()
        
        # Use submit with longer timeout
        job = client.submit(
            "Hello! This is a test of the local OpenVoice system.",
            "default",
            str(audio_path.resolve()),
            True,
            fn_index=1
        )
        
        log("Request submitted, waiting for result...")
        result = job.result(timeout=180)  # 3 minute timeout
        
        elapsed = time.time() - start_time
        
        info, audio_output, ref_audio = result
        
        log(f"SUCCESS! Generated in {elapsed:.1f}s", "SUCCESS")
        log(f"Info: {info[:100]}...", "INFO")
        log(f"Output Audio: {audio_output}", "SUCCESS")
        
        if audio_output and Path(audio_output).exists():
            file_size = os.path.getsize(audio_output) / 1024
            log(f"Audio file size: {file_size:.1f} KB", "INFO")
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        log(f"Failed: {error_msg}", "ERROR")
        
        if "HTTP 500" in error_msg or "500" in error_msg:
            log("Server returned HTTP 500 - check server window for errors", "WARNING")
        elif "timeout" in error_msg.lower():
            log("Request timed out - server may be processing", "WARNING")
        else:
            import traceback
            traceback.print_exc()
        
        return False

def test_qwen3_web_interface():
    """Test Qwen3-TTS web interface accessibility"""
    print("\n" + "=" * 70)
    print(" TEST: Qwen3-TTS Web Interface")
    print("=" * 70)
    
    base_url = "https://qwen-qwen3-tts-voice-design.hf.space"
    
    log("Testing web interface...")
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            log("Web interface is accessible", "SUCCESS")
            log(f"Visit: {base_url}", "INFO")
            log("You can test it manually in the browser", "INFO")
            return True
        else:
            log(f"HTTP {response.status_code}", "ERROR")
            return False
    except Exception as e:
        log(f"Failed: {e}", "ERROR")
        return False

def main():
    print("=" * 70)
    print(" Testing What Actually Works")
    print("=" * 70)
    
    results = {}
    
    # Test 1: Local generation
    results["Local OpenVoice Generation"] = test_local_generation()
    
    # Test 2: Qwen3 web interface
    results["Qwen3-TTS Web Interface"] = test_qwen3_web_interface()
    
    # Summary
    print("\n" + "=" * 70)
    print(" FINAL RESULTS")
    print("=" * 70)
    
    for name, success in results.items():
        status = "[PASS]" if success else "[FAIL]"
        level = "SUCCESS" if success else "ERROR"
        log(f"{status} - {name}", level)
    
    print("\n" + "=" * 70)
    print(" WHAT WORKS")
    print("=" * 70)
    
    if results.get("Local OpenVoice Generation"):
        log("✅ Local OpenVoice - FULLY WORKING", "SUCCESS")
        log("  - Server: http://localhost:7860", "INFO")
        log("  - API: Accessible via gradio_client", "INFO")
        log("  - Generation: Working", "INFO")
        log("  - Use: python start_server.py", "INFO")
    else:
        log("⚠️  Local OpenVoice - Server accessible but generation failed", "WARNING")
        log("  - Check server window for error messages", "INFO")
    
    if results.get("Qwen3-TTS Web Interface"):
        log("✅ Qwen3-TTS - Web Interface Works", "SUCCESS")
        log("  - URL: https://qwen-qwen3-tts-voice-design.hf.space", "INFO")
        log("  - API: WebSocket issues (use browser JavaScript)", "WARNING")
        log("  - Use: Open in browser and test manually", "INFO")
    
    print("=" * 70)

if __name__ == "__main__":
    main()

