#!/usr/bin/env python3
"""
Create sample audio files for TTS benchmarking using text-to-speech
This creates reference audio that we can use to test voice cloning quality
"""

import os
import sys
from pathlib import Path

def create_reference_audio():
    """Create reference audio samples using available TTS"""
    
    # Test phrases for different voice characteristics
    test_phrases = {
        "clean_speech": "Hello, this is a clear and professional voice sample for testing text-to-speech quality.",
        "emotional_speech": "I'm so excited about this amazing technology! It's absolutely incredible what we can achieve today.",
        "technical_speech": "The neural network architecture utilizes transformer-based attention mechanisms for improved synthesis quality.",
        "conversational": "Hey there! How's it going? I was just thinking about grabbing some coffee later.",
        "narrative": "Once upon a time, in a land far away, there lived a wise old wizard who possessed magical powers."
    }
    
    # Create output directory
    output_dir = Path("audio_samples")
    output_dir.mkdir(exist_ok=True)
    
    print("🎤 Creating reference audio samples...")
    
    try:
        # Try using Coqui TTS (which we know works)
        from TTS.api import TTS
        
        # Use a fast, simple model
        tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)
        
        for name, text in test_phrases.items():
            output_file = output_dir / f"{name}.wav"
            print(f"Generating: {name}")
            
            tts.tts_to_file(text=text, file_path=str(output_file))
            
            if output_file.exists():
                file_size = output_file.stat().st_size
                print(f"✅ Created {name}.wav ({file_size} bytes)")
            else:
                print(f"❌ Failed to create {name}.wav")
        
        return True
        
    except ImportError:
        print("❌ Coqui TTS not available")
        return False
    except Exception as e:
        print(f"❌ Error creating audio: {e}")
        return False

def main():
    """Main function"""
    print("🎵 Creating Sample Audio for TTS Benchmarking")
    print("=" * 50)
    
    if create_reference_audio():
        print("\n✅ Reference audio samples created successfully!")
        
        # List created files
        audio_dir = Path("audio_samples")
        files = list(audio_dir.glob("*.wav"))
        print(f"\n📁 Created {len(files)} audio files:")
        for file in files:
            print(f"  - {file.name}")
        
        print(f"\nNext step: Process audio segments")
        print(f"Run: python tools\\audio_processor.py --input audio_samples --output processed_segments")
        
    else:
        print("\n❌ Failed to create reference audio samples")
        return False

if __name__ == "__main__":
    main()
