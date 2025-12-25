#!/usr/bin/env python3
"""
Easy YouTube Downloader

A simplified interface for the modular YouTube downloader.
This script can be used directly from any directory.
"""

import os
import sys
import argparse
from pathlib import Path
import logging

# Add the parent directory to the path so we can import the module
script_dir = Path(__file__).resolve().parent
sys.path.append(str(script_dir))

# Import the modular downloader
try:
    from scripts.modular_youtube_downloader import YouTubeDownloader
except ImportError:
    print("Error: Could not import modular_youtube_downloader module.")
    print(f"Make sure '{script_dir}/scripts/modular_youtube_downloader.py' exists.")
    sys.exit(1)

def setup_logging(verbose=False):
    """Set up logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(
        description='Download audio from YouTube videos from any directory'
    )
    
    parser.add_argument(
        'urls', 
        nargs='*', 
        help='YouTube URLs to download'
    )
    
    parser.add_argument(
        '-i', '--input-file', 
        help='File containing YouTube URLs (one per line)'
    )
    
    parser.add_argument(
        '-o', '--output-dir',
        default='./downloaded_audio',
        help='Output directory for downloaded audio (default: ./downloaded_audio)'
    )
    
    parser.add_argument(
        '-f', '--format',
        default='m4a',
        choices=['m4a', 'mp3', 'wav', 'ogg'],
        help='Audio format (default: m4a)'
    )
    
    parser.add_argument(
        '--include-title',
        action='store_true',
        help='Include video title in filename'
    )
    
    parser.add_argument(
        '--no-video-id',
        action='store_true',
        help="Don't include video ID in filename"
    )
    
    parser.add_argument(
        '--install-deps',
        action='store_true',
        help='Install required dependencies'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create downloader
    downloader = YouTubeDownloader(
        output_dir=str(output_dir),
        audio_format=args.format
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
    print(f"🎬 Downloading {len(urls)} videos to {output_dir}...")
    
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
        print(f"\n📁 Downloaded {len(results['output_files'])} audio files to {output_dir}")
        for file in results['output_files']:
            print(f"  - {Path(file).name}")
    
    return 0 if results['successful'] else 1

if __name__ == "__main__":
    sys.exit(main())
