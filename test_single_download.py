#!/usr/bin/env python3
"""
Test downloading a single YouTube video to debug issues
"""

import yt_dlp
import os
from pathlib import Path

def test_single_download():
    """Test downloading one video with minimal options"""
    
    # Create output directory
    output_dir = Path("temp_downloads")
    output_dir.mkdir(exist_ok=True)
    
    # Simple yt-dlp options
    ydl_opts = {
        'outtmpl': str(output_dir / '%(title)s.%(ext)s'),
        'format': 'best[height<=480]/best',  # Lower quality for faster download
    }
    
    # Test URL - using a short, simple video
    test_url = "https://www.youtube.com/watch?v=Uh34kDEF500"
    
    print(f"🎬 Testing download of: {test_url}")
    print(f"📁 Output directory: {output_dir}")
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Get video info first
            print("Getting video info...")
            info = ydl.extract_info(test_url, download=False)
            
            title = info.get('title', 'Unknown')
            duration = info.get('duration', 0)
            
            print(f"Title: {title}")
            print(f"Duration: {duration} seconds")
            
            # Download the video
            print("Starting download...")
            ydl.download([test_url])
            
            print("✅ Download completed!")
            
            # Check what files were created
            files = list(output_dir.iterdir())
            print(f"📁 Files created: {len(files)}")
            for file in files:
                print(f"  - {file.name} ({file.stat().st_size} bytes)")
            
            return True
            
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False

if __name__ == "__main__":
    success = test_single_download()
    if success:
        print("\n🎉 Single download test successful!")
    else:
        print("\n❌ Single download test failed")
