#!/usr/bin/env python3
"""
Run OpenVoice locally
"""

import sys
import os
from pathlib import Path

# Add openvoice_deploy to path
sys.path.insert(0, str(Path(__file__).parent / "openvoice_deploy"))

# Change to openvoice_deploy directory
os.chdir(Path(__file__).parent / "openvoice_deploy")

# Import and run
from app import demo

if __name__ == "__main__":
    print("=" * 70)
    print(" Starting OpenVoice locally...")
    print("=" * 70)
    print("\nOpen your browser to: http://localhost:7860")
    print("Press Ctrl+C to stop\n")
    
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
