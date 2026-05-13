#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agentic YouTube Channel Video Analyzer

Automatically analyzes your YouTube channel to find:
- Videos with highest quality audio
- Long continuous talking segments
- Best videos for voice cloning dataset
"""

import subprocess
import sys
import json
import re
import io
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime
import time

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

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
file_handler = logging.FileHandler('agentic_analyzer.log', encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
logger.addHandler(file_handler)


class AgenticVideoAnalyzer:
    """Agentic system to analyze YouTube channel videos."""
    
    def __init__(self, channel_url: str, output_dir: str = "audio_samples"):
        self.channel_url = channel_url
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.video_analysis = []
        self.channel_id = None
    
    def _get_video_duration(self, video_id: str) -> int:
        """Get video duration by fetching full info."""
        try:
            cmd = [
                "yt-dlp",
                "--print", "%(duration)s",
                f"https://www.youtube.com/watch?v={video_id}",
                "--no-warnings",
                "--quiet"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout.strip().isdigit():
                return int(result.stdout.strip())
        except:
            pass
        return 0
    
    def check_yt_dlp(self) -> bool:
        """Check if yt-dlp is available."""
        try:
            result = subprocess.run(
                ["yt-dlp", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def extract_channel_id(self) -> Optional[str]:
        """Extract channel ID from URL."""
        try:
            # Try to get channel info
            cmd = [
                "yt-dlp",
                "--flat-playlist",
                "--print", "%(channel_id)s",
                self.channel_url,
                "--playlist-end", "1"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and result.stdout.strip():
                self.channel_id = result.stdout.strip()
                return self.channel_id
        except Exception as e:
            logger.warning(f"Could not extract channel ID: {e}")
        return None
    
    def get_channel_videos(self, max_videos: int = 50) -> List[Dict]:
        """Get list of videos from channel."""
        logger.info(f"Fetching videos from channel: {self.channel_url}")
        logger.info(f"Max videos to analyze: {max_videos}")
        
        try:
            # Get video list with metadata (need to extract info, not flat playlist)
            cmd = [
                "yt-dlp",
                "--flat-playlist",
                "--print", "%(id)s|||%(title)s|||%(duration)s|||%(view_count)s|||%(upload_date)s",
                self.channel_url,
                "--playlist-end", str(max_videos),
                "--no-warnings"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                logger.error(f"Failed to fetch videos: {result.stderr}")
                return []
            
            videos = []
            for line in result.stdout.strip().split('\n'):
                if '|||' in line:
                    parts = line.split('|||')
                    if len(parts) >= 3:
                        video_id = parts[0]
                        title = parts[1] if len(parts) > 1 else "Unknown"
                        duration = parts[2] if len(parts) > 2 else "0"
                        view_count = parts[3] if len(parts) > 3 else "0"
                        upload_date = parts[4] if len(parts) > 4 else ""
                        
                        # Parse duration (handle "NA" or empty)
                        try:
                            if duration and duration != "NA" and duration.isdigit():
                                duration_sec = int(duration)
                            else:
                                # Try to get duration from full video info
                                duration_sec = self._get_video_duration(video_id)
                        except:
                            duration_sec = self._get_video_duration(video_id)
                        
                        videos.append({
                            "video_id": video_id,
                            "title": title,
                            "duration_seconds": duration_sec,
                            "duration_minutes": duration_sec / 60,
                            "view_count": view_count,
                            "upload_date": upload_date,
                            "url": f"https://www.youtube.com/watch?v={video_id}"
                        })
            
            logger.info(f"✅ Found {len(videos)} videos")
            return videos
            
        except Exception as e:
            logger.error(f"Error fetching videos: {e}")
            return []
    
    def analyze_video_title(self, title: str) -> Dict:
        """Analyze video title for indicators of good voice content."""
        title_lower = title.lower()
        
        # Keywords that suggest good voice content
        good_keywords = [
            "tutorial", "explain", "guide", "how to", "review", "analysis",
            "discussion", "talk", "speech", "presentation", "lecture",
            "podcast", "interview", "monologue", "solo", "alone"
        ]
        
        # Keywords that suggest poor voice content
        bad_keywords = [
            "music", "song", "remix", "beat", "instrumental", "karaoke",
            "compilation", "highlights", "short", "clip", "teaser"
        ]
        
        good_score = sum(1 for kw in good_keywords if kw in title_lower)
        bad_score = sum(1 for kw in bad_keywords if kw in title_lower)
        
        # Duration indicators
        has_duration = any(word in title_lower for word in ["hour", "minute", "long", "full"])
        
        return {
            "title_score": good_score - bad_score,
            "has_good_keywords": good_score > 0,
            "has_bad_keywords": bad_score > 0,
            "suggests_long_content": has_duration
        }
    
    def sample_audio_quality(
        self,
        video_url: str,
        sample_duration: int = 60
    ) -> Dict:
        """Download a sample of audio and analyze quality."""
        logger.info(f"  Sampling audio quality (first {sample_duration}s)...")
        
        try:
            # Download first 60 seconds as sample
            temp_file = self.output_dir / f"temp_sample_{int(time.time())}.m4a"
            
            cmd = [
                "yt-dlp",
                "--extract-audio",
                "--audio-format", "m4a",
                "--audio-quality", "0",
                "--postprocessor-args", f"ffmpeg:-t {sample_duration}",
                "--output", str(temp_file),
                video_url
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0 or not temp_file.exists():
                return {"error": "Failed to download sample"}
            
            # Analyze audio quality
            quality_metrics = self.analyze_audio_file(temp_file)
            
            # Cleanup
            temp_file.unlink(missing_ok=True)
            
            return quality_metrics
            
        except Exception as e:
            logger.warning(f"  ⚠️  Could not sample audio: {e}")
            return {"error": str(e)}
    
    def analyze_audio_file(self, audio_file: Path) -> Dict:
        """Analyze audio file quality."""
        try:
            import librosa
            import numpy as np
            
            # Load audio
            audio, sr = librosa.load(str(audio_file), sr=22050, duration=60)
            
            # Calculate metrics
            duration = len(audio) / sr
            
            # SNR estimation
            frame_energy = librosa.feature.rms(y=audio, frame_length=2048, hop_length=512)[0]
            noise_threshold = np.percentile(frame_energy, 20)
            noise_frames = frame_energy < noise_threshold
            
            if np.sum(noise_frames) > 0:
                noise_energy = np.mean(frame_energy[noise_frames]) ** 2
                signal_energy = np.mean(frame_energy[~noise_frames]) ** 2
                snr = 10 * np.log10(signal_energy / noise_energy) if noise_energy > 0 else 20
            else:
                snr = 20
            
            # Voice activity
            speech_threshold = np.percentile(frame_energy, 40)
            voice_activity = np.sum(frame_energy > speech_threshold) / len(frame_energy)
            
            # Spectral quality
            spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
            spectral_stability = 1.0 / (1.0 + np.std(spectral_centroids))
            
            # Detect if likely has music (higher spectral spread)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)[0]
            has_music_indicator = np.mean(spectral_rolloff) > 4000  # Higher = more likely music
            
            # Quality score
            quality_score = (
                0.3 * min(snr / 30, 1.0) +
                0.3 * voice_activity +
                0.2 * spectral_stability +
                0.2 * (1.0 if not has_music_indicator else 0.5)  # Penalize music
            )
            
            return {
                "snr": round(snr, 2),
                "voice_activity": round(voice_activity, 3),
                "spectral_quality": round(spectral_stability, 3),
                "has_music_likely": has_music_indicator,
                "quality_score": round(quality_score, 3),
                "duration_analyzed": round(duration, 2)
            }
            
        except ImportError:
            return {"error": "librosa not available"}
        except Exception as e:
            return {"error": str(e)}
    
    def score_video(self, video: Dict, audio_quality: Optional[Dict] = None) -> Dict:
        """Score video based on multiple criteria."""
        score = 0.0
        factors = {}
        
        # Duration score (longer is better, but not too long)
        duration_min = video.get("duration_minutes", 0)
        if 5 <= duration_min <= 30:
            duration_score = 1.0  # Ideal range
        elif 3 <= duration_min < 5:
            duration_score = 0.7
        elif 30 < duration_min <= 60:
            duration_score = 0.8
        elif duration_min > 60:
            duration_score = 0.6  # Very long might have filler
        else:
            duration_score = 0.3  # Too short
        
        score += duration_score * 0.25
        factors["duration_score"] = round(duration_score, 2)
        
        # Title analysis
        title_analysis = self.analyze_video_title(video.get("title", ""))
        title_score = max(0, min(1, (title_analysis["title_score"] + 2) / 4))  # Normalize to 0-1
        score += title_score * 0.15
        factors["title_score"] = round(title_score, 2)
        
        # Audio quality (if analyzed)
        if audio_quality and "quality_score" in audio_quality:
            quality_score = audio_quality["quality_score"]
            score += quality_score * 0.35
            factors["audio_quality_score"] = round(quality_score, 3)
            factors["snr"] = audio_quality.get("snr", 0)
            factors["voice_activity"] = audio_quality.get("voice_activity", 0)
            factors["has_music"] = audio_quality.get("has_music_likely", False)
        else:
            # Estimate based on duration (longer videos often better quality)
            estimated_quality = min(1.0, duration_min / 20)
            score += estimated_quality * 0.20
            factors["estimated_quality"] = round(estimated_quality, 2)
        
        # View count (popular videos might be better content)
        try:
            view_count = int(video.get("view_count", 0))
            if view_count > 1000:
                popularity_score = min(1.0, np.log10(view_count) / 6)  # Log scale
            else:
                popularity_score = 0.3
        except:
            popularity_score = 0.5
        
        score += popularity_score * 0.10
        factors["popularity_score"] = round(popularity_score, 2)
        
        # Recency (newer might be better quality)
        upload_date = video.get("upload_date", "")
        if upload_date:
            try:
                from datetime import datetime
                upload_dt = datetime.strptime(upload_date[:8], "%Y%m%d")
                days_old = (datetime.now() - upload_dt).days
                recency_score = max(0.5, 1.0 - (days_old / 365) * 0.5)  # Decay over year
            except:
                recency_score = 0.7
        else:
            recency_score = 0.7
        
        score += recency_score * 0.15
        factors["recency_score"] = round(recency_score, 2)
        
        return {
            "total_score": round(score, 3),
            "factors": factors,
            "recommended": score >= 0.65  # Threshold for recommendation
        }
    
    def analyze_channel(self, max_videos: int = 50, sample_audio: bool = True) -> List[Dict]:
        """Analyze entire channel and rank videos."""
        logger.info("=" * 70)
        logger.info("AGENTIC YOUTUBE CHANNEL ANALYZER")
        logger.info("=" * 70)
        
        if not self.check_yt_dlp():
            logger.error("❌ yt-dlp not found. Install with: pip install yt-dlp")
            return []
        
        # Get channel videos
        videos = self.get_channel_videos(max_videos)
        
        if not videos:
            logger.error("❌ No videos found")
            return []
        
        logger.info(f"\nAnalyzing {len(videos)} videos...")
        logger.info("This may take a while (sampling audio quality)...")
        
        analyzed_videos = []
        
        for i, video in enumerate(videos, 1):
            logger.info(f"\n[{i}/{len(videos)}] {video['title'][:60]}...")
            logger.info(f"  Duration: {video['duration_minutes']:.1f} minutes")
            
            # Sample audio if requested
            audio_quality = None
            if sample_audio and video['duration_seconds'] > 30:
                audio_quality = self.sample_audio_quality(video['url'])
                if "error" not in audio_quality:
                    logger.info(f"  ✅ Quality: {audio_quality.get('quality_score', 0):.3f}, "
                              f"SNR: {audio_quality.get('snr', 0):.1f}dB, "
                              f"Voice: {audio_quality.get('voice_activity', 0):.1%}")
                else:
                    logger.warning(f"  ⚠️  Could not analyze audio")
            
            # Score video
            scoring = self.score_video(video, audio_quality)
            
            # Combine all info
            analyzed_video = {
                **video,
                "audio_quality": audio_quality,
                "scoring": scoring,
                "rank": 0  # Will be set after sorting
            }
            
            analyzed_videos.append(analyzed_video)
            
            logger.info(f"  📊 Total Score: {scoring['total_score']:.3f} "
                      f"{'✅ RECOMMENDED' if scoring['recommended'] else ''}")
        
        # Rank videos by score
        analyzed_videos.sort(key=lambda x: x['scoring']['total_score'], reverse=True)
        
        for i, video in enumerate(analyzed_videos, 1):
            video['rank'] = i
        
        self.video_analysis = analyzed_videos
        
        return analyzed_videos
    
    def generate_recommendations(self, top_n: int = 10) -> Dict:
        """Generate recommendations report."""
        if not self.video_analysis:
            return {}
        
        recommended = [v for v in self.video_analysis if v['scoring']['recommended']]
        top_videos = self.video_analysis[:top_n]
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "channel_url": self.channel_url,
            "total_videos_analyzed": len(self.video_analysis),
            "recommended_videos": len(recommended),
            "top_videos": [
                {
                    "rank": v['rank'],
                    "video_id": v['video_id'],
                    "title": v['title'],
                    "url": v['url'],
                    "duration_minutes": v['duration_minutes'],
                    "total_score": v['scoring']['total_score'],
                    "factors": v['scoring']['factors'],
                    "audio_quality": v.get('audio_quality', {})
                }
                for v in top_videos
            ],
            "recommendations": [
                {
                    "rank": v['rank'],
                    "video_id": v['video_id'],
                    "title": v['title'],
                    "url": v['url'],
                    "duration_minutes": v['duration_minutes'],
                    "total_score": v['scoring']['total_score'],
                    "why_recommended": self._explain_recommendation(v)
                }
                for v in recommended[:top_n]
            ]
        }
        
        return report
    
    def _explain_recommendation(self, video: Dict) -> str:
        """Explain why a video is recommended."""
        reasons = []
        factors = video['scoring']['factors']
        
        if factors.get('duration_score', 0) >= 0.8:
            reasons.append("Ideal duration (5-30 minutes)")
        
        if factors.get('audio_quality_score', 0) >= 0.7:
            reasons.append("High audio quality")
        
        if factors.get('snr', 0) >= 15:
            reasons.append("Good signal-to-noise ratio")
        
        if factors.get('voice_activity', 0) >= 0.85:
            reasons.append("High voice activity (lots of talking)")
        
        if not factors.get('has_music', True):
            reasons.append("No background music detected")
        
        if factors.get('title_score', 0) >= 0.7:
            reasons.append("Title suggests good voice content")
        
        return "; ".join(reasons) if reasons else "Good overall score"
    
    def save_report(self, report: Dict, filename: str = "video_analysis_report.json"):
        """Save analysis report."""
        report_file = Path(filename)
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"\n📊 Report saved: {report_file}")
        return report_file
    
    def print_recommendations(self, report: Dict):
        """Print recommendations in readable format."""
        print("\n" + "=" * 70)
        print("TOP RECOMMENDED VIDEOS FOR VOICE CLONING")
        print("=" * 70)
        
        if not report.get('recommendations'):
            print("\nNote: No videos met the recommendation threshold (score >= 0.65)")
            print("Showing top videos by score:")
            for video in report.get('top_videos', [])[:5]:
                print(f"\n  {video['rank']}. {video['title'][:60]}")
                print(f"     Score: {video['total_score']:.3f}")
                print(f"     Duration: {video['duration_minutes']:.1f} min")
                print(f"     URL: {video['url']}")
        else:
            for video in report['recommendations']:
                print(f"\n  {video['rank']}. {video['title'][:60]}")
                print(f"     Score: {video['total_score']:.3f}")
                print(f"     Duration: {video['duration_minutes']:.1f} min")
                print(f"     Why: {video['why_recommended']}")
                print(f"     URL: {video['url']}")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Agentically analyze YouTube channel for best voice cloning videos"
    )
    parser.add_argument(
        "channel_url",
        help="YouTube channel URL (e.g., https://www.youtube.com/@channelname)"
    )
    parser.add_argument(
        "--max-videos",
        type=int,
        default=50,
        help="Maximum videos to analyze (default: 50)"
    )
    parser.add_argument(
        "--no-audio-sample",
        action="store_true",
        help="Skip audio quality sampling (faster but less accurate)"
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=10,
        help="Number of top videos to recommend (default: 10)"
    )
    
    args = parser.parse_args()
    
    analyzer = AgenticVideoAnalyzer(args.channel_url)
    
    # Analyze channel
    analyzed_videos = analyzer.analyze_channel(
        max_videos=args.max_videos,
        sample_audio=not args.no_audio_sample
    )
    
    if not analyzed_videos:
        print("\n❌ Analysis failed")
        return
    
    # Generate recommendations
    report = analyzer.generate_recommendations(top_n=args.top_n)
    
    # Save report
    analyzer.save_report(report)
    
    # Print recommendations
    analyzer.print_recommendations(report)
    
    # Save URLs for easy download
    if report.get('recommendations'):
        urls_file = Path("recommended_video_urls.txt")
        with open(urls_file, 'w', encoding='utf-8') as f:
            f.write("# Recommended videos for voice cloning dataset\n")
            f.write("# Generated by agentic_video_analyzer.py\n\n")
            for video in report['recommendations']:
                f.write(f"{video['url']}\n")
        
        print(f"\n📝 URLs saved to: {urls_file}")
        print(f"\n💡 Next step: Download recommended videos:")
        print(f"   python download_high_quality_voice_dataset.py --file {urls_file}")


if __name__ == "__main__":
    import numpy as np  # For scoring calculations
    main()

