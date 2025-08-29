#!/usr/bin/env python3
"""
Custom Audio Processing Tool for TTS Comparison Study

This tool analyzes audio files and extracts the best voice segments
based on multiple quality metrics including:
- Signal-to-noise ratio
- Voice activity detection
- Spectral quality
- Emotional neutrality
- Clear pronunciation
"""

import os
import argparse
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
import webrtcvad
import parselmouth
from scipy import signal
from typing import List, Tuple, Dict
import json
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns


class AudioQualityAnalyzer:
    """Analyzes audio quality using multiple metrics."""
    
    def __init__(self, sample_rate: int = 22050):
        self.sample_rate = sample_rate
        self.vad = webrtcvad.Vad(2)  # Aggressiveness level 2
        
    def calculate_snr(self, audio: np.ndarray) -> float:
        """Calculate Signal-to-Noise Ratio."""
        # Simple energy-based SNR estimation
        energy = np.sum(audio ** 2)
        if energy == 0:
            return -np.inf
        
        # Estimate noise from quiet segments
        frame_energy = librosa.feature.rms(y=audio, frame_length=2048, hop_length=512)[0]
        noise_threshold = np.percentile(frame_energy, 20)
        noise_frames = frame_energy < noise_threshold
        
        if np.sum(noise_frames) == 0:
            return 20.0  # Assume good SNR if no quiet segments
            
        noise_energy = np.mean(frame_energy[noise_frames]) ** 2
        signal_energy = np.mean(frame_energy[~noise_frames]) ** 2
        
        if noise_energy == 0:
            return 40.0  # Very good SNR
            
        snr_db = 10 * np.log10(signal_energy / noise_energy)
        return snr_db
    
    def detect_voice_activity(self, audio: np.ndarray) -> float:
        """Calculate percentage of frames with voice activity."""
        # Convert to 16kHz for WebRTC VAD
        audio_16k = librosa.resample(audio, orig_sr=self.sample_rate, target_sr=16000)
        audio_16k = (audio_16k * 32767).astype(np.int16)
        
        frame_duration = 30  # ms
        frame_length = int(16000 * frame_duration / 1000)
        
        voice_frames = 0
        total_frames = 0
        
        for i in range(0, len(audio_16k) - frame_length, frame_length):
            frame = audio_16k[i:i + frame_length].tobytes()
            if self.vad.is_speech(frame, 16000):
                voice_frames += 1
            total_frames += 1
            
        return voice_frames / total_frames if total_frames > 0 else 0.0
    
    def calculate_spectral_quality(self, audio: np.ndarray) -> float:
        """Calculate spectral quality metrics."""
        # Spectral centroid stability
        spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=self.sample_rate)[0]
        centroid_stability = 1.0 / (1.0 + np.std(spectral_centroids))
        
        # Spectral rolloff
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=self.sample_rate)[0]
        rolloff_mean = np.mean(spectral_rolloff)
        
        # Combine metrics (normalized to 0-1)
        quality_score = centroid_stability * min(rolloff_mean / 4000, 1.0)
        return quality_score
    
    def analyze_pronunciation_clarity(self, audio: np.ndarray) -> float:
        """Analyze pronunciation clarity using Praat."""
        try:
            # Create Praat Sound object
            sound = parselmouth.Sound(audio, sampling_frequency=self.sample_rate)
            
            # Calculate harmonicity (measure of voice quality)
            harmonicity = sound.to_harmonicity()
            mean_harmonicity = harmonicity.values[harmonicity.values > -200].mean()
            
            # Normalize to 0-1 scale
            clarity_score = min(max((mean_harmonicity + 10) / 20, 0), 1)
            return clarity_score
            
        except Exception:
            # Fallback to spectral analysis
            return self.calculate_spectral_quality(audio)


class VoiceSegmentExtractor:
    """Extracts the best voice segments from audio files."""
    
    def __init__(self, target_duration: float = 10.0, min_segment: float = 3.0):
        self.target_duration = target_duration
        self.min_segment = min_segment
        self.analyzer = AudioQualityAnalyzer()
        
    def extract_segments(self, audio_path: str) -> List[Dict]:
        """Extract and rank voice segments from audio file."""
        # Load audio
        audio, sr = librosa.load(audio_path, sr=22050)
        
        # Split into segments based on silence
        segments = self._split_by_silence(audio, sr)
        
        # Analyze each segment
        segment_scores = []
        for i, (start, end) in enumerate(segments):
            segment_audio = audio[start:end]
            
            if len(segment_audio) / sr < self.min_segment:
                continue
                
            # Calculate quality metrics
            snr = self.analyzer.calculate_snr(segment_audio)
            voice_activity = self.analyzer.detect_voice_activity(segment_audio)
            spectral_quality = self.analyzer.calculate_spectral_quality(segment_audio)
            clarity = self.analyzer.analyze_pronunciation_clarity(segment_audio)
            
            # Combined quality score
            quality_score = (
                0.3 * min(max(snr, 0) / 30, 1) +  # SNR component
                0.3 * voice_activity +              # Voice activity component
                0.2 * spectral_quality +            # Spectral quality component
                0.2 * clarity                       # Pronunciation clarity
            )
            
            segment_scores.append({
                'segment_id': i,
                'start_time': start / sr,
                'end_time': end / sr,
                'duration': (end - start) / sr,
                'snr': snr,
                'voice_activity': voice_activity,
                'spectral_quality': spectral_quality,
                'clarity': clarity,
                'quality_score': quality_score,
                'audio_data': segment_audio
            })
        
        # Sort by quality score
        segment_scores.sort(key=lambda x: x['quality_score'], reverse=True)
        
        return segment_scores
    
    def _split_by_silence(self, audio: np.ndarray, sr: int) -> List[Tuple[int, int]]:
        """Split audio by silence detection."""
        # Calculate RMS energy
        frame_length = 2048
        hop_length = 512
        rms = librosa.feature.rms(y=audio, frame_length=frame_length, hop_length=hop_length)[0]
        
        # Determine silence threshold
        silence_threshold = np.percentile(rms, 30)
        
        # Find silence/speech boundaries
        is_speech = rms > silence_threshold
        
        # Convert frame indices to sample indices
        frame_to_sample = lambda f: f * hop_length
        
        segments = []
        start = None
        
        for i, speech in enumerate(is_speech):
            if speech and start is None:
                start = frame_to_sample(i)
            elif not speech and start is not None:
                end = frame_to_sample(i)
                if end - start > sr * self.min_segment:  # Minimum segment length
                    segments.append((start, end))
                start = None
        
        # Handle case where audio ends with speech
        if start is not None:
            segments.append((start, len(audio)))
        
        return segments


class AudioProcessor:
    """Main audio processing pipeline."""
    
    def __init__(self, output_dir: str = "processed"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.extractor = VoiceSegmentExtractor()
        
    def process_directory(self, input_dir: str, max_files: int = None) -> Dict:
        """Process all audio files in directory."""
        input_path = Path(input_dir)
        audio_extensions = {'.wav', '.mp3', '.flac', '.m4a', '.ogg', '.webm', '.mp4'}
        
        audio_files = [
            f for f in input_path.rglob('*') 
            if f.suffix.lower() in audio_extensions
        ]
        
        if max_files:
            audio_files = audio_files[:max_files]
        
        results = {
            'processed_files': [],
            'best_segments': [],
            'statistics': {}
        }
        
        print(f"Processing {len(audio_files)} audio files...")
        
        for audio_file in tqdm(audio_files, desc="Processing audio files"):
            try:
                file_results = self.process_file(str(audio_file))
                results['processed_files'].append(file_results)
                
                # Keep track of best segments overall
                if file_results['segments']:
                    best_segment = file_results['segments'][0]
                    best_segment['source_file'] = str(audio_file)
                    results['best_segments'].append(best_segment)
                    
            except Exception as e:
                print(f"Error processing {audio_file}: {e}")
                continue
        
        # Sort best segments globally
        results['best_segments'].sort(key=lambda x: x['quality_score'], reverse=True)
        
        # Generate statistics
        results['statistics'] = self._generate_statistics(results)
        
        # Save results
        self._save_results(results)
        
        return results
    
    def process_file(self, audio_path: str) -> Dict:
        """Process single audio file."""
        segments = self.extractor.extract_segments(audio_path)
        
        # Save best segments
        output_segments = []
        for i, segment in enumerate(segments[:3]):  # Keep top 3 segments
            output_filename = f"{Path(audio_path).stem}_segment_{i}.wav"
            output_path = self.output_dir / output_filename
            
            sf.write(str(output_path), segment['audio_data'], 22050)
            
            segment_info = segment.copy()
            del segment_info['audio_data']  # Remove audio data for JSON serialization
            segment_info['output_file'] = str(output_path)
            output_segments.append(segment_info)
        
        return {
            'input_file': audio_path,
            'segments': output_segments,
            'total_segments': len(segments)
        }
    
    def _generate_statistics(self, results: Dict) -> Dict:
        """Generate processing statistics."""
        if not results['best_segments']:
            return {}
        
        quality_scores = [s['quality_score'] for s in results['best_segments']]
        snr_values = [s['snr'] for s in results['best_segments']]
        voice_activities = [s['voice_activity'] for s in results['best_segments']]
        
        return {
            'total_files_processed': len(results['processed_files']),
            'total_segments_found': len(results['best_segments']),
            'average_quality_score': np.mean(quality_scores),
            'best_quality_score': max(quality_scores),
            'average_snr': np.mean(snr_values),
            'average_voice_activity': np.mean(voice_activities),
            'quality_score_std': np.std(quality_scores)
        }
    
    def _save_results(self, results: Dict) -> None:
        """Save processing results to JSON."""
        output_file = self.output_dir / "processing_results.json"
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"Results saved to {output_file}")
        
        # Create visualization
        self._create_visualization(results)
    
    def _create_visualization(self, results: Dict) -> None:
        """Create visualization of processing results."""
        if not results['best_segments']:
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        
        # Quality score distribution
        quality_scores = [s['quality_score'] for s in results['best_segments']]
        axes[0, 0].hist(quality_scores, bins=20, alpha=0.7)
        axes[0, 0].set_title('Quality Score Distribution')
        axes[0, 0].set_xlabel('Quality Score')
        axes[0, 0].set_ylabel('Frequency')
        
        # SNR vs Quality Score
        snr_values = [s['snr'] for s in results['best_segments']]
        axes[0, 1].scatter(snr_values, quality_scores, alpha=0.6)
        axes[0, 1].set_title('SNR vs Quality Score')
        axes[0, 1].set_xlabel('SNR (dB)')
        axes[0, 1].set_ylabel('Quality Score')
        
        # Voice Activity Distribution
        voice_activities = [s['voice_activity'] for s in results['best_segments']]
        axes[1, 0].hist(voice_activities, bins=20, alpha=0.7)
        axes[1, 0].set_title('Voice Activity Distribution')
        axes[1, 0].set_xlabel('Voice Activity Ratio')
        axes[1, 0].set_ylabel('Frequency')
        
        # Duration Distribution
        durations = [s['duration'] for s in results['best_segments']]
        axes[1, 1].hist(durations, bins=20, alpha=0.7)
        axes[1, 1].set_title('Segment Duration Distribution')
        axes[1, 1].set_xlabel('Duration (seconds)')
        axes[1, 1].set_ylabel('Frequency')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'processing_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()


def main():
    parser = argparse.ArgumentParser(description='Extract best voice segments from audio files')
    parser.add_argument('--input', '-i', required=True, help='Input directory with audio files')
    parser.add_argument('--output', '-o', default='processed', help='Output directory')
    parser.add_argument('--max-files', type=int, help='Maximum number of files to process')
    parser.add_argument('--target-duration', type=float, default=10.0, help='Target segment duration')
    
    args = parser.parse_args()
    
    processor = AudioProcessor(args.output)
    results = processor.process_directory(args.input, args.max_files)
    
    print(f"\nProcessing complete!")
    print(f"Processed {results['statistics'].get('total_files_processed', 0)} files")
    print(f"Found {results['statistics'].get('total_segments_found', 0)} segments")
    print(f"Average quality score: {results['statistics'].get('average_quality_score', 0):.3f}")
    print(f"Best segments saved to: {args.output}/")


if __name__ == "__main__":
    main()
