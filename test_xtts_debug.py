#!/usr/bin/env python3
"""
Debug XTTS-v2 initialization issue
"""

import os
import sys

# MeCab workaround
class DummyMeCab:
    class Tagger:
        def __init__(self, *args, **kwargs):
            pass
sys.modules['MeCab'] = DummyMeCab()

from TTS.api import TTS
import torch

print("=" * 70)
print(" XTTS-v2 Debug")
print("=" * 70)

print("\n[1] Creating TTS object...")
gpu = torch.cuda.is_available()
tts = TTS("xtts_v2", gpu=gpu)

print(f"Model name: {tts.model_name}")
print(f"Has synthesizer attr: {hasattr(tts, 'synthesizer')}")
print(f"Synthesizer value: {tts.synthesizer}")

# Try to access synthesizer property - might trigger lazy loading
print("\n[2] Accessing synthesizer property...")
try:
    synth = tts.synthesizer
    print(f"Synthesizer: {synth}")
    print(f"Type: {type(synth)}")
except Exception as e:
    print(f"Error accessing synthesizer: {e}")

# Check if there's a method to load/initialize
print("\n[3] Checking TTS methods...")
methods = [m for m in dir(tts) if not m.startswith('_')]
print(f"Available methods: {methods[:10]}...")

# Try calling load_tts_model_by_name
print("\n[4] Trying to manually load model...")
try:
    tts.load_tts_model_by_name("xtts_v2", gpu=gpu)
    print("✅ Manual load successful")
    print(f"Synthesizer after manual load: {tts.synthesizer}")
except Exception as e:
    print(f"❌ Manual load failed: {e}")

# Check manager
print("\n[5] Checking model manager...")
try:
    print(f"Manager: {tts.manager}")
    print(f"Manager type: {type(tts.manager)}")
    if hasattr(tts.manager, 'models_dict'):
        print("Has models_dict")
        # Check if xtts_v2 is in there
        # This might be complex, so let's just see what we can access
except Exception as e:
    print(f"Error: {e}")

# Final check - try to use it anyway
print("\n[6] Attempting to use TTS object...")
ref_audio = "openvoice_deploy/resources/demo_speaker2.mp3"
if os.path.exists(ref_audio):
    try:
        print("Calling tts.tts()...")
        wav = tts.tts(
            text="Test",
            speaker_wav=ref_audio,
            language="en"
        )
        print(f"✅ tts() worked! Output shape: {wav.shape if hasattr(wav, 'shape') else type(wav)}")
    except Exception as e:
        print(f"❌ tts() failed: {e}")
        import traceback
        traceback.print_exc()
else:
    print("Reference audio not found, skipping test")

print("\n" + "=" * 70)

