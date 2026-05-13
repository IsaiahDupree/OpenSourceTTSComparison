#!/usr/bin/env python3
"""
Automated test runner - no manual input required
Starts server, waits, runs tests, shows summary
"""

import os
import sys
import time
import subprocess
import requests
from pathlib import Path
from gradio_client import Client

def log(message, level="INFO"):
    """Console logging with @pwsh format"""
    import datetime
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] @pwsh [{level}] {message}")

def check_server_running():
    """Check if server is already running"""
    try:
        response = requests.get("http://localhost:7860", timeout=2)
        return response.status_code == 200
    except:
        return False

def start_server_background():
    """Start server in background"""
    log("Starting OpenVoice server in background...", "INFO")
    script_path = Path(__file__).parent / "start_server.py"
    process = subprocess.Popen(
        [sys.executable, str(script_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
    )
    return process

def wait_for_server(max_wait=60):
    """Wait for server to be ready"""
    log("Waiting for server to start...", "INFO")
    for i in range(max_wait):
        if check_server_running():
            log(f"Server is ready! (waited {i+1}s)", "SUCCESS")
            return True
        time.sleep(1)
        if (i + 1) % 5 == 0:
            log(f"Still waiting... ({i+1}s)", "INFO")
    log("Server did not start in time", "ERROR")
    return False

def run_tests():
    """Run the test suite"""
    log("Running test suite...", "INFO")
    script_path = Path(__file__).parent / "run_all_tests.py"
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode

def main():
    log("=" * 70, "TEST")
    log(" Automated OpenVoice Test Runner", "TEST")
    log("=" * 70, "TEST")
    log("", "INFO")
    
    # Check if server is already running
    if check_server_running():
        log("Server is already running, skipping startup", "INFO")
    else:
        log("Server not detected, starting it...", "INFO")
        process = start_server_background()
        if not wait_for_server():
            log("Failed to start server", "ERROR")
            return 1
        log("Server started successfully", "SUCCESS")
        time.sleep(2)  # Give it a moment to fully initialize
    
    # Run tests
    log("", "INFO")
    exit_code = run_tests()
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())

