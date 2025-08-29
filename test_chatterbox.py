#!/usr/bin/env python3
"""
Test Chatterbox TTS Installation and Basic Functionality
"""

import sys
import traceback

def test_chatterbox_import():
    """Test if chatterbox can be imported."""
    try:
        import chatterbox
        print("✅ Chatterbox imported successfully")
        print(f"Chatterbox version: {getattr(chatterbox, '__version__', 'Unknown')}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import chatterbox: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error importing chatterbox: {e}")
        return False

def test_chatterbox_basic_usage():
    """Test basic chatterbox functionality."""
    try:
        import chatterbox
        
        # Try to initialize TTS
        print("Initializing Chatterbox TTS...")
        tts = chatterbox.TTS()
        print("✅ Chatterbox TTS initialized")
        
        # Test text synthesis
        test_text = "Hello, this is a test of Chatterbox TTS."
        print(f"Synthesizing: '{test_text}'")
        
        audio = tts.synthesize(test_text)
        print(f"✅ Audio generated, length: {len(audio)} samples")
        
        # Save audio file
        import soundfile as sf
        output_file = "chatterbox_test_output.wav"
        sf.write(output_file, audio, 22050)
        print(f"✅ Audio saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing chatterbox functionality: {e}")
        traceback.print_exc()
        return False

def main():
    print("🎤 Testing Chatterbox TTS")
    print("=" * 40)
    
    # Test import
    if not test_chatterbox_import():
        print("\n❌ Chatterbox not properly installed. Try:")
        print("pip install chatterbox-tts")
        return False
    
    # Test basic usage
    print("\n🔧 Testing basic functionality...")
    if test_chatterbox_basic_usage():
        print("\n🎉 Chatterbox TTS is working correctly!")
        return True
    else:
        print("\n❌ Chatterbox TTS functionality test failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
