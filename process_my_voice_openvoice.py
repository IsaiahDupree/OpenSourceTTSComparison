#!/usr/bin/env python3
"""
Process Your Voice Data with OpenVoice
======================================
Feed your voice data and get actual generated audio back using OpenVoice.
"""

import os
import sys
import time
from pathlib import Path

# Add pubsub to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pubsub.service import PubSubService, Subscriber
from pubsub.voice_processor import VoiceProcessor, OpenVoiceProcessor


def main():
    print("=" * 70)
    print(" Voice Processing with OpenVoice - Generate New Audio")
    print("=" * 70)
    
    # Check for token
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        print("\n[ERROR] HF_TOKEN environment variable not set")
        print("   Set it with: $env:HF_TOKEN='your_token_here'")
        return
    
    # Find your voice data
    segments_dir = Path("processed_segments")
    if not segments_dir.exists():
        print("\n[ERROR] processed_segments directory not found")
        return
    
    wav_files = list(segments_dir.glob("*.wav"))
    if not wav_files:
        print("\n[ERROR] No WAV files found in processed_segments")
        return
    
    # Use the first available voice file
    reference_audio = wav_files[0]
    print(f"\n[1] Using reference voice: {reference_audio.name}")
    print(f"    Path: {reference_audio.resolve()}")
    
    # Create pub/sub service
    print("\n[2] Starting pub/sub service...")
    service = PubSubService()
    service.start()
    
    # Create voice processor
    processor = VoiceProcessor(service=service)
    
    # Register ONLY OpenVoice processor (so it's used first)
    print("\n[3] Registering OpenVoice processor...")
    try:
        openvoice_proc = OpenVoiceProcessor(hf_token=hf_token)
        processor.register_processor("openvoice", openvoice_proc)
        print("  [OK] OpenVoice processor registered")
    except Exception as e:
        print(f"  [ERROR] Failed to initialize OpenVoice: {e}")
        service.stop()
        return
    
    # Collect responses
    responses = []
    
    def response_handler(message):
        """Handle audio generation responses"""
        response = message.payload
        
        # Handle both dict and AudioResponse objects
        if isinstance(response, dict):
            request_id = response.get('request_id', 'unknown')
            success = response.get('success', False)
            audio_path = response.get('audio_path')
            error = response.get('error')
        else:
            request_id = getattr(response, 'request_id', 'unknown')
            success = getattr(response, 'success', False)
            audio_path = getattr(response, 'audio_path', None)
            error = getattr(response, 'error', None)
        
        responses.append({
            'request_id': request_id,
            'success': success,
            'audio_path': audio_path,
            'error': error
        })
        
        print(f"\n  📢 Response for request: {request_id[:8]}...")
        if success:
            print(f"    [SUCCESS]")
            if audio_path:
                print(f"    📁 Audio saved to: {audio_path}")
                if Path(audio_path).exists():
                    file_size = Path(audio_path).stat().st_size
                    print(f"    📊 File size: {file_size:,} bytes")
        else:
            print(f"    [FAILED] {error}")
    
    # Subscribe to responses
    subscriber = Subscriber(service)
    subscriber.subscribe("voice.response", response_handler)
    
    # Subscribe to status
    def status_handler(message):
        status = message.payload
        if isinstance(status, dict):
            status_msg = status.get('message', '')
            if status_msg and 'Trying processor' not in status_msg:
                print(f"  📊 {status_msg}")
    
    subscriber.subscribe("voice.status", status_handler)
    
    print("\n[4] Subscribed to responses")
    
    # Test text to generate
    test_text = "Hello, this is a test of voice cloning. I am using my own voice data to generate new speech with OpenVoice."
    
    print("\n[5] Generating audio from your voice...")
    print("-" * 70)
    print(f"  Text: {test_text}")
    print(f"  Reference: {reference_audio.name}")
    print(f"  Style: en_default")
    
    request_id = processor.request_audio(
        text=test_text,
        reference_audio_path=str(reference_audio),
        style="en_default",
        metadata={"test": True}
    )
    
    print(f"\n  Request ID: {request_id}")
    print("  Processing... (this may take 10-30 seconds)")
    
    # Wait for processing
    max_wait = 60
    waited = 0
    while len(responses) == 0 and waited < max_wait:
        time.sleep(2)
        waited += 2
        if waited % 10 == 0:
            print(f"    Still processing... ({waited}s)")
    
    # Results
    print("\n" + "=" * 70)
    print(" RESULTS")
    print("=" * 70)
    
    if responses:
        resp = responses[0]
        if resp['success']:
            print("\n  [SUCCESS] Audio generated successfully")
            print(f"  📁 Output file: {resp['audio_path']}")
            
            audio_file = Path(resp['audio_path'])
            if audio_file.exists():
                size = audio_file.stat().st_size
                print(f"  📊 File size: {size:,} bytes")
                print(f"  📍 Full path: {audio_file.resolve()}")
                print("\n  🎵 You can now play this audio file!")
            else:
                print("  [WARNING] File path reported but file not found")
        else:
            print(f"\n  [FAILED] {resp['error']}")
    else:
        print("\n  [WARNING] No response received (timeout or error)")
        print("  Check the status messages above for details")
    
    stats = processor.get_stats()
    print(f"\n  Statistics:")
    print(f"    Requests received: {stats['requests_received']}")
    print(f"    Requests processed: {stats['requests_processed']}")
    print(f"    Requests failed: {stats['requests_failed']}")
    
    # Cleanup
    print("\n[6] Cleaning up...")
    subscriber.unsubscribe_all()
    service.stop()
    print("  Service stopped")
    
    print("\n" + "=" * 70)
    if responses and responses[0]['success']:
        print(" [SUCCESS] Done! Your generated audio is ready!")
    else:
        print(" [INFO] Check the output above for details")
    print("=" * 70)


if __name__ == "__main__":
    main()

