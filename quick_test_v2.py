#!/usr/bin/env python3
"""Quick test of OpenVoice V2 official API"""

from gradio_client import Client
import os

endpoint = "https://myshell-ai-openvoicev2.hf.space/--replicas/c2rsh/"
token = os.getenv("HF_TOKEN", (__import__('os').environ['HF_TOKEN']))

print("Connecting to OpenVoice V2...")
client = Client(endpoint, hf_token=token)

print("Testing with: 'Howdy! This is a test.'")
result = client.predict(
    "Howdy! This is a test.",
    "en_default",
    "https://github.com/gradio-app/gradio/raw/main/test/test_files/audio_sample.wav",
    True,
    fn_index=1
)

info, audio, ref = result
print(f"SUCCESS! Info: {info}")
print(f"Audio: {audio}")

