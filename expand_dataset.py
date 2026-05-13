#!C:\Users\Isaia\AppData\Local\Programs\Python\Python310\python.exe
"""
Expand Voice Dataset
====================
Batch downloads recent videos from the authorized YouTube channel to expand the voice cloning dataset.

Target Channel: https://www.youtube.com/channel/UCnDBsELI2OIaEI5yxA77HNA
Limit: Last 5 videos (configurable)
Quality: Best Audio (m4a/opus)

Usage:
    python expand_dataset.py --limit 5
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime

# Configuration
CHANNEL_URL = "https://www.youtube.com/channel/UCnDBsELI2OIaEI5yxA77HNA"
OUTPUT_DIR = Path("audio_samples")
PROCESSED_DIR = Path("processed_segments")

def log(msg, level="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{level}] {msg}")

def check_yt_dlp():
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        log("yt-dlp not found. Please install it: pip install yt-dlp", "ERROR")
        return False

def download_channel_videos(limit=5):
    """Download the most recent videos from the channel."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    log(f"Fetching last {limit} videos from channel...", "INFO")
    
    cmd = [
        "yt-dlp",
        "--extract-audio",
        "--audio-format", "m4a",
        "--audio-quality", "0",
        "--output", str(OUTPUT_DIR / "%(id)s_%(title)s.%(ext)s"),
        "--playlist-end", str(limit),
        "--no-write-playlist-metafiles",
        CHANNEL_URL
    ]
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8', 
            errors='replace'
        )
        
        # Stream output
        for line in process.stdout:
            line = line.strip()
            if line:
                if "[download]" in line and "%" in line:
                    # Don't spam progress bars
                    pass 
                else:
                    print(f"  {line}")
        
        process.wait()
        
        if process.returncode == 0:
            log("Download completed successfully.", "OK")
            return True
        else:
            log("Download finished with errors.", "WARN")
            return False
            
    except Exception as e:
        log(f"Download failed: {e}", "ERROR")
        return False

def process_audio():
    """Run the existing audio processor tool."""
    processor_script = Path("tools/audio_processor.py")
    
    if not processor_script.exists():
        log(f"Processor script not found: {processor_script}", "WARN")
        return False
        
    log("Starting audio segmentation (removing silence, formatting)...", "INFO")
    
    cmd = [
        sys.executable,
        str(processor_script),
        "--input", str(OUTPUT_DIR),
        "--output", str(PROCESSED_DIR)
    ]
    
    subprocess.run(cmd)

def main():
    parser = argparse.ArgumentParser(description="Expand Voice Dataset from YouTube Channel")
    parser.add_argument("--limit", type=int, default=5, help="Number of recent videos to download")
    parser.add_argument("--process", action="store_true", help="Run audio processor after download")
    
    args = parser.parse_args()
    
    log("="*60)
    log(" DATASET EXPANSION TOOL")
    log("="*60)
    log(f"Target: {CHANNEL_URL}")
    log(f"Limit:  Most recent {args.limit} videos")
    
    if check_yt_dlp():
        if download_channel_videos(args.limit):
            count = len(list(OUTPUT_DIR.glob("*.*")))
            log(f"Total raw samples in {OUTPUT_DIR}: {count}", "INFO")
            
            if args.process:
                process_audio()
            else:
                log("To process these files into training segments, run:", "INFO")
                log(f"python tools/audio_processor.py --input {OUTPUT_DIR} --output {PROCESSED_DIR}", "INFO")
    
    log("="*60)

if __name__ == "__main__":
    main()
