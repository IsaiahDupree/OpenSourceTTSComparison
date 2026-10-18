#!/usr/bin/env python3
"""
Restart server with fixed code and run tests automatically
"""

import os
import sys
import time
import subprocess
import requests
import signal
from pathlib import Path

def log(message, level="INFO"):
    """Console logging"""
    import datetime
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] @pwsh [{level}] {message}")

def kill_existing_server():
    """Kill any existing server on port 7860"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 7860))
        if result == 0:
            log("Found existing server, it will be replaced", "INFO")
            # On Windows, we can't easily kill by port, so just note it
            log("Please stop the existing server manually (Ctrl+C in its terminal)", "INFO")
            log("Or wait 10 seconds and the new server will start...", "INFO")
            time.sleep(10)
    except:
        pass

def start_server():
    """Start the server"""
    log("Starting OpenVoice server with fixed code...", "INFO")
    script_path = Path(__file__).parent / "start_server.py"
    process = subprocess.Popen(
        [sys.executable, str(script_path)],
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
    )
    return process

def wait_for_server(max_wait=60):
    """Wait for server to be ready"""
    log("Waiting for server to start...", "INFO")
    for i in range(max_wait):
        try:
            response = requests.get("http://localhost:7860", timeout=2)
            if response.status_code == 200:
                log(f"Server is ready! (waited {i+1}s)", "SUCCESS")
                time.sleep(3)  # Give it a moment to fully initialize
                return True
        except:
            pass
        time.sleep(1)
        if (i + 1) % 5 == 0:
            log(f"Still waiting... ({i+1}s)", "INFO")
    return False

def run_tests():
    """Run tests"""
    log("Running automated tests...", "INFO")
    script_path = Path(__file__).parent / "run_all_tests.py"
    result = subprocess.run([sys.executable, str(script_path)], text=True)
    return result.returncode

def main():
    log("=" * 70, "TEST")
    log(" Restart Server and Run Tests", "TEST")
    log("=" * 70, "TEST")
    log("", "INFO")
    
    # Kill existing server
    kill_existing_server()
    
    # Start server
    process = start_server()
    log("Server starting in new window...", "INFO")
    
    # Wait for server
    if not wait_for_server():
        log("Server failed to start", "ERROR")
        return 1
    
    # Run tests
    log("", "INFO")
    exit_code = run_tests()
    
    log("", "INFO")
    log("=" * 70, "TEST")
    log("Test run complete. Server is still running.", "INFO")
    log("Stop it with Ctrl+C in the server window.", "INFO")
    log("=" * 70, "TEST")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())

