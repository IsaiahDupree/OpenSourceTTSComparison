#!/usr/bin/env python3
"""
YouTube Video Downloader and Audio Processor

Downloads YouTube videos, extracts audio, and processes them for TTS benchmarking.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import List
import argparse
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class YouTubeAudioProcessor:
    """Downloads YouTube videos and processes audio for TTS benchmarking."""
    
    def __init__(self, output_dir: str = "audio_samples"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.temp_dir = Path("temp_downloads")
        self.temp_dir.mkdir(exist_ok=True)
        
    def install_yt_dlp(self) -> bool:
        """Install yt-dlp for YouTube downloading."""
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
            logger.info("✅ yt-dlp installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install yt-dlp: {e}")
            return False
    
    def extract_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL."""
        if "youtube.com/video/" in url:
            return url.split("/video/")[1].split("/")[0]
        elif "youtu.be/" in url:
            return url.split("youtu.be/")[1].split("?")[0]
        elif "v=" in url:
            return url.split("v=")[1].split("&")[0]
        else:
            # Assume it's already a video ID
            return url
    
    def download_audio(self, video_url: str) -> str:
        """Download audio from YouTube video."""
        video_id = self.extract_video_id(video_url)
        output_path = self.output_dir / f"{video_id}.mp3"
        
        if output_path.exists():
            logger.info(f"Audio already exists: {output_path}")
            return str(output_path)
        
        try:
            # Use yt-dlp to download audio only
            cmd = [
                "yt-dlp",
                "--extract-audio",
                "--audio-format", "mp3",
                "--audio-quality", "0",  # Best quality
                "--output", str(self.output_dir / "%(id)s.%(ext)s"),
                f"https://www.youtube.com/watch?v={video_id}"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"✅ Downloaded audio: {output_path}")
            return str(output_path)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to download {video_id}: {e}")
            logger.error(f"Error output: {e.stderr}")
            return None
    
    def process_youtube_urls(self, urls: List[str]) -> List[str]:
        """Process multiple YouTube URLs."""
        downloaded_files = []
        
        for url in urls:
            logger.info(f"Processing: {url}")
            audio_file = self.download_audio(url)
            if audio_file:
                downloaded_files.append(audio_file)
        
        return downloaded_files
    
    def run_audio_processor(self, audio_files: List[str]) -> str:
        """Run our custom audio processor on downloaded files."""
        if not audio_files:
            logger.error("No audio files to process")
            return None
        
        # Create temporary directory with audio files
        temp_audio_dir = Path("temp_audio_input")
        temp_audio_dir.mkdir(exist_ok=True)
        
        # Copy files to temp directory for processing
        for audio_file in audio_files:
            src = Path(audio_file)
            dst = temp_audio_dir / src.name
            if src.exists():
                import shutil
                shutil.copy2(src, dst)
        
        try:
            # Run our audio processor
            cmd = [
                sys.executable,
                "tools/audio_processor.py",
                "--input", str(temp_audio_dir),
                "--output", "processed_segments",
                "--target-duration", "10.0"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info("✅ Audio processing completed")
            logger.info(result.stdout)
            
            # Clean up temp directory
            import shutil
            shutil.rmtree(temp_audio_dir)
            
            return "processed_segments"
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Audio processing failed: {e}")
            logger.error(f"Error output: {e.stderr}")
            return None
    
    def cleanup_original_files(self, audio_files: List[str]):
        """Clean up original downloaded files (optional)."""
        for audio_file in audio_files:
            try:
                Path(audio_file).unlink()
                logger.info(f"🗑️ Deleted: {audio_file}")
            except Exception as e:
                logger.warning(f"Could not delete {audio_file}: {e}")


def main():
    parser = argparse.ArgumentParser(description='Download YouTube videos and process audio for TTS benchmarking')
    parser.add_argument('urls', nargs='+', help='YouTube URLs to download')
    parser.add_argument('--output-dir', default='audio_samples', help='Output directory for audio files')
    parser.add_argument('--keep-originals', action='store_true', help='Keep original downloaded files')
    parser.add_argument('--install-deps', action='store_true', help='Install required dependencies')
    
    args = parser.parse_args()
    
    processor = YouTubeAudioProcessor(args.output_dir)
    
    # Install dependencies if requested
    if args.install_deps:
        if not processor.install_yt_dlp():
            logger.error("Failed to install dependencies")
            return 1
    
    # Process URLs
    logger.info(f"Processing {len(args.urls)} YouTube URLs...")
    downloaded_files = processor.process_youtube_urls(args.urls)
    
    if not downloaded_files:
        logger.error("No files were downloaded successfully")
        return 1
    
    logger.info(f"Successfully downloaded {len(downloaded_files)} audio files")
    
    # Process audio with our custom tool
    logger.info("Running audio processor to extract best segments...")
    processed_dir = processor.run_audio_processor(downloaded_files)
    
    if processed_dir:
        logger.info(f"✅ Audio processing complete! Best segments saved to: {processed_dir}/")
        
        # Clean up original files if not keeping them
        if not args.keep_originals:
            processor.cleanup_original_files(downloaded_files)
        
        print(f"\n🎉 Success! Best audio segments ready for TTS benchmarking:")
        print(f"📁 Processed segments: {processed_dir}/")
        print(f"📊 Check {processed_dir}/processing_results.json for analysis")
        print(f"\nNext step: Run TTS benchmarks with:")
        print(f"python benchmark/run_all_tests.py")
        
    else:
        logger.error("Audio processing failed")
        return 1
    
    return 0


if __name__ == "__main__":
    # Predefined YouTube URLs from the user
    youtube_urls = [
        "https://studio.youtube.com/video/Uh34kDEF500/",
        "https://studio.youtube.com/video/KpuEkonkuiU/", 
        "https://studio.youtube.com/video/JXHPIahTayU/",
        "https://studio.youtube.com/video/w4sarAE9h9I/",
        "https://studio.youtube.com/video/0YWpkJkbXxs/"
    ]
    
    # Check if only --install-deps is provided
    if len(sys.argv) == 2 and "--install-deps" in sys.argv:
        processor = YouTubeAudioProcessor()
        processor.install_yt_dlp()
        print("✅ Dependencies installed. Now run without --install-deps to download videos.")
        exit(0)
    
    # If no URLs provided, use predefined ones
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and "--install-deps" in sys.argv):
        sys.argv = [sys.argv[0]] + youtube_urls
        if "--install-deps" in sys.argv:
            sys.argv.append("--install-deps")
    
    exit(main())
