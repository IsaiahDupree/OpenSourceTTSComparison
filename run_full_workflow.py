#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Full Workflow: Agentic Analysis → Download → Process

Complete automated workflow with comprehensive console logging.
"""

import sys
import io
from pathlib import Path
from datetime import datetime
import subprocess
import json

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Import logging config
try:
    from logging_config import setup_logging, log_section, log_progress, log_success, log_error, log_warning
except ImportError:
    # Fallback if logging_config not available
    import logging
    def setup_logging(name, **kwargs):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
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

logger = setup_logging(__name__, "full_workflow.log")


class FullWorkflow:
    """Complete workflow orchestrator."""
    
    def __init__(self, channel_url: str):
        self.channel_url = channel_url
        self.workflow_start = datetime.now()
        self.results = {
            "analysis": None,
            "download": None,
            "processing": None
        }
    
    def step_1_analyze_channel(self, max_videos: int = 50, top_n: int = 15):
        """Step 1: Analyze channel for best videos."""
        log_section(logger, "STEP 1: ANALYZING CHANNEL FOR BEST VIDEOS")
        
        logger.info(f"Channel URL: {self.channel_url}")
        logger.info(f"Max videos to analyze: {max_videos}")
        logger.info(f"Top N to recommend: {top_n}")
        logger.info("")
        
        try:
            cmd = [
                sys.executable,
                "agentic_video_analyzer.py",
                self.channel_url,
                "--max-videos", str(max_videos),
                "--top-n", str(top_n)
            ]
            
            logger.info(f"Running: {' '.join(cmd)}")
            logger.info("")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Stream output in real-time
            for line in process.stdout:
                line = line.strip()
                if line:
                    logger.info(f"  {line}")
            
            return_code = process.wait()
            
            if return_code == 0:
                log_success(logger, "Channel analysis completed")
                
                # Check if report was generated
                if Path("video_analysis_report.json").exists():
                    with open("video_analysis_report.json", 'r', encoding='utf-8') as f:
                        report = json.load(f)
                    self.results["analysis"] = report
                    log_success(logger, f"Found {report.get('total_videos_analyzed', 0)} videos")
                    log_success(logger, f"Recommended: {report.get('recommended_videos', 0)} videos")
                    return True
                else:
                    log_warning(logger, "Analysis report not found")
                    return False
            else:
                log_error(logger, f"Analysis failed with code {return_code}")
                return False
                
        except Exception as e:
            log_error(logger, f"Analysis error: {e}")
            return False
    
    def step_2_download_videos(self, urls_file: str = "recommended_video_urls.txt"):
        """Step 2: Download recommended videos."""
        log_section(logger, "STEP 2: DOWNLOADING RECOMMENDED VIDEOS")
        
        if not Path(urls_file).exists():
            log_error(logger, f"URLs file not found: {urls_file}")
            log_warning(logger, "Skipping download step")
            return False
        
        # Count URLs
        with open(urls_file, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
        
        logger.info(f"Found {len(urls)} video URLs to download")
        logger.info("")
        
        try:
            cmd = [
                sys.executable,
                "download_high_quality_voice_dataset.py",
                "--file", urls_file
            ]
            
            logger.info(f"Running: {' '.join(cmd)}")
            logger.info("")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Stream output in real-time
            for line in process.stdout:
                line = line.strip()
                if line:
                    logger.info(f"  {line}")
            
            return_code = process.wait()
            
            if return_code == 0:
                log_success(logger, "Video downloads completed")
                return True
            else:
                log_error(logger, f"Download failed with code {return_code}")
                return False
                
        except Exception as e:
            log_error(logger, f"Download error: {e}")
            return False
    
    def step_3_process_audio(
        self,
        input_dir: str = "audio_samples",
        output_dir: str = "processed_segments",
        min_duration: float = 5.0,
        min_snr: float = 15.0
    ):
        """Step 3: Process audio to extract high-quality segments."""
        log_section(logger, "STEP 3: PROCESSING AUDIO SEGMENTS")
        
        logger.info(f"Input directory: {input_dir}")
        logger.info(f"Output directory: {output_dir}")
        logger.info(f"Min duration: {min_duration}s")
        logger.info(f"Min SNR: {min_snr}dB")
        logger.info("")
        
        try:
            cmd = [
                sys.executable,
                "improved_audio_processor.py",
                "--input", input_dir,
                "--output", output_dir,
                "--min-duration", str(min_duration),
                "--min-snr", str(min_snr)
            ]
            
            logger.info(f"Running: {' '.join(cmd)}")
            logger.info("")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Stream output in real-time
            for line in process.stdout:
                line = line.strip()
                if line:
                    logger.info(f"  {line}")
            
            return_code = process.wait()
            
            if return_code == 0:
                log_success(logger, "Audio processing completed")
                
                # Check results
                results_file = Path(output_dir) / "processing_results.json"
                if results_file.exists():
                    with open(results_file, 'r', encoding='utf-8') as f:
                        results = json.load(f)
                    stats = results.get('statistics', {})
                    log_success(logger, f"Total segments: {stats.get('total_segments_found', 0)}")
                    log_success(logger, f"Average quality: {stats.get('average_quality_score', 0):.3f}")
                    log_success(logger, f"Best quality: {stats.get('best_quality_score', 0):.3f}")
                    self.results["processing"] = results
                    return True
                else:
                    log_warning(logger, "Processing results not found")
                    return False
            else:
                log_error(logger, f"Processing failed with code {return_code}")
                return False
                
        except Exception as e:
            log_error(logger, f"Processing error: {e}")
            return False
    
    def run_full_workflow(
        self,
        max_videos: int = 50,
        top_n: int = 15,
        download: bool = True,
        process: bool = True
    ):
        """Run the complete workflow."""
        log_section(logger, "FULL WORKFLOW: VOICE CLONING DATASET CREATION")
        logger.info(f"Started: {self.workflow_start.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("")
        
        workflow_steps = []
        
        # Step 1: Analyze
        logger.info("")
        if self.step_1_analyze_channel(max_videos, top_n):
            workflow_steps.append("✅ Analysis")
        else:
            workflow_steps.append("❌ Analysis")
            log_error(logger, "Workflow stopped: Analysis failed")
            return False
        
        # Step 2: Download
        if download:
            logger.info("")
            if self.step_2_download_videos():
                workflow_steps.append("✅ Download")
            else:
                workflow_steps.append("⚠️  Download (skipped/failed)")
        else:
            log_warning(logger, "Skipping download step (--no-download)")
            workflow_steps.append("⏭️  Download (skipped)")
        
        # Step 3: Process
        if process:
            logger.info("")
            if self.step_3_process_audio():
                workflow_steps.append("✅ Processing")
            else:
                workflow_steps.append("❌ Processing")
        else:
            log_warning(logger, "Skipping processing step (--no-process)")
            workflow_steps.append("⏭️  Processing (skipped)")
        
        # Summary
        workflow_end = datetime.now()
        duration = (workflow_end - self.workflow_start).total_seconds()
        
        log_section(logger, "WORKFLOW SUMMARY")
        logger.info("Steps completed:")
        for step in workflow_steps:
            logger.info(f"  {step}")
        logger.info("")
        logger.info(f"Total time: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        logger.info(f"Completed: {workflow_end.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Save workflow results
        workflow_report = {
            "timestamp": workflow_end.isoformat(),
            "duration_seconds": duration,
            "steps": workflow_steps,
            "results": self.results
        }
        
        with open("workflow_report.json", 'w', encoding='utf-8') as f:
            json.dump(workflow_report, f, indent=2, default=str)
        
        log_success(logger, "Workflow report saved: workflow_report.json")
        
        return True


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Full workflow: Analyze channel → Download → Process audio"
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
    parser.add_argument(
        "--no-download",
        action="store_true",
        help="Skip download step (analysis only)"
    )
    parser.add_argument(
        "--no-process",
        action="store_true",
        help="Skip processing step"
    )
    
    args = parser.parse_args()
    
    workflow = FullWorkflow(args.channel_url)
    workflow.run_full_workflow(
        max_videos=args.max_videos,
        top_n=args.top_n,
        download=not args.no_download,
        process=not args.no_process
    )


if __name__ == "__main__":
    main()

