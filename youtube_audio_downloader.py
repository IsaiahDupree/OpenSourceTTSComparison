#!/usr/bin/env python3
"""
YouTube Audio Downloader Program

Downloads YouTube videos and extracts audio using yt-dlp Python library.
"""

import yt_dlp
import os
import sys
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class YouTubeAudioDownloader:
    """Downloads YouTube videos and extracts audio."""
    
    def __init__(self, output_dir: str = "audio_samples"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Configure yt-dlp options - simplified to avoid FFmpeg issues
        self.ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'outtmpl': str(self.output_dir / '%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
            'ignoreerrors': True,
        }
    
    def download_video(self, url: str) -> bool:
        """Download single video and extract audio."""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                # Get video info first
                info = ydl.extract_info(url, download=False)
                video_id = info.get('id', 'unknown')
                title = info.get('title', 'Unknown Title')
                
                logger.info(f"Downloading: {title} ({video_id})")
                
                # Download the video
                ydl.download([url])
                
                logger.info(f"✅ Successfully downloaded: {title}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to download {url}: {e}")
            return False
    
    def download_multiple_videos(self, urls: list) -> dict:
        """Download multiple videos."""
        results = {"successful": [], "failed": []}
        
        for i, url in enumerate(urls, 1):
            logger.info(f"\n[{i}/{len(urls)}] Processing: {url}")
            
            if self.download_video(url):
                results["successful"].append(url)
            else:
                results["failed"].append(url)
        
        return results
    
    def get_downloaded_files(self) -> list:
        """Get list of downloaded audio files."""
        audio_extensions = ['.mp3', '.wav', '.m4a', '.ogg', '.webm', '.mp4']
        files = []
        
        for file in self.output_dir.iterdir():
            if file.suffix.lower() in audio_extensions:
                files.append(str(file))
        
        return files


def main():
    # YouTube URLs from your request
    youtube_urls = [
        "https://www.youtube.com/watch?v=Uh34kDEF500",
        "https://www.youtube.com/watch?v=KpuEkonkuiU", 
        "https://www.youtube.com/watch?v=JXHPIahTayU",
        "https://www.youtube.com/watch?v=w4sarAE9h9I",
        "https://www.youtube.com/watch?v=0YWpkJkbXxs"
    ]
    
    print("🎬 YouTube Audio Downloader")
    print("=" * 50)
    
    # Create downloader
    downloader = YouTubeAudioDownloader()
    
    # Download all videos
    print(f"Downloading {len(youtube_urls)} videos...")
    results = downloader.download_multiple_videos(youtube_urls)
    
    # Print results
    print(f"\n📊 Download Results:")
    print(f"✅ Successful: {len(results['successful'])}")
    print(f"❌ Failed: {len(results['failed'])}")
    
    if results['failed']:
        print(f"\nFailed URLs:")
        for url in results['failed']:
            print(f"  - {url}")
    
    # Get downloaded files
    downloaded_files = downloader.get_downloaded_files()
    print(f"\n📁 Downloaded {len(downloaded_files)} audio files:")
    for file in downloaded_files:
        print(f"  - {Path(file).name}")
    
    # Process audio with our custom tool
    if downloaded_files:
        print(f"\n🎵 Processing audio segments...")
        try:
            import subprocess
            cmd = [
                sys.executable,
                "tools/audio_processor.py",
                "--input", "audio_samples",
                "--output", "processed_segments"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print("✅ Audio processing completed!")
            print(result.stdout)
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Audio processing failed: {e}")
            print(f"Error: {e.stderr}")
        except Exception as e:
            print(f"❌ Error running audio processor: {e}")
    
    print(f"\n🎉 Complete! Audio files ready for TTS benchmarking.")
    print(f"📁 Raw audio: audio_samples/")
    print(f"📁 Processed segments: processed_segments/")
    print(f"\nNext step: python benchmark/run_all_tests.py")


if __name__ == "__main__":
    main()
