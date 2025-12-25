#!/usr/bin/env python3
"""
Modular YouTube Audio Downloader

A flexible, reusable library for downloading YouTube videos and extracting audio.
Can be used both as a command-line tool or imported into other projects.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Union, Optional
import argparse
import json

# Configure logging
logger = logging.getLogger(__name__)

class YouTubeDownloader:
    """
    Core YouTube downloader class that handles downloading videos and extracting audio.
    
    This class is designed to be used as a library and imported into other projects.
    """
    
    def __init__(self, 
                 output_dir: str = "audio_samples",
                 audio_format: str = "m4a",
                 quality: str = "0",
                 use_yt_dlp: bool = True):
        """
        Initialize the YouTube downloader.
        
        Args:
            output_dir: Directory to save downloaded audio files
            audio_format: Format to save audio in (m4a, mp3, wav, etc.)
            quality: Audio quality (0 is best)
            use_yt_dlp: Whether to use yt-dlp (True) or youtube-dl (False)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.audio_format = audio_format
        self.quality = quality
        self.downloader = "yt-dlp" if use_yt_dlp else "youtube-dl"
        
    def extract_video_id(self, url: str) -> str:
        """
        Extract video ID from YouTube URL.
        
        Args:
            url: YouTube URL or video ID
            
        Returns:
            YouTube video ID
        """
        if "youtube.com/video/" in url:
            return url.split("/video/")[1].split("/")[0]
        elif "youtube.com/watch" in url and "v=" in url:
            return url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in url:
            return url.split("youtu.be/")[1].split("?")[0]
        elif "studio.youtube.com/video/" in url:
            return url.split("studio.youtube.com/video/")[1].split("/")[0]
        else:
            # Assume it's already a video ID
            return url
    
    def ensure_dependencies(self) -> bool:
        """
        Make sure required dependencies are installed.
        
        Returns:
            True if dependencies are installed, False otherwise
        """
        try:
            subprocess.check_call(
                [self.downloader, "--version"], 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            logger.info(f"✅ {self.downloader} is already installed")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.info(f"{self.downloader} not found, attempting to install...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", self.downloader])
                logger.info(f"✅ {self.downloader} installed successfully")
                return True
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Failed to install {self.downloader}: {e}")
                return False
    
    def download_audio(self, video_url: str, 
                      output_path: Optional[str] = None,
                      include_video_id: bool = True,
                      include_title: bool = False) -> Optional[str]:
        """
        Download audio from YouTube video.
        
        Args:
            video_url: YouTube URL or video ID
            output_path: Optional custom output path
            include_video_id: Whether to include video ID in filename
            include_title: Whether to include video title in filename
            
        Returns:
            Path to downloaded audio file or None if download failed
        """
        video_id = self.extract_video_id(video_url)
        
        # Determine output template
        if output_path:
            output_template = output_path
        else:
            if include_title and include_video_id:
                output_template = str(self.output_dir / "%(id)s_%(title)s.%(ext)s")
            elif include_title:
                output_template = str(self.output_dir / "%(title)s.%(ext)s")
            elif include_video_id:
                output_template = str(self.output_dir / "%(id)s.%(ext)s") 
            else:
                # Use just the numeric hash of the video ID to anonymize
                import hashlib
                filename = hashlib.md5(video_id.encode()).hexdigest()[:10]
                output_template = str(self.output_dir / f"{filename}.%(ext)s")
        
        try:
            # Build command
            cmd = [
                self.downloader,
                "--extract-audio",
                "--audio-format", self.audio_format,
                "--audio-quality", self.quality,
                "--output", output_template,
                f"https://www.youtube.com/watch?v={video_id}"
            ]
            
            # Run the command
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Find the output file
            if include_title:
                # Need to scan directory for new files
                before_files = set(self.output_dir.glob(f"*{video_id}*.{self.audio_format}"))
                after_files = set(self.output_dir.glob(f"*{video_id}*.{self.audio_format}"))
                new_files = after_files - before_files
                if new_files:
                    output_file = new_files.pop()
                else:
                    # Try to find by just looking at recent files
                    files = list(self.output_dir.glob(f"*.{self.audio_format}"))
                    if files:
                        output_file = max(files, key=lambda p: p.stat().st_mtime)
                    else:
                        output_file = None
            else:
                # We can predict the filename
                if include_video_id:
                    output_file = self.output_dir / f"{video_id}.{self.audio_format}"
                else:
                    # Use hash
                    import hashlib
                    filename = hashlib.md5(video_id.encode()).hexdigest()[:10]
                    output_file = self.output_dir / f"{filename}.{self.audio_format}"
            
            if output_file and output_file.exists():
                logger.info(f"✅ Downloaded audio: {output_file}")
                return str(output_file)
            else:
                logger.error(f"✅ Download completed but couldn't locate output file")
                # Return any file that looks like it might be the right one
                potential_files = list(self.output_dir.glob(f"*.{self.audio_format}"))
                if potential_files:
                    newest_file = max(potential_files, key=lambda p: p.stat().st_mtime)
                    logger.info(f"Using most recently modified file: {newest_file}")
                    return str(newest_file)
                return None
                
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to download {video_id}: {e}")
            logger.error(f"Error output: {e.stderr}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error downloading {video_id}: {e}")
            return None
    
    def download_multiple(self, video_urls: List[str], 
                         include_video_id: bool = True,
                         include_title: bool = False) -> Dict[str, List[str]]:
        """
        Download audio from multiple YouTube videos.
        
        Args:
            video_urls: List of YouTube URLs or video IDs
            include_video_id: Whether to include video ID in filename
            include_title: Whether to include video title in filename
            
        Returns:
            Dictionary with "successful" and "failed" lists of URLs
        """
        results = {"successful": [], "failed": [], "output_files": []}
        
        for i, url in enumerate(video_urls, 1):
            logger.info(f"[{i}/{len(video_urls)}] Processing: {url}")
            
            output_file = self.download_audio(
                url, 
                include_video_id=include_video_id,
                include_title=include_title
            )
            
            if output_file:
                results["successful"].append(url)
                results["output_files"].append(output_file)
            else:
                results["failed"].append(url)
        
        return results
    
    def get_downloaded_files(self) -> List[str]:
        """
        Get list of downloaded audio files.
        
        Returns:
            List of paths to downloaded audio files
        """
        audio_extensions = ['.mp3', '.wav', '.m4a', '.ogg', '.webm', '.mp4', '.flac']
        files = []
        
        for file in self.output_dir.iterdir():
            if file.suffix.lower() in audio_extensions:
                files.append(str(file))
        
        return files


def download_from_command_line():
    """Command-line interface for downloading YouTube videos."""
    parser = argparse.ArgumentParser(description='Download audio from YouTube videos')
    
    parser.add_argument('urls', nargs='*', help='YouTube URLs to download')
    parser.add_argument('-i', '--input-file', help='File containing YouTube URLs (one per line)')
    parser.add_argument('-o', '--output-dir', default='audio_samples', help='Output directory')
    parser.add_argument('-f', '--format', default='m4a', help='Audio format')
    parser.add_argument('-q', '--quality', default='0', help='Audio quality (0 is best)')
    parser.add_argument('--no-video-id', action='store_true', help="Don't include video ID in filename")
    parser.add_argument('--include-title', action='store_true', help="Include video title in filename")
    parser.add_argument('--install-deps', action='store_true', help='Install required dependencies')
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Create downloader
    downloader = YouTubeDownloader(
        output_dir=args.output_dir,
        audio_format=args.format,
        quality=args.quality
    )
    
    # Install dependencies if requested
    if args.install_deps:
        if not downloader.ensure_dependencies():
            logger.error("Failed to install dependencies")
            return 1
        if len(args.urls) == 0 and not args.input_file:
            print("✅ Dependencies installed. Run again with YouTube URLs to download.")
            return 0
    
    # Get URLs from arguments or input file
    urls = []
    
    if args.urls:
        urls.extend(args.urls)
    
    if args.input_file:
        try:
            with open(args.input_file, 'r') as f:
                file_urls = [line.strip() for line in f if line.strip()]
                urls.extend(file_urls)
        except Exception as e:
            logger.error(f"Error reading input file: {e}")
    
    if not urls:
        parser.print_help()
        return 1
    
    # Download videos
    logger.info(f"Downloading {len(urls)} videos...")
    results = downloader.download_multiple(
        urls, 
        include_video_id=not args.no_video_id,
        include_title=args.include_title
    )
    
    # Print results
    print(f"\n📊 Download Results:")
    print(f"✅ Successful: {len(results['successful'])}")
    print(f"❌ Failed: {len(results['failed'])}")
    
    if results['failed']:
        print("\nFailed URLs:")
        for url in results['failed']:
            print(f"  - {url}")
    
    if results['output_files']:
        print(f"\n📁 Downloaded {len(results['output_files'])} audio files to {args.output_dir}/")
    
    return 0 if results['successful'] else 1


if __name__ == "__main__":
    sys.exit(download_from_command_line())
