#!/usr/bin/env python3
"""Quick test of Qwen3-TTS Voice Design API"""

from gradio_client import Client
import os

space_id = "Qwen/Qwen3-TTS-Voice-Design"
token = os.getenv("HF_TOKEN", (__import__('os').environ['HF_TOKEN']))

print("=" * 70)
print(" Qwen3-TTS Voice Design - Quick Test")
print("=" * 70)

print(f"\n[1] Connecting to: {space_id}")
client = Client(space_id, hf_token=token)
print("  [OK] Connected!")

print("\n[2] Testing voice generation...")
text = "Hello! This is a test of the Qwen3-TTS voice design system."
instruct = "A clear and natural female voice, moderate speed, stable tone."

print(f"  Text: {text}")
print(f"  Instruction: {instruct}")
print("  (This may take 10-30 seconds...)")

try:
    # Use submit() with longer timeout for better reliability
    job = client.submit(
        text,
        instruct,
        api_name="/tts_interface"
    )
    
    print("  [OK] Request submitted, waiting for result...")
    result = job.result(timeout=120)  # 2 minute timeout
    
    print(f"\n  [SUCCESS] Generated!")
    print(f"  Audio file: {result}")
    
except Exception as e:
    print(f"\n  [ERROR] {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)

