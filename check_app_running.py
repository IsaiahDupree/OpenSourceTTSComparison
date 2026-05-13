#!/usr/bin/env python3
"""Check if OpenVoice app is running on localhost:7860"""

import socket
import time
import requests

def check_port(host, port):
    """Check if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def check_http(url):
    """Check if HTTP server is responding"""
    try:
        response = requests.get(url, timeout=2)
        return response.status_code == 200
    except:
        return False

print("Checking if OpenVoice is running...")
print("=" * 70)

# Check port
if check_port("localhost", 7860):
    print("✅ Port 7860 is open")
    
    # Check HTTP
    if check_http("http://localhost:7860"):
        print("✅ HTTP server is responding")
        print("\n🎉 OpenVoice is running!")
        print("Open: http://localhost:7860")
    else:
        print("⚠️  Port is open but HTTP not responding yet")
        print("   The app may still be starting...")
else:
    print("❌ Port 7860 is not open")
    print("\nThe app is not running. Start it with:")
    print("  python run_openvoice_local.py")
    print("\nOr:")
    print("  cd openvoice_deploy")
    print("  python app.py")

