#!/usr/bin/env python3
"""
Test Coqui TTS Installation and Basic Functionality
"""

import sys
import traceback
import os

def test_coqui_import():
    """Test if TTS can be imported."""
    try:
        from TTS.api import TTS
        print("✅ Coqui TTS imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import TTS: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error importing TTS: {e}")
        return False

def test_coqui_basic_usage():
    """Test basic Coqui TTS functionality."""
    try:
        from TTS.api import TTS
        
        # Initialize with a simple model
        print("Initializing Coqui TTS with basic model...")
        tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)
        print("✅ Coqui TTS initialized")
        
        # Test text synthesis
        test_text = "Hello, this is a test of Coqui TTS."
        print(f"Synthesizing: '{test_text}'")
        
        output_file = "coqui_test_output.wav"
        tts.tts_to_file(text=test_text, file_path=output_file)
        
        if os.path.exists(output_file):
            print(f"✅ Audio saved to: {output_file}")
            file_size = os.path.getsize(output_file)
            print(f"File size: {file_size} bytes")
            return True
        else:
            print("❌ Audio file was not created")
            return False
        
    except Exception as e:
        print(f"❌ Error testing Coqui TTS functionality: {e}")
        traceback.print_exc()
        return False

def test_coqui_voice_cloning():
    """Test Coqui TTS voice cloning capability."""
    try:
        from TTS.api import TTS
        
        print("Testing voice cloning with XTTS model...")
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False)
        print("✅ XTTS model loaded")
        
        # Use one of our synthetic audio samples as reference
        reference_audio = "audio_samples/clean_speech.wav"
        if not os.path.exists(reference_audio):
            print(f"❌ Reference audio not found: {reference_audio}")
            return False
        
        test_text = "This is a voice cloning test with Coqui TTS."
        output_file = "coqui_cloned_output.wav"
        
        tts.tts_to_file(
            text=test_text,
            speaker_wav=reference_audio,
            language="en",
            file_path=output_file
        )
        
        if os.path.exists(output_file):
            print(f"✅ Voice cloned audio saved to: {output_file}")
            return True
        else:
            print("❌ Voice cloned audio file was not created")
            return False
            
    except Exception as e:
        print(f"❌ Error testing voice cloning: {e}")
        traceback.print_exc()
        return False

def main():
    print("🎤 Testing Coqui TTS")
    print("=" * 40)
    
    # Test import
    if not test_coqui_import():
        print("\n❌ Coqui TTS not properly installed. Try:")
        print("pip install TTS")
        return False
    
    # Test basic usage
    print("\n🔧 Testing basic TTS functionality...")
    basic_success = test_coqui_basic_usage()
    
    # Test voice cloning
    print("\n🎭 Testing voice cloning functionality...")
    cloning_success = test_coqui_voice_cloning()
    
    if basic_success or cloning_success:
        print("\n🎉 Coqui TTS is working!")
        if basic_success:
            print("✅ Basic TTS: Working")
        if cloning_success:
            print("✅ Voice Cloning: Working")
        return True
    else:
        print("\n❌ All Coqui TTS tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
