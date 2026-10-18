#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete Workflow with Full Console Logging

Checks data → Analyzes channel → Downloads → Processes → Tests voice cloning
"""

import sys
import io
import json
import subprocess
from pathlib import Path
from datetime import datetime
import time

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def log(msg, level="INFO"):
    """Simple logging function."""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"{timestamp} [{level}] {msg}", flush=True)

def log_section(title):
    """Log section header."""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

def check_data():
    """Check current data."""
    log_section("CHECKING CURRENT DATA")
    
    # Audio samples
    audio_dir = Path("audio_samples")
    audio_count = 0
    if audio_dir.exists():
        audio_files = list(audio_dir.glob("*.m4a")) + list(audio_dir.glob("*.mp3"))
        audio_count = len(audio_files)
        log(f"✅ Audio samples: {audio_count}")
    else:
        log("⚠️  No audio_samples directory", "WARNING")
    
    # Processed segments
    segments_dir = Path("processed_segments")
    segment_count = 0
    best_segment = None
    if segments_dir.exists():
        segment_files = list(segments_dir.glob("*.wav"))
        segment_count = len(segment_files)
        log(f"✅ Processed segments: {segment_count}")
        
        # Check results
        results_file = segments_dir / "processing_results.json"
        if results_file.exists():
            with open(results_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
            best_segments = results.get('best_segments', [])
            if best_segments:
                best_segment = best_segments[0].get('output_file')
                quality = best_segments[0].get('quality_score', 0)
                log(f"✅ Best segment quality: {quality:.3f}")
    else:
        log("⚠️  No processed_segments directory", "WARNING")
    
    # Models
    has_chatterbox = False
    has_coqui = False
    try:
        import chatterbox
        has_chatterbox = True
        log("✅ Chatterbox available")
    except:
        log("⚠️  Chatterbox not available", "WARNING")
    
    try:
        from TTS.api import TTS
        has_coqui = True
        log("✅ Coqui TTS available")
    except:
        log("⚠️  Coqui TTS not available", "WARNING")
    
    return {
        "audio_count": audio_count,
        "segment_count": segment_count,
        "best_segment": best_segment,
        "has_chatterbox": has_chatterbox,
        "has_coqui": has_coqui
    }

def run_command(cmd, description):
    """Run command with real-time output."""
    log(f"Running: {description}")
    log(f"Command: {' '.join(cmd)}")
    print("")
    
    try:
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
                print(f"  {line}", flush=True)
        
        return_code = process.wait()
        print("")
        
        if return_code == 0:
            log(f"✅ {description} completed", "INFO")
            return True
        else:
            log(f"❌ {description} failed (code: {return_code})", "ERROR")
            return False
    except Exception as e:
        log(f"❌ Error: {e}", "ERROR")
        return False

def test_voice_cloning(best_segment, has_chatterbox, has_coqui):
    """Test voice cloning."""
    log_section("TESTING VOICE CLONING")
    
    if not best_segment or not Path(best_segment).exists():
        log("❌ No valid segment file found", "ERROR")
        return False
    
    log(f"Using segment: {Path(best_segment).name}")
    print("")
    
    # Try Chatterbox
    if has_chatterbox:
        log("Testing with Chatterbox...")
        try:
            import chatterbox
            import torch
            import soundfile as sf
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            log(f"Device: {device}")
            
            log("Loading model...")
            tts = chatterbox.ChatterboxTTS.from_pretrained(device)
            log("✅ Model loaded")
            
            test_text = "Hello, this is a test of voice cloning using my voice from YouTube videos."
            log(f"Generating: '{test_text}'")
            
            start = time.time()
            audio_tensor = tts.generate(test_text, audio_prompt_path=best_segment)
            elapsed = time.time() - start
            
            output_file = "voice_clone_test_chatterbox.wav"
            audio_np = audio_tensor.squeeze(0).detach().cpu().numpy()
            sr = int(getattr(tts, "sr", 24000))
            sf.write(output_file, audio_np, sr)
            
            log(f"✅ Voice cloning successful!", "INFO")
            log(f"   Output: {output_file}", "INFO")
            log(f"   Time: {elapsed:.2f}s", "INFO")
            return True
            
        except Exception as e:
            log(f"❌ Chatterbox failed: {e}", "ERROR")
            import traceback
            traceback.print_exc()
    
    # Try Coqui
    if has_coqui:
        log("Testing with Coqui TTS...")
        try:
            from TTS.api import TTS
            
            log("Loading XTTS-v2 model...")
            model = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
            log("✅ Model loaded")
            
            test_text = "Hello, this is a test of voice cloning."
            log(f"Generating: '{test_text}'")
            
            start = time.time()
            output_file = "voice_clone_test_coqui.wav"
            model.tts_to_file(text=test_text, speaker_wav=best_segment, file_path=output_file)
            elapsed = time.time() - start
            
            log(f"✅ Voice cloning successful!", "INFO")
            log(f"   Output: {output_file}", "INFO")
            log(f"   Time: {elapsed:.2f}s", "INFO")
            return True
            
        except Exception as e:
            log(f"❌ Coqui failed: {e}", "ERROR")
            import traceback
            traceback.print_exc()
    
    log("❌ No working voice cloning model", "ERROR")
    return False

def main():
    """Main workflow."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Complete workflow with logging")
    parser.add_argument("channel_url", help="YouTube channel URL")
    parser.add_argument("--max-videos", type=int, default=30, help="Max videos to analyze")
    parser.add_argument("--top-n", type=int, default=10, help="Top N to download")
    
    args = parser.parse_args()
    
    log_section("COMPLETE WORKFLOW STARTED")
    log(f"Channel: {args.channel_url}")
    log(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = time.time()
    
    # Check data
    data = check_data()
    print("")
    
    # Determine workflow
    needs_download = data["audio_count"] < 5
    needs_processing = data["segment_count"] < 10
    can_clone = data["segment_count"] >= 1 and (data["has_chatterbox"] or data["has_coqui"])
    
    log("Workflow plan:")
    log(f"  Analysis: Yes")
    download_msg = "Yes" if needs_download else f"Skip ({data['audio_count']} exist)"
    log(f"  Download: {download_msg}")
    process_msg = "Yes" if needs_processing else f"Skip ({data['segment_count']} exist)"
    log(f"  Processing: {process_msg}")
    log(f"  Voice Cloning: {'Yes' if can_clone else 'No'}")
    print("")
    
    # Step 1: Analysis
    log_section("STEP 1: ANALYZING CHANNEL")
    if run_command(
        [sys.executable, "agentic_video_analyzer.py", args.channel_url, 
         "--max-videos", str(args.max_videos), "--top-n", str(args.top_n)],
        "Channel Analysis"
    ):
        log("✅ Analysis step completed")
    else:
        log("❌ Analysis failed, continuing anyway...", "WARNING")
    
    # Step 2: Download
    if needs_download:
        log_section("STEP 2: DOWNLOADING VIDEOS")
        urls_file = "recommended_video_urls.txt"
        if Path(urls_file).exists():
            run_command(
                [sys.executable, "download_high_quality_voice_dataset.py", "--file", urls_file],
                "Video Download"
            )
        else:
            log(f"⚠️  {urls_file} not found, skipping download", "WARNING")
    
    # Step 3: Processing
    if needs_processing:
        log_section("STEP 3: PROCESSING AUDIO")
        run_command(
            [sys.executable, "improved_audio_processor.py", 
             "--input", "audio_samples", "--output", "processed_segments",
             "--min-duration", "5.0", "--min-snr", "15.0"],
            "Audio Processing"
        )
        # Re-check segments
        segments_dir = Path("processed_segments")
        if segments_dir.exists():
            data["segment_count"] = len(list(segments_dir.glob("*.wav")))
            results_file = segments_dir / "processing_results.json"
            if results_file.exists():
                with open(results_file, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                best_segments = results.get('best_segments', [])
                if best_segments:
                    data["best_segment"] = best_segments[0].get('output_file')
            can_clone = data["segment_count"] >= 1
    
    # Step 4: Voice Cloning
    if can_clone and data["best_segment"]:
        test_voice_cloning(data["best_segment"], data["has_chatterbox"], data["has_coqui"])
    else:
        log_section("VOICE CLONING SKIPPED")
        if data["segment_count"] < 1:
            log("❌ Need at least 1 processed segment", "WARNING")
        if not data["has_chatterbox"] and not data["has_coqui"]:
            log("❌ No voice cloning models available", "WARNING")
    
    # Summary
    elapsed = time.time() - start_time
    log_section("WORKFLOW COMPLETE")
    log(f"Total time: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
    log(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()

