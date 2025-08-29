#!/usr/bin/env python3
"""
Test pytube with a single video to debug issues
"""

from pytube import YouTube
import os
from pathlib import Path

def test_single_video():
    """Test downloading one video"""
    
    # Create output directory
    output_dir = Path("audio_samples")
    output_dir.mkdir(exist_ok=True)
    
    # Test with a short video
    test_url = "https://www.youtube.com/watch?v=Uh34kDEF500"
    
    print(f"🎬 Testing pytube with: {test_url}")
    
    try:
        # Create YouTube object
        yt = YouTube(test_url)
        
        print(f"Title: {yt.title}")
        print(f"Duration: {yt.length} seconds")
        print(f"Views: {yt.views:,}")
        
        # List available streams
        print("\nAvailable audio streams:")
        audio_streams = yt.streams.filter(only_audio=True)
        for i, stream in enumerate(audio_streams):
            print(f"  {i+1}. {stream}")
        
        if audio_streams:
            # Download the first audio stream
            audio_stream = audio_streams.first()
            print(f"\nDownloading: {audio_stream}")
            
            output_path = audio_stream.download(
                output_path=str(output_dir),
                filename="test_audio.mp4"
            )
            
            print(f"✅ Downloaded to: {output_path}")
            
            # Check file size
            file_size = Path(output_path).stat().st_size
            print(f"File size: {file_size:,} bytes")
            
            return True
        else:
            print("❌ No audio streams available")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_single_video()
    if success:
        print("\n🎉 Pytube test successful!")
    else:
        print("\n❌ Pytube test failed")
