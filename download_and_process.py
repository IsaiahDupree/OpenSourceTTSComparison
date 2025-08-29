#!/usr/bin/env python3
"""
Simple script to download YouTube videos and process audio
"""

import subprocess
import sys
import os
from pathlib import Path

# Video IDs extracted from the URLs
video_ids = [
    "Uh34kDEF500",
    "KpuEkonkuiU", 
    "JXHPIahTayU",
    "w4sarAE9h9I",
    "0YWpkJkbXxs"
]

def download_videos():
    """Download videos using yt-dlp"""
    audio_dir = Path("audio_samples")
    audio_dir.mkdir(exist_ok=True)
    
    for video_id in video_ids:
        print(f"Downloading {video_id}...")
        try:
            cmd = [
                "yt-dlp",
                "--extract-audio",
                "--audio-format", "mp3",
                "--audio-quality", "0",
                "--output", f"audio_samples/{video_id}.%(ext)s",
                f"https://www.youtube.com/watch?v={video_id}"
            ]
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"✅ Downloaded {video_id}")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to download {video_id}: {e}")
            print(f"Error: {e.stderr}")

def process_audio():
    """Process downloaded audio with our tool"""
    print("Processing audio files...")
    try:
        cmd = [
            sys.executable,
            "tools/audio_processor.py",
            "--input", "audio_samples",
            "--output", "processed_segments"
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Audio processing completed")
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Audio processing failed: {e}")
        print(f"Error: {e.stderr}")

if __name__ == "__main__":
    print("🎬 Downloading YouTube videos...")
    download_videos()
    
    print("\n🎵 Processing audio segments...")
    process_audio()
    
    print("\n🎉 Complete! Ready for TTS benchmarking.")
    print("Next: python benchmark/run_all_tests.py")
