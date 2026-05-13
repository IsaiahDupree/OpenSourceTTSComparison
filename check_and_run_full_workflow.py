#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check Current Data → Run Full Workflow → Test Voice Cloning

Complete workflow with comprehensive console logging at every step.
"""

import sys
import io
from pathlib import Path
from datetime import datetime
import subprocess
import json
import time

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Import logging config
try:
    from logging_config import setup_logging, log_section, log_progress, log_success, log_error, log_warning, log_info
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
    def setup_logging(name, **kwargs):
        return logging.getLogger(name)
    def log_section(logger, title, char="="):
        logger.info(f"\n{char * 70}\n{title}\n{char * 70}")
    def log_progress(logger, current, total, item=""):
        logger.info(f"[{current}/{total}] ({current/total*100:.1f}%) {item}")
    def log_success(logger, msg):
        logger.info(f"✅ {msg}")
    def log_error(logger, msg):
        logger.error(f"❌ {msg}")
    def log_warning(logger, msg):
        logger.warning(f"⚠️  {msg}")
    def log_info(logger, msg):
        logger.info(f"ℹ️  {msg}")

logger = setup_logging(__name__, "full_workflow_with_cloning.log")


class CompleteWorkflow:
    """Complete workflow with voice cloning test."""
    
    def __init__(self, channel_url: str):
        self.channel_url = channel_url
        self.start_time = time.time()
        self.results = {}
    
    def check_current_data(self):
        """Check what data we currently have."""
        log_section(logger, "CHECKING CURRENT DATA")
        
        data_status = {
            "audio_samples": 0,
            "processed_segments": 0,
            "best_segment": None,
            "has_chatterbox": False,
            "has_coqui": False
        }
        
        # Check audio samples
        audio_dir = Path("audio_samples")
        if audio_dir.exists():
            audio_files = list(audio_dir.glob("*.m4a")) + list(audio_dir.glob("*.mp3")) + list(audio_dir.glob("*.wav"))
            data_status["audio_samples"] = len(audio_files)
            log_info(logger, f"Audio samples found: {len(audio_files)}")
            for f in audio_files[:5]:
                size_mb = f.stat().st_size / (1024 * 1024)
                log_info(logger, f"  - {f.name} ({size_mb:.1f} MB)")
        else:
            log_warning(logger, "audio_samples/ directory not found")
        
        # Check processed segments
        segments_dir = Path("processed_segments")
        if segments_dir.exists():
            segment_files = list(segments_dir.glob("*.wav"))
            data_status["processed_segments"] = len(segment_files)
            log_info(logger, f"Processed segments found: {len(segment_files)}")
            
            # Check for results file
            results_file = segments_dir / "processing_results.json"
            if results_file.exists():
                with open(results_file, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                stats = results.get('statistics', {})
                best_segments = results.get('best_segments', [])
                
                if best_segments:
                    best = best_segments[0]
                    data_status["best_segment"] = best.get('output_file')
                    log_success(logger, f"Best segment quality: {best.get('quality_score', 0):.3f}")
                    log_info(logger, f"  File: {Path(best.get('output_file', '')).name}")
                    log_info(logger, f"  Duration: {best.get('duration', 0):.2f}s")
                    log_info(logger, f"  SNR: {best.get('snr', 0):.1f}dB")
                
                log_info(logger, f"Average quality: {stats.get('average_quality_score', 0):.3f}")
                log_info(logger, f"Total segments: {stats.get('total_segments_found', 0)}")
        else:
            log_warning(logger, "processed_segments/ directory not found")
        
        # Check for voice cloning models
        try:
            import chatterbox
            data_status["has_chatterbox"] = True
            log_success(logger, "Chatterbox available")
        except:
            log_warning(logger, "Chatterbox not available")
        
        try:
            from TTS.api import TTS
            data_status["has_coqui"] = True
            log_success(logger, "Coqui TTS available")
        except:
            log_warning(logger, "Coqui TTS not available")
        
        self.results["current_data"] = data_status
        return data_status
    
    def run_analysis(self, max_videos: int = 50, top_n: int = 15):
        """Run channel analysis."""
        log_section(logger, "STEP 1: ANALYZING CHANNEL")
        
        logger.info(f"Channel: {self.channel_url}")
        logger.info(f"Max videos: {max_videos}, Top N: {top_n}")
        logger.info("")
        
        try:
            cmd = [
                sys.executable, "agentic_video_analyzer.py",
                self.channel_url,
                "--max-videos", str(max_videos),
                "--top-n", str(top_n)
            ]
            
            logger.info(f"Command: {' '.join(cmd)}")
            logger.info("")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            for line in process.stdout:
                line = line.strip()
                if line:
                    logger.info(f"  {line}")
            
            return_code = process.wait()
            
            if return_code == 0 and Path("video_analysis_report.json").exists():
                log_success(logger, "Analysis completed")
                with open("video_analysis_report.json", 'r', encoding='utf-8') as f:
                    report = json.load(f)
                self.results["analysis"] = report
                return True
            else:
                log_error(logger, "Analysis failed")
                return False
        except Exception as e:
            log_error(logger, f"Analysis error: {e}")
            return False
    
    def download_videos(self, urls_file: str = "recommended_video_urls.txt"):
        """Download recommended videos."""
        log_section(logger, "STEP 2: DOWNLOADING VIDEOS")
        
        if not Path(urls_file).exists():
            log_warning(logger, f"{urls_file} not found, skipping download")
            return False
        
        with open(urls_file, 'r', encoding='utf-8') as f:
            urls = [l.strip() for l in f if l.strip() and not l.strip().startswith('#')]
        
        logger.info(f"Found {len(urls)} URLs to download")
        logger.info("")
        
        try:
            cmd = [sys.executable, "download_high_quality_voice_dataset.py", "--file", urls_file]
            logger.info(f"Command: {' '.join(cmd)}")
            logger.info("")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            for line in process.stdout:
                line = line.strip()
                if line:
                    logger.info(f"  {line}")
            
            return_code = process.wait()
            
            if return_code == 0:
                log_success(logger, "Downloads completed")
                return True
            else:
                log_error(logger, "Downloads failed")
                return False
        except Exception as e:
            log_error(logger, f"Download error: {e}")
            return False
    
    def process_audio(self, min_duration: float = 5.0, min_snr: float = 15.0):
        """Process audio segments."""
        log_section(logger, "STEP 3: PROCESSING AUDIO")
        
        logger.info(f"Min duration: {min_duration}s, Min SNR: {min_snr}dB")
        logger.info("")
        
        try:
            cmd = [
                sys.executable, "improved_audio_processor.py",
                "--input", "audio_samples",
                "--output", "processed_segments",
                "--min-duration", str(min_duration),
                "--min-snr", str(min_snr)
            ]
            
            logger.info(f"Command: {' '.join(cmd)}")
            logger.info("")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            for line in process.stdout:
                line = line.strip()
                if line:
                    logger.info(f"  {line}")
            
            return_code = process.wait()
            
            if return_code == 0:
                log_success(logger, "Processing completed")
                return True
            else:
                log_error(logger, "Processing failed")
                return False
        except Exception as e:
            log_error(logger, f"Processing error: {e}")
            return False
    
    def test_voice_cloning(self):
        """Test voice cloning with best segment."""
        log_section(logger, "STEP 4: TESTING VOICE CLONING")
        
        # Find best segment
        results_file = Path("processed_segments/processing_results.json")
        if not results_file.exists():
            log_error(logger, "Processing results not found")
            return False
        
        with open(results_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        best_segments = results.get('best_segments', [])
        if not best_segments:
            log_error(logger, "No segments found")
            return False
        
        best_segment = best_segments[0]
        segment_file = Path(best_segment['output_file'])
        
        if not segment_file.exists():
            log_error(logger, f"Segment file not found: {segment_file}")
            return False
        
        log_info(logger, f"Using best segment: {segment_file.name}")
        log_info(logger, f"  Quality: {best_segment.get('quality_score', 0):.3f}")
        log_info(logger, f"  Duration: {best_segment.get('duration', 0):.2f}s")
        log_info(logger, f"  SNR: {best_segment.get('snr', 0):.1f}dB")
        logger.info("")
        
        # Try Chatterbox first
        if self.results["current_data"].get("has_chatterbox"):
            log_info(logger, "Testing with Chatterbox...")
            try:
                import chatterbox
                import torch
                import soundfile as sf
                
                device = "cuda" if torch.cuda.is_available() else "cpu"
                logger.info(f"Device: {device}")
                
                logger.info("Loading Chatterbox model...")
                tts = chatterbox.ChatterboxTTS.from_pretrained(device)
                log_success(logger, "Model loaded")
                
                test_text = "Hello, this is a test of voice cloning using my voice from YouTube videos. Does it sound natural?"
                logger.info(f"Generating speech: '{test_text[:50]}...'")
                
                start_time = time.time()
                audio_tensor = tts.generate(
                    test_text,
                    audio_prompt_path=str(segment_file)
                )
                generation_time = time.time() - start_time
                
                output_file = "voice_clone_test_chatterbox.wav"
                audio_np = audio_tensor.squeeze(0).detach().cpu().numpy()
                sr = int(getattr(tts, "sr", 24000))
                sf.write(output_file, audio_np, sr)
                
                log_success(logger, f"Voice cloning successful!")
                log_info(logger, f"  Output: {output_file}")
                log_info(logger, f"  Generation time: {generation_time:.2f}s")
                log_info(logger, f"  Audio length: {len(audio_np)/sr:.2f}s")
                
                self.results["voice_cloning"] = {
                    "model": "Chatterbox",
                    "success": True,
                    "output_file": output_file,
                    "generation_time": generation_time
                }
                return True
                
            except Exception as e:
                log_error(logger, f"Chatterbox cloning failed: {e}")
                import traceback
                logger.error(traceback.format_exc())
        
        # Try Coqui TTS
        if self.results["current_data"].get("has_coqui"):
            log_info(logger, "Testing with Coqui TTS...")
            try:
                from TTS.api import TTS
                import soundfile as sf
                
                logger.info("Loading XTTS-v2 model...")
                model = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
                log_success(logger, "Model loaded")
                
                test_text = "Hello, this is a test of voice cloning using my voice from YouTube videos."
                logger.info(f"Generating speech: '{test_text}'")
                
                start_time = time.time()
                output_file = "voice_clone_test_coqui.wav"
                model.tts_to_file(
                    text=test_text,
                    speaker_wav=str(segment_file),
                    file_path=output_file
                )
                generation_time = time.time() - start_time
                
                log_success(logger, f"Voice cloning successful!")
                log_info(logger, f"  Output: {output_file}")
                log_info(logger, f"  Generation time: {generation_time:.2f}s")
                
                self.results["voice_cloning"] = {
                    "model": "Coqui TTS",
                    "success": True,
                    "output_file": output_file,
                    "generation_time": generation_time
                }
                return True
                
            except Exception as e:
                log_error(logger, f"Coqui TTS cloning failed: {e}")
                import traceback
                logger.error(traceback.format_exc())
        
        log_error(logger, "No voice cloning models available")
        return False
    
    def run_complete_workflow(self, max_videos: int = 50, top_n: int = 15):
        """Run complete workflow."""
        log_section(logger, "COMPLETE WORKFLOW: ANALYSIS → DOWNLOAD → PROCESS → CLONE")
        logger.info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("")
        
        # Check current data
        data_status = self.check_current_data()
        logger.info("")
        
        # Determine what to do
        needs_analysis = True
        needs_download = data_status["audio_samples"] < 5
        needs_processing = data_status["processed_segments"] < 10
        can_clone = data_status["processed_segments"] >= 1 and (
            data_status["has_chatterbox"] or data_status["has_coqui"]
        )
        
        logger.info("Workflow plan:")
        logger.info(f"  Analysis: {'Yes' if needs_analysis else 'Skip (already done)'}")
        download_msg = f"Skip ({data_status['audio_samples']} samples exist)" if not needs_download else "Yes"
        logger.info(f"  Download: {download_msg}")
        process_msg = f"Skip ({data_status['processed_segments']} segments exist)" if not needs_processing else "Yes"
        logger.info(f"  Processing: {process_msg}")
        logger.info(f"  Voice Cloning: {'Yes' if can_clone else 'No (need segments + model)'}")
        logger.info("")
        
        # Run steps
        steps_completed = []
        
        if needs_analysis:
            if self.run_analysis(max_videos, top_n):
                steps_completed.append("✅ Analysis")
            else:
                steps_completed.append("❌ Analysis")
                log_error(logger, "Stopping: Analysis failed")
                return False
        else:
            steps_completed.append("⏭️  Analysis (skipped)")
        
        if needs_download:
            logger.info("")
            if self.download_videos():
                steps_completed.append("✅ Download")
            else:
                steps_completed.append("⚠️  Download (failed)")
        else:
            steps_completed.append("⏭️  Download (skipped)")
        
        if needs_processing:
            logger.info("")
            if self.process_audio():
                steps_completed.append("✅ Processing")
                # Re-check segments
                segments_dir = Path("processed_segments")
                if segments_dir.exists():
                    segments = list(segments_dir.glob("*.wav"))
                    can_clone = len(segments) >= 1
            else:
                steps_completed.append("❌ Processing")
        else:
            steps_completed.append("⏭️  Processing (skipped)")
        
        if can_clone:
            logger.info("")
            if self.test_voice_cloning():
                steps_completed.append("✅ Voice Cloning")
            else:
                steps_completed.append("❌ Voice Cloning")
        else:
            log_warning(logger, "Cannot test voice cloning:")
            if not data_status["processed_segments"]:
                log_warning(logger, "  - No processed segments")
            if not data_status["has_chatterbox"] and not data_status["has_coqui"]:
                log_warning(logger, "  - No voice cloning models available")
            steps_completed.append("⏭️  Voice Cloning (skipped)")
        
        # Summary
        total_time = time.time() - self.start_time
        log_section(logger, "WORKFLOW SUMMARY")
        logger.info("Steps completed:")
        for step in steps_completed:
            logger.info(f"  {step}")
        logger.info("")
        logger.info(f"Total time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
        logger.info(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Save report
        self.results["workflow_summary"] = {
            "steps": steps_completed,
            "total_time": total_time,
            "timestamp": datetime.now().isoformat()
        }
        
        with open("complete_workflow_report.json", 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        log_success(logger, "Workflow report saved: complete_workflow_report.json")
        
        return True


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Complete workflow: Check → Analyze → Download → Process → Clone"
    )
    parser.add_argument(
        "channel_url",
        help="YouTube channel URL"
    )
    parser.add_argument(
        "--max-videos",
        type=int,
        default=50,
        help="Max videos to analyze (default: 50)"
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=15,
        help="Top N videos to download (default: 15)"
    )
    
    args = parser.parse_args()
    
    workflow = CompleteWorkflow(args.channel_url)
    workflow.run_complete_workflow(
        max_videos=args.max_videos,
        top_n=args.top_n
    )


if __name__ == "__main__":
    main()

