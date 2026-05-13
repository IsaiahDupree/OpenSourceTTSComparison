#!/usr/bin/env python3
"""
yt-dlp Downloader (2025)

A simple wrapper around yt-dlp using the most reliable and proven commands
for downloading YouTube videos in 2025.

This script handles:
- Audio-only downloads
- Video downloads (with merged streams)
- Playlist downloads with proper folder structure
- Automatic yt-dlp updates
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd):
    """Run a command and return True if successful"""
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        return False


def update_ytdlp():
    """Update yt-dlp to the latest version"""
    print("Updating yt-dlp...")
    return run_command(["yt-dlp", "-U"])


def install_ytdlp():
    """Attempt to install yt-dlp using pip"""
    print("Attempting to install yt-dlp...")
    return run_command([sys.executable, "-m", "pip", "install", "-U", "yt-dlp[default]"])


def check_ytdlp():
    """Check if yt-dlp is installed and working"""
    try:
        subprocess.run(["yt-dlp", "--version"], check=True, stdout=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("yt-dlp not found or not working correctly.")
        return False


def check_ffmpeg():
    """Check if FFmpeg is installed"""
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.PIPE)
        print("✅ FFmpeg is installed (recommended for merging streams)")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ FFmpeg not found - some features may not work correctly")
        print("ℹ️ Install FFmpeg from: https://ffmpeg.org/download.html")
        return False


def download_video(url, output_dir="downloads", download_type="audio", playlist=False):
    """Download video or audio using the proven yt-dlp commands"""
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Base command
    cmd = ["yt-dlp"]
    
    # Format options
    if download_type == "video":
        # Best MP4 with merged streams (needs FFmpeg)
        cmd.extend(["-S", "res,ext:mp4:m4a", "-f", "bv*+ba/b"])
    else:
        # Audio-only M4A
        cmd.extend(["-f", "bestaudio[ext=m4a]/bestaudio"])
    
    # Output template
    if playlist:
        output_template = os.path.join(output_dir, "%(uploader)s/%(playlist)s/%(playlist_index)s - %(title).200B.%(ext)s")
    else:
        output_template = os.path.join(output_dir, "%(id)s_%(title).200B.%(ext)s")
    
    cmd.extend(["-o", output_template])
    
    # Add URL
    cmd.append(url)
    
    # Print command
    print(f"Running: {' '.join(cmd)}")
    
    # Execute
    return run_command(cmd)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Download YouTube videos using proven yt-dlp commands",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download audio only (M4A)
  python yt_dlp_downloader.py https://www.youtube.com/watch?v=L6yKk7EQYZc
  
  # Download best MP4 video
  python yt_dlp_downloader.py -t video https://www.youtube.com/watch?v=L6yKk7EQYZc
  
  # Download playlist with folder structure
  python yt_dlp_downloader.py -p https://www.youtube.com/playlist?list=XXXX
  
  # Update yt-dlp and download
  python yt_dlp_downloader.py -u https://www.youtube.com/watch?v=L6yKk7EQYZc
"""
    )
    
    parser.add_argument("url", help="YouTube URL to download")
    parser.add_argument("-t", "--type", choices=["audio", "video"], default="audio",
                       help="Download type: audio (default) or video")
    parser.add_argument("-o", "--output-dir", default="custom_output",
                       help="Output directory for downloads")
    parser.add_argument("-p", "--playlist", action="store_true",
                       help="Create uploader/playlist folder structure")
    parser.add_argument("-u", "--update", action="store_true",
                       help="Update yt-dlp before downloading")
    
    args = parser.parse_args()
    
    # Check for yt-dlp
    if not check_ytdlp():
        if not install_ytdlp():
            print("\nPlease install yt-dlp manually:")
            print("  pip install -U 'yt-dlp[default]'")
            print("  or download from: https://github.com/yt-dlp/yt-dlp#installation")
            return 1
    
    # Update yt-dlp if requested
    if args.update:
        if not update_ytdlp():
            print("Failed to update yt-dlp")
            return 1
    
    # Check for FFmpeg (recommended but not required)
    check_ffmpeg()
    
    print(f"🎬 Downloading {'video' if args.type == 'video' else 'audio'} from: {args.url}")
    print(f"📂 Output directory: {args.output_dir}")
    print("=" * 60)
    
    # Download
    if download_video(args.url, args.output_dir, args.type, args.playlist):
        print("\n✅ Download completed successfully!")
        return 0
    else:
        print("\n❌ Download failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
