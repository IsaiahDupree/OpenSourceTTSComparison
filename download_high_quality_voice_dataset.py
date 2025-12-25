#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Download High-Quality Voice Dataset from YouTube

This script downloads YouTube videos with focus on:
- High audio quality
- Long continuous speech segments
- Better voice cloning dataset
"""

import subprocess
import sys
import json
from pathlib import Path
from typing import List, Dict, Optional
import logging
from datetime import datetime

# Configure comprehensive console logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ],
    force=True
)
logger = logging.getLogger(__name__)

# Also log to file
file_handler = logging.FileHandler('download_voice_dataset.log', encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
logger.addHandler(file_handler)


class HighQualityVoiceDownloader:
    """Download high-quality voice data from YouTube."""
    
    def __init__(self, output_dir: str = "audio_samples"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.downloaded_videos = []
    
    def check_yt_dlp(self) -> bool:
        """Check if yt-dlp is installed."""
        try:
            result = subprocess.run(
                ["yt-dlp", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(f"✅ yt-dlp available: {result.stdout.strip()}")
                return True
        except FileNotFoundError:
            logger.error("❌ yt-dlp not found. Install with: pip install yt-dlp")
            return False
        except Exception as e:
            logger.error(f"❌ Error checking yt-dlp: {e}")
            return False
        return False
    
    def download_video(
        self,
        url: str,
        video_id: Optional[str] = None,
        quality: str = "best",
        format_preference: str = "m4a"
    ) -> Dict:
        """Download a single video with high quality settings."""
        
        if not video_id:
            # Extract video ID from URL
            if "watch?v=" in url:
                video_id = url.split("watch?v=")[1].split("&")[0]
            elif "youtu.be/" in url:
                video_id = url.split("youtu.be/")[1].split("?")[0]
            else:
                video_id = "unknown"
        
        logger.info(f"Downloading: {url}")
        logger.info(f"Video ID: {video_id}")
        
        # High quality download settings
        cmd = [
            "yt-dlp",
            "--extract-audio",
            "--audio-format", format_preference,
            "--audio-quality", "0",  # Best quality (0 = best)
            "--prefer-ffmpeg",
            "--no-playlist",
            "--write-info-json",  # Save metadata
            "--write-thumbnail",  # Save thumbnail
            "--output", str(self.output_dir / f"%(id)s_%(title)s.%(ext)s"),
            url
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode == 0:
                # Find downloaded file
                downloaded_files = list(self.output_dir.glob(f"{video_id}*"))
                audio_file = next((f for f in downloaded_files if f.suffix in ['.m4a', '.mp3', '.opus']), None)
                
                if audio_file:
                    logger.info(f"✅ Downloaded: {audio_file.name}")
                    
                    # Get file size
                    file_size = audio_file.stat().st_size / (1024 * 1024)  # MB
                    
                    return {
                        "success": True,
                        "video_id": video_id,
                        "url": url,
                        "file": str(audio_file),
                        "file_size_mb": round(file_size, 2),
                        "format": audio_file.suffix
                    }
                else:
                    logger.warning(f"⚠️  Downloaded but file not found")
                    return {"success": False, "error": "File not found after download"}
            else:
                error_msg = result.stderr or result.stdout
                logger.error(f"❌ Download failed: {error_msg[:200]}")
                return {"success": False, "error": error_msg[:200]}
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Download timeout")
            return {"success": False, "error": "Timeout"}
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return {"success": False, "error": str(e)}
    
    def download_multiple(
        self,
        urls: List[str],
        quality: str = "best",
        format_preference: str = "m4a"
    ) -> List[Dict]:
        """Download multiple videos."""
        logger.info(f"Downloading {len(urls)} videos...")
        
        results = []
        for i, url in enumerate(urls, 1):
            logger.info(f"\n[{i}/{len(urls)}] Processing video...")
            result = self.download_video(url, quality=quality, format_preference=format_preference)
            results.append(result)
            self.downloaded_videos.append(result)
        
        return results
    
    def analyze_video_for_speech(
        self,
        audio_file: str,
        min_duration: float = 5.0,
        min_snr: float = 15.0
    ) -> Dict:
        """Quick analysis to estimate speech quality."""
        try:
            import librosa
            import numpy as np
            
            # Load audio
            audio, sr = librosa.load(audio_file, sr=None, duration=60)  # Sample first 60 seconds
            
            # Basic metrics
            duration = len(audio) / sr
            
            # Estimate SNR (simple)
            energy = np.sum(audio ** 2)
            frame_energy = librosa.feature.rms(y=audio, frame_length=2048, hop_length=512)[0]
            noise_threshold = np.percentile(frame_energy, 20)
            noise_frames = frame_energy < noise_threshold
            
            if np.sum(noise_frames) > 0:
                noise_energy = np.mean(frame_energy[noise_frames]) ** 2
                signal_energy = np.mean(frame_energy[~noise_frames]) ** 2
                snr = 10 * np.log10(signal_energy / noise_energy) if noise_energy > 0 else 20
            else:
                snr = 20
            
            # Voice activity (simple energy-based)
            voice_activity = np.sum(frame_energy > np.percentile(frame_energy, 50)) / len(frame_energy)
            
            return {
                "duration": duration,
                "estimated_snr": snr,
                "voice_activity": voice_activity,
                "suitable": duration >= min_duration and snr >= min_snr
            }
        except Exception as e:
            logger.warning(f"⚠️  Could not analyze {audio_file}: {e}")
            return {"error": str(e)}
    
    def save_download_log(self, filename: str = "download_log.json"):
        """Save download log."""
        log_file = self.output_dir.parent / filename
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "downloaded_videos": self.downloaded_videos,
            "total": len(self.downloaded_videos),
            "successful": sum(1 for v in self.downloaded_videos if v.get("success"))
        }
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, default=str)
        
        logger.info(f"📊 Download log saved: {log_file}")


def interactive_download():
    """Interactive download session."""
    downloader = HighQualityVoiceDownloader()
    
    if not downloader.check_yt_dlp():
        print("\n❌ yt-dlp is required. Install with: pip install yt-dlp")
        return
    
    print("\n" + "=" * 70)
    print("HIGH-QUALITY VOICE DATASET DOWNLOADER")
    print("=" * 70)
    print("\nThis will download YouTube videos with:")
    print("  ✅ Best audio quality (format: m4a)")
    print("  ✅ Highest bitrate available")
    print("  ✅ Metadata and thumbnails")
    print("\nTips for better voice cloning:")
    print("  - Choose videos where you talk continuously")
    print("  - Avoid videos with background music")
    print("  - Prefer videos 5+ minutes long")
    print("  - Solo talking is better than interviews")
    
    urls = []
    print("\n" + "-" * 70)
    print("Enter YouTube URLs (one per line, empty line to finish):")
    print("-" * 70)
    
    while True:
        url = input("URL (or press Enter to finish): ").strip()
        if not url:
            break
        if "youtube.com" in url or "youtu.be" in url:
            urls.append(url)
            print(f"✅ Added: {url}")
        else:
            print("⚠️  Invalid YouTube URL, skipping...")
    
    if not urls:
        print("\n⚠️  No URLs provided. Exiting.")
        return
    
    print(f"\n📥 Downloading {len(urls)} video(s)...")
    results = downloader.download_multiple(urls)
    
    # Summary
    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]
    
    print("\n" + "=" * 70)
    print("DOWNLOAD SUMMARY")
    print("=" * 70)
    print(f"✅ Successful: {len(successful)}/{len(results)}")
    print(f"❌ Failed: {len(failed)}/{len(results)}")
    
    if successful:
        print("\n✅ Downloaded files:")
        for r in successful:
            print(f"   - {Path(r['file']).name} ({r.get('file_size_mb', 0)} MB)")
    
    if failed:
        print("\n❌ Failed downloads:")
        for r in failed:
            print(f"   - {r.get('video_id', 'unknown')}: {r.get('error', 'Unknown error')}")
    
    # Save log
    downloader.save_download_log()
    
    # Next steps
    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("1. Process audio segments:")
    print("   python tools/audio_processor.py --input audio_samples --output processed_segments")
    print("\n2. Check quality scores in:")
    print("   processed_segments/processing_results.json")
    print("\n3. Use best segments for voice cloning!")


def batch_download_from_file(url_file: str):
    """Download videos from a file containing URLs."""
    downloader = HighQualityVoiceDownloader()
    
    if not downloader.check_yt_dlp():
        return
    
    url_path = Path(url_file)
    if not url_path.exists():
        logger.error(f"❌ File not found: {url_file}")
        return
    
    # Read URLs
    urls = []
    with open(url_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if "youtube.com" in line or "youtu.be" in line:
                    urls.append(line)
    
    if not urls:
        logger.error("❌ No valid URLs found in file")
        return
    
    logger.info(f"Found {len(urls)} URLs in {url_file}")
    results = downloader.download_multiple(urls)
    downloader.save_download_log()


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Download high-quality voice dataset from YouTube"
    )
    parser.add_argument(
        "--urls",
        nargs="+",
        help="YouTube URLs to download"
    )
    parser.add_argument(
        "--file",
        help="File containing YouTube URLs (one per line)"
    )
    parser.add_argument(
        "--output",
        default="audio_samples",
        help="Output directory for downloaded files"
    )
    parser.add_argument(
        "--format",
        default="m4a",
        choices=["m4a", "mp3", "opus"],
        help="Audio format preference"
    )
    
    args = parser.parse_args()
    
    if args.file:
        batch_download_from_file(args.file)
    elif args.urls:
        downloader = HighQualityVoiceDownloader(args.output)
        if downloader.check_yt_dlp():
            downloader.download_multiple(args.urls, format_preference=args.format)
            downloader.save_download_log()
    else:
        interactive_download()


if __name__ == "__main__":
    main()

