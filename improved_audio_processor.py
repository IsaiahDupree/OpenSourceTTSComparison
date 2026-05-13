#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Improved Audio Processor for High-Quality Voice Dataset

Enhanced version that:
- Extracts longer speech segments (5-15 seconds)
- Better quality filtering
- Prioritizes continuous speech
- Creates better voice cloning dataset
"""

import sys
import io
import argparse
from pathlib import Path
import json
import numpy as np
import librosa
import soundfile as sf
from typing import List, Dict, Tuple
import logging
from tqdm import tqdm

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
file_handler = logging.FileHandler('audio_processor.log', encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
logger.addHandler(file_handler)


class ImprovedAudioProcessor:
    """Process audio to extract high-quality voice segments."""
    
    def __init__(
        self,
        min_segment_duration: float = 5.0,
        max_segment_duration: float = 15.0,
        min_snr: float = 15.0,
        min_voice_activity: float = 0.85,
        target_segments_per_file: int = 5
    ):
        self.min_segment_duration = min_segment_duration
        self.max_segment_duration = max_segment_duration
        self.min_snr = min_snr
        self.min_voice_activity = min_voice_activity
        self.target_segments_per_file = target_segments_per_file
    
    def find_long_speech_segments(
        self,
        audio: np.ndarray,
        sr: int,
        min_duration: float = 5.0
    ) -> List[Tuple[float, float]]:
        """Find long continuous speech segments."""
        # Use energy-based VAD
        frame_length = 2048
        hop_length = 512
        rms = librosa.feature.rms(y=audio, frame_length=frame_length, hop_length=hop_length)[0]
        
        # Normalize
        rms_norm = (rms - np.min(rms)) / (np.max(rms) - np.min(rms) + 1e-10)
        
        # Threshold for speech
        speech_threshold = np.percentile(rms_norm, 40)
        is_speech = rms_norm > speech_threshold
        
        # Find continuous speech segments
        segments = []
        in_speech = False
        start_frame = 0
        
        for i, speech in enumerate(is_speech):
            if speech and not in_speech:
                # Start of speech
                start_frame = i
                in_speech = True
            elif not speech and in_speech:
                # End of speech
                end_frame = i
                duration = (end_frame - start_frame) * hop_length / sr
                
                if duration >= min_duration:
                    start_time = start_frame * hop_length / sr
                    end_time = end_frame * hop_length / sr
                    segments.append((start_time, end_time))
                
                in_speech = False
        
        # Handle case where speech continues to end
        if in_speech:
            end_frame = len(is_speech)
            duration = (end_frame - start_frame) * hop_length / sr
            if duration >= min_duration:
                start_time = start_frame * hop_length / sr
                end_time = end_frame * hop_length / sr
                segments.append((start_time, end_time))
        
        return segments
    
    def calculate_quality_metrics(
        self,
        audio_segment: np.ndarray,
        sr: int
    ) -> Dict:
        """Calculate quality metrics for a segment."""
        # SNR estimation
        energy = np.sum(audio_segment ** 2)
        if energy == 0:
            snr = 0
        else:
            frame_energy = librosa.feature.rms(y=audio_segment, frame_length=2048, hop_length=512)[0]
            noise_threshold = np.percentile(frame_energy, 20)
            noise_frames = frame_energy < noise_threshold
            
            if np.sum(noise_frames) > 0:
                noise_energy = np.mean(frame_energy[noise_frames]) ** 2
                signal_energy = np.mean(frame_energy[~noise_frames]) ** 2
                snr = 10 * np.log10(signal_energy / noise_energy) if noise_energy > 0 else 20
            else:
                snr = 20
        
        # Voice activity
        rms = librosa.feature.rms(y=audio_segment, frame_length=2048, hop_length=512)[0]
        speech_threshold = np.percentile(rms, 40)
        voice_activity = np.sum(rms > speech_threshold) / len(rms)
        
        # Spectral quality
        spectral_centroids = librosa.feature.spectral_centroid(y=audio_segment, sr=sr)[0]
        centroid_stability = 1.0 / (1.0 + np.std(spectral_centroids))
        
        # Clarity (zero-crossing rate stability)
        zcr = librosa.feature.zero_crossing_rate(audio_segment)[0]
        clarity = 1.0 / (1.0 + np.std(zcr))
        
        # Combined quality score
        quality_score = (
            0.3 * min(snr / 30, 1.0) +  # SNR component (normalized)
            0.3 * voice_activity +  # Voice activity
            0.2 * centroid_stability +  # Spectral stability
            0.2 * clarity  # Clarity
        )
        
        return {
            "snr": snr,
            "voice_activity": voice_activity,
            "spectral_quality": centroid_stability,
            "clarity": clarity,
            "quality_score": quality_score
        }
    
    def process_audio_file(
        self,
        input_file: Path,
        output_dir: Path
    ) -> Dict:
        """Process a single audio file."""
        logger.info(f"Processing: {input_file.name}")
        
        try:
            # Load audio
            audio, sr = librosa.load(str(input_file), sr=22050)
            duration = len(audio) / sr
            
            logger.info(f"  Duration: {duration:.1f}s, Sample rate: {sr}Hz")
            
            # Find long speech segments
            segments = self.find_long_speech_segments(
                audio,
                sr,
                min_duration=self.min_segment_duration
            )
            
            logger.info(f"  Found {len(segments)} potential segments")
            
            # Process each segment
            processed_segments = []
            for i, (start_time, end_time) in enumerate(segments):
                # Extract segment
                start_sample = int(start_time * sr)
                end_sample = int(end_time * sr)
                segment_audio = audio[start_sample:end_sample]
                segment_duration = len(segment_audio) / sr
                
                # Filter by duration
                if segment_duration < self.min_segment_duration:
                    continue
                if segment_duration > self.max_segment_duration:
                    # Split long segments
                    num_splits = int(np.ceil(segment_duration / self.max_segment_duration))
                    split_duration = segment_duration / num_splits
                    for j in range(num_splits):
                        split_start = int(j * split_duration * sr)
                        split_end = int((j + 1) * split_duration * sr)
                        split_audio = segment_audio[split_start:split_end]
                        self._process_segment(
                            split_audio, sr, start_time + j * split_duration,
                            input_file, output_dir, len(processed_segments), processed_segments
                        )
                else:
                    self._process_segment(
                        segment_audio, sr, start_time,
                        input_file, output_dir, i, processed_segments
                    )
            
            # Sort by quality and keep best
            processed_segments.sort(key=lambda x: x["quality_score"], reverse=True)
            best_segments = processed_segments[:self.target_segments_per_file]
            
            logger.info(f"  [OK] Extracted {len(best_segments)} high-quality segments")
            
            return {
                "input_file": str(input_file),
                "total_segments_found": len(segments),
                "segments": best_segments,
                "total_segments": len(best_segments)
            }
            
        except Exception as e:
            logger.error(f"  ❌ Error processing {input_file.name}: {e}")
            return {
                "input_file": str(input_file),
                "error": str(e),
                "segments": []
            }
    
    def _process_segment(
        self,
        segment_audio: np.ndarray,
        sr: int,
        start_time: float,
        input_file: Path,
        output_dir: Path,
        segment_id: int,
        processed_segments: List
    ):
        """Process a single segment."""
        # Calculate metrics
        metrics = self.calculate_quality_metrics(segment_audio, sr)
        
        # Filter by quality
        if (metrics["snr"] < self.min_snr or
            metrics["voice_activity"] < self.min_voice_activity):
            return
        
        # Save segment
        output_filename = f"{input_file.stem}_segment_{segment_id}.wav"
        output_path = output_dir / output_filename
        
        sf.write(str(output_path), segment_audio, sr)
        
        # Add to processed segments
        processed_segments.append({
            "segment_id": segment_id,
            "start_time": start_time,
            "end_time": start_time + len(segment_audio) / sr,
            "duration": len(segment_audio) / sr,
            "output_file": str(output_path),
            **metrics
        })
    
    def process_directory(
        self,
        input_dir: Path,
        output_dir: Path
    ) -> Dict:
        """Process all audio files in a directory."""
        output_dir.mkdir(exist_ok=True, parents=True)
        
        # Find audio files
        audio_files = []
        for ext in ['.m4a', '.mp3', '.wav', '.opus', '.flac']:
            audio_files.extend(input_dir.glob(f"*{ext}"))
        
        if not audio_files:
            logger.warning(f"No audio files found in {input_dir}")
            return {}
        
        logger.info(f"Found {len(audio_files)} audio file(s)")
        
        # Process each file
        results = []
        for audio_file in tqdm(audio_files, desc="Processing audio"):
            result = self.process_audio_file(audio_file, output_dir)
            results.append(result)
        
        # Generate summary
        all_segments = []
        for result in results:
            all_segments.extend(result.get("segments", []))
        
        # Sort by quality
        all_segments.sort(key=lambda x: x["quality_score"], reverse=True)
        
        summary = {
            "processed_files": results,
            "best_segments": all_segments[:20],  # Top 20
            "statistics": {
                "total_files_processed": len(results),
                "total_segments_found": sum(r.get("total_segments", 0) for r in results),
                "average_quality_score": np.mean([s["quality_score"] for s in all_segments]) if all_segments else 0,
                "best_quality_score": all_segments[0]["quality_score"] if all_segments else 0,
                "average_snr": np.mean([s["snr"] for s in all_segments]) if all_segments else 0,
                "average_voice_activity": np.mean([s["voice_activity"] for s in all_segments]) if all_segments else 0,
                "average_duration": np.mean([s["duration"] for s in all_segments]) if all_segments else 0,
            }
        }
        
        # Save results
        results_file = output_dir / "processing_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, default=str)
        
        logger.info(f"\n[INFO] Results saved: {results_file}")
        logger.info(f"[OK] Total segments: {summary['statistics']['total_segments_found']}")
        logger.info(f"[INFO] Average quality: {summary['statistics']['average_quality_score']:.3f}")
        logger.info(f"[INFO] Best quality: {summary['statistics']['best_quality_score']:.3f}")
        logger.info(f"[INFO] Average duration: {summary['statistics']['average_duration']:.2f}s")
        
        return summary


def main():
    parser = argparse.ArgumentParser(
        description="Process audio files to extract high-quality voice segments"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Input directory with audio files"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output directory for processed segments"
    )
    parser.add_argument(
        "--min-duration",
        type=float,
        default=5.0,
        help="Minimum segment duration in seconds (default: 5.0)"
    )
    parser.add_argument(
        "--max-duration",
        type=float,
        default=15.0,
        help="Maximum segment duration in seconds (default: 15.0)"
    )
    parser.add_argument(
        "--min-snr",
        type=float,
        default=15.0,
        help="Minimum SNR in dB (default: 15.0)"
    )
    parser.add_argument(
        "--min-voice-activity",
        type=float,
        default=0.85,
        help="Minimum voice activity ratio (default: 0.85)"
    )
    parser.add_argument(
        "--segments-per-file",
        type=int,
        default=5,
        help="Target segments per file (default: 5)"
    )
    
    args = parser.parse_args()
    
    processor = ImprovedAudioProcessor(
        min_segment_duration=args.min_duration,
        max_segment_duration=args.max_duration,
        min_snr=args.min_snr,
        min_voice_activity=args.min_voice_activity,
        target_segments_per_file=args.segments_per_file
    )
    
    processor.process_directory(
        Path(args.input),
        Path(args.output)
    )


if __name__ == "__main__":
    main()

