#!/usr/bin/env python3
"""
Test Chatterbox TTS Installation and Basic Functionality
"""

import sys
import traceback
from typing import Any, Tuple
import torch
import soundfile as sf

def test_chatterbox_import():
    """Test if chatterbox can be imported."""
    try:
        import chatterbox
        print("Chatterbox import successful")
        print(f"Chatterbox version: {getattr(chatterbox, '__version__', 'Unknown')}")
        return True
    except ImportError as e:
        print(f"Failed to import chatterbox: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error importing chatterbox: {e}")
        return False

def _unused() -> None:
    """Placeholder to keep file structure while removing dynamic helpers."""
    return None

def test_chatterbox_basic_usage():
    """Test basic chatterbox functionality."""
    try:
        import chatterbox
        
        # Select device
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Initializing Chatterbox TTS (device={device})...")

        # Use official factory
        tts = chatterbox.ChatterboxTTS.from_pretrained(device)
        print("Chatterbox TTS initialized")

        # Test text synthesis via generate()
        test_text = "Hello, this is a test of Chatterbox TTS."
        print(f"Synthesizing: '{test_text}'")
        audio_tensor = tts.generate(test_text)
        sr = int(getattr(tts, "sr", 44100))

        # Convert to numpy for saving
        audio_np = audio_tensor.squeeze(0).detach().cpu().numpy()
        n_samples = audio_np.shape[-1]
        print(f"Audio generated, length: {len(audio_np)} samples @ {tts.sr} Hz")

        # Save audio file
        output_file = "chatterbox_test_output.wav"
        sf.write(output_file, audio_np, sr)
        print(f"Audio saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"Error testing chatterbox functionality: {e}")
        traceback.print_exc()
        return False

def main():
    print("Testing Chatterbox TTS")
    print("=" * 40)
    
    # Test import
    if not test_chatterbox_import():
        print("\nChatterbox not properly installed. Try:")
        print("pip install chatterbox-tts")
        return False
    
    # Test basic usage
    print("\nTesting basic functionality...")
    if test_chatterbox_basic_usage():
        print("\nChatterbox TTS is working correctly!")
        return True
    else:
        print("\nChatterbox TTS functionality test failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
