#!/usr/bin/env python3
"""
YouTube Audio Downloader using pytube library
More reliable than yt-dlp for simple audio extraction
"""

import os
import sys
from pathlib import Path
from pytube import YouTube
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PytubeDownloader:
    """Downloads YouTube videos and extracts audio using pytube"""
    
    def __init__(self, output_dir: str = "audio_samples"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def download_audio(self, url: str) -> bool:
        """Download audio from a single YouTube video"""
        try:
            # Create YouTube object
            yt = YouTube(url)
            
            # Get video info
            title = yt.title
            video_id = yt.video_id
            duration = yt.length
            
            logger.info(f"Downloading: {title} ({video_id}) - {duration}s")
            
            # Prefer M4A (audio/mp4) if available, else best available audio
            audio_stream = (
                yt.streams.filter(only_audio=True, mime_type="audio/mp4").order_by("abr").desc().first()
                or yt.streams.filter(only_audio=True, subtype="m4a").order_by("abr").desc().first()
                or yt.streams.filter(only_audio=True).order_by("abr").desc().first()
            )
            
            if not audio_stream:
                logger.error(f"No audio stream found for {url}")
                return False
            
            # Clean filename for Windows compatibility
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            # Determine extension
            if getattr(audio_stream, 'mime_type', None) and 'audio/mp4' in audio_stream.mime_type:
                ext = 'm4a'
            else:
                ext = getattr(audio_stream, 'subtype', None) or 'mp4'
            filename = f"{video_id}_{safe_title[:50]}.{ext}"
            
            # Download the audio
            output_path = audio_stream.download(
                output_path=str(self.output_dir),
                filename=filename
            )
            
            logger.info(f"✅ Downloaded: {Path(output_path).name} | itag={audio_stream.itag} | abr={getattr(audio_stream, 'abr', 'n/a')} | mime={getattr(audio_stream, 'mime_type', 'n/a')}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to download {url}: {e}")
            return False
    
    def download_multiple(self, urls: list) -> dict:
        """Download multiple YouTube videos"""
        results = {"successful": [], "failed": []}
        
        for i, url in enumerate(urls, 1):
            logger.info(f"\n[{i}/{len(urls)}] Processing: {url}")
            
            if self.download_audio(url):
                results["successful"].append(url)
            else:
                results["failed"].append(url)
        
        return results
    
    def get_downloaded_files(self) -> list:
        """Get list of downloaded audio files"""
        audio_extensions = ['.mp4', '.mp3', '.m4a', '.webm']
        files = []
        
        for file in self.output_dir.iterdir():
            if file.suffix.lower() in audio_extensions:
                files.append(str(file))
        
        return files

def main():
    """Main function to download YouTube audio samples"""
    
    # YouTube URLs for TTS comparison
    youtube_urls = [
        "https://www.youtube.com/watch?v=Uh34kDEF500",
        "https://www.youtube.com/watch?v=KpuEkonkuiU", 
        "https://www.youtube.com/watch?v=JXHPIahTayU",
        "https://www.youtube.com/watch?v=w4sarAE9h9I",
        "https://www.youtube.com/watch?v=0YWpkJkbXxs"
    ]
    
    print("🎬 YouTube Audio Downloader (pytube)")
    print("=" * 50)
    
    # Create downloader
    downloader = PytubeDownloader()
    
    # Download all videos
    print(f"Downloading {len(youtube_urls)} videos...")
    results = downloader.download_multiple(youtube_urls)
    
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
        file_path = Path(file)
        file_size = file_path.stat().st_size
        print(f"  - {file_path.name} ({file_size:,} bytes)")
    
    if downloaded_files:
        print(f"\n🎉 Success! Audio files ready for processing.")
        print(f"Next step: python tools\\audio_processor.py --input audio_samples --output processed_segments")
    else:
        print(f"\n❌ No audio files downloaded. Check network connection and URLs.")
    
    return len(downloaded_files) > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
