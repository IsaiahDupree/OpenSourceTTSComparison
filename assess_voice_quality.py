#!/usr/bin/env python3
"""
Voice Quality Assessment Tool
==============================
Audits the quality of cloned voices using automated metrics.

Metrics:
1. Intelligibility (WER): Word Error Rate using OpenAI Whisper
2. Speaker Similarity: Cosine similarity of d-vector embeddings (requires resemblyzer or TTS)

Usage:
    python assess_voice_quality.py --ref reference.wav --gen generated.wav --text "Expected text"
"""

import sys
import os
import argparse
import numpy as np
import traceback
from pathlib import Path
from scipy.spatial.distance import cosine

# Suppress warnings
import warnings
warnings.filterwarnings("ignore")

def log(msg, level="INFO"):
    print(f"[{level}] {msg}")

def calculate_wer(reference_text, audio_path, model_name="base"):
    """
    Calculate Word Error Rate (WER) using OpenAI Whisper.
    """
    try:
        import whisper
        import jiwer
        
        log(f"Loading Whisper model '{model_name}'...", "INFO")
        model = whisper.load_model(model_name)
        
        log(f"Transcribing {audio_path}...", "INFO")
        # Transcribe
        result = model.transcribe(audio_path)
        transcribed_text = result["text"].strip()
        
        # Normalize
        ref_norm = jiwer.ToLowerCase()(reference_text)
        hyp_norm = jiwer.ToLowerCase()(transcribed_text)
        
        # Calculate WER
        wer = jiwer.wer(ref_norm, hyp_norm)
        
        return {
            "wer": wer,
            "transcription": transcribed_text,
            "reference": reference_text
        }
    except ImportError:
        log("Missing dependencies: pip install openai-whisper jiwer", "ERROR")
        return None
    except Exception as e:
        log(f"WER calculation failed: {e}", "ERROR")
        traceback.print_exc()
        return None

def calculate_similarity(ref_wav, gen_wav):
    """
    Calculate Cosine Similarity between two audio files using Resemblyzer.
    """
    try:
        from resemblyzer import VoiceEncoder, preprocess_wav
        
        log("Loading Resemblyzer VoiceEncoder...", "INFO")
        encoder = VoiceEncoder()
        
        # Process wavs
        wav1 = preprocess_wav(ref_wav)
        wav2 = preprocess_wav(gen_wav)
        
        # Get embeddings
        embed1 = encoder.embed_utterance(wav1)
        embed2 = encoder.embed_utterance(wav2)
        
        # Compute cosine similarity
        # 1 - cosine distance = cosine similarity
        similarity = 1 - cosine(embed1, embed2)
        
        return similarity
    except ImportError:
        log("Resemblyzer not installed. Skipping similarity check.", "WARN")
        return None
    except Exception as e:
        log(f"Similarity calculation failed: {e}", "ERROR")
        return None

def main():
    parser = argparse.ArgumentParser(description="Voice Cloning Quality Assessment")
    parser.add_argument("--ref", required=True, help="Reference/Target voice sample (WAV)")
    parser.add_argument("--gen", required=True, help="Generated/Cloned voice output (WAV)")
    parser.add_argument("--text", required=True, help="The text that was spoken in the generated audio")
    
    args = parser.parse_args()
    
    if not Path(args.ref).exists():
        log(f"Reference file not found: {args.ref}", "ERROR")
        sys.exit(1)
        
    if not Path(args.gen).exists():
        log(f"Generated file not found: {args.gen}", "ERROR")
        sys.exit(1)
        
    print("="*60)
    print(" VOICE QUALITY ASSESSMENT REPORT")
    print("="*60)
    print(f"Reference: {Path(args.ref).name}")
    print(f"Generated: {Path(args.gen).name}")
    print("-" * 60)
    
    # 1. Intelligibility (WER)
    log("Calculating Intelligibility (WER)...", "STEP")
    wer_result = calculate_wer(args.text, args.gen)
    
    wer_score = 0.0
    if wer_result:
        wer = wer_result["wer"]
        print(f"\n📝 Transcription: \"{wer_result['transcription']}\"")
        print(f"📖 Reference:     \"{wer_result['reference']}\"")
        print(f"📊 Word Error Rate (WER): {wer:.2%} (Lower is better)")
        
        # Simple quality checking
        if wer < 0.1:
            print("✅ Status: EXCELLENT Intelligibility")
        elif wer < 0.2:
            print("✅ Status: GOOD Intelligibility")
        else:
            print("⚠️ Status: POOR Intelligibility (Mumbling/Hallucination?)")
    else:
        print("❌ Failed to calculate WER")
        
    print("-" * 60)
    
    # 2. Speaker Similarity
    log("Calculating Speaker Similarity...", "STEP")
    similarity = calculate_similarity(args.ref, args.gen)
    
    if similarity is not None:
        print(f"\n👥 Speaker Similarity: {similarity:.3f} (Range: -1.0 to 1.0)")
        
        # Thresholds (empirical)
        if similarity > 0.75:
            print("✅ Status: EXCELLENT Match (High confidence same speaker)")
        elif similarity > 0.60:
            print("✅ Status: GOOD Match (Likely same speaker)")
        else:
            print("⚠️ Status: POOR Match (Sounds like different person)")
    else:
        print("⚠️ Similarity check skipped (install 'resemblyzer' for this metric)")
        
    print("="*60)

if __name__ == "__main__":
    main()
