#!/usr/bin/env python3
"""
Process Your Voice Data
=======================
Feed your voice data into the system and get audio back.
"""

import os
import sys
import time
from pathlib import Path

# Add pubsub to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pubsub.service import PubSubService, Subscriber
from pubsub.voice_processor import VoiceProcessor, OpenVoiceProcessor, FileAudioProcessor


def main():
    print("=" * 70)
    print(" Voice Processing - Feed Your Voice Data")
    print("=" * 70)
    
    # Find your voice data
    segments_dir = Path("processed_segments")
    if not segments_dir.exists():
        print("\n[ERROR] processed_segments directory not found")
        print("   Please run 'python expand_dataset.py --limit 5 --process' first")
        return
    
    wav_files = list(segments_dir.glob("*.wav"))
    if not wav_files:
        print("\n[ERROR] No WAV files found in processed_segments")
        return
    
    # Use the first available voice file
    reference_audio = wav_files[0]
    print(f"\n[1] Found reference voice: {reference_audio.name}")
    print(f"    Path: {reference_audio}")
    
    # Create pub/sub service
    print("\n[2] Starting pub/sub service...")
    service = PubSubService()
    service.start()
    
    # Create voice processor
    processor = VoiceProcessor(service=service)
    
    # Register processors
    print("\n[3] Registering processors...")
    
    # File processor (always available)
    file_proc = FileAudioProcessor()
    processor.register_processor("file", file_proc)
    print("  [OK] File processor registered")
    
    # OpenVoice processor (if token available)
    hf_token = os.getenv("HF_TOKEN")
    if hf_token:
        try:
            openvoice_proc = OpenVoiceProcessor(hf_token=hf_token)
            processor.register_processor("openvoice", openvoice_proc)
            print("  [OK] OpenVoice processor registered")
            use_openvoice = True
        except Exception as e:
            print(f"  ⚠ OpenVoice processor failed: {e}")
            use_openvoice = False
    else:
        print("  [WARNING] HF_TOKEN not set - using file processor only")
        print("  Set HF_TOKEN environment variable to use OpenVoice")
        use_openvoice = False
    
    # Collect responses
    responses = []
    
    def response_handler(message):
        """Handle audio generation responses"""
        response = message.payload
        responses.append(response)
        
        # Handle both dict and AudioResponse objects
        if isinstance(response, dict):
            request_id = response.get('request_id', 'unknown')
            success = response.get('success', False)
            audio_path = response.get('audio_path')
            error = response.get('error')
            processor_name = response.get('metadata', {}).get('processor', 'unknown')
        else:
            request_id = getattr(response, 'request_id', 'unknown')
            success = getattr(response, 'success', False)
            audio_path = getattr(response, 'audio_path', None)
            error = getattr(response, 'error', None)
            processor_name = getattr(response, 'metadata', {}).get('processor', 'unknown')
        
        print(f"\n  📢 Response for request: {request_id[:8]}...")
        if success:
            print(f"    [SUCCESS]")
            print(f"    📁 Audio saved to: {audio_path}")
            print(f"    🔧 Processor: {processor_name}")
            
            # Check if file exists
            if audio_path and Path(audio_path).exists():
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
            if status_msg:
                print(f"  📊 {status_msg}")
    
    subscriber.subscribe("voice.status", status_handler)
    
    print("\n[4] Subscribed to responses and status")
    
    # Test texts to generate
    test_texts = [
        "Hello, this is a test of voice cloning using my own voice data.",
        "The system is processing my voice and generating new audio.",
        "This demonstrates the pub/sub messaging system for voice processing."
    ]
    
    print("\n[5] Processing voice data...")
    print("-" * 70)
    
    request_ids = []
    for i, text in enumerate(test_texts, 1):
        print(f"\n  Request {i}/{len(test_texts)}: {text[:50]}...")
        
        request_id = processor.request_audio(
            text=text,
            reference_audio_path=str(reference_audio),
            style="en_default",
            metadata={"test_number": i}
        )
        request_ids.append(request_id)
        print(f"    Request ID: {request_id[:8]}...")
        
        # Small delay between requests
        time.sleep(0.5)
    
    # Wait for all processing to complete
    print(f"\n[6] Waiting for processing to complete...")
    print("    (This may take a while if using OpenVoice API)")
    
    max_wait = 30 if use_openvoice else 5
    waited = 0
    while len(responses) < len(test_texts) and waited < max_wait:
        time.sleep(1)
        waited += 1
        if waited % 5 == 0:
            print(f"    Waiting... ({waited}s / {max_wait}s)")
    
    # Summary
    print("\n" + "=" * 70)
    print(" RESULTS SUMMARY")
    print("=" * 70)
    
    stats = processor.get_stats()
    print(f"\n  Requests received: {stats['requests_received']}")
    print(f"  Requests processed: {stats['requests_processed']}")
    print(f"  Requests failed: {stats['requests_failed']}")
    print(f"  Responses collected: {len(responses)}")
    
    # Show successful outputs
    successful = [r for r in responses if (
        (isinstance(r, dict) and r.get('success')) or
        (hasattr(r, 'success') and r.success)
    )]
    
    if successful:
        print(f"\n  [SUCCESS] Successful generations: {len(successful)}")
        print("\n  Generated audio files:")
        for i, resp in enumerate(successful, 1):
            if isinstance(resp, dict):
                audio_path = resp.get('audio_path')
                processor_name = resp.get('metadata', {}).get('processor', 'unknown')
            else:
                audio_path = getattr(resp, 'audio_path', None)
                processor_name = getattr(resp, 'metadata', {}).get('processor', 'unknown')
            
            if audio_path:
                file_path = Path(audio_path)
                if file_path.exists():
                    size = file_path.stat().st_size
                    print(f"    {i}. {file_path.name} ({size:,} bytes) - {processor_name}")
                else:
                    print(f"    {i}. {file_path.name} (file not found) - {processor_name}")
    
    failed = len(responses) - len(successful)
    if failed > 0:
        print(f"\n  [FAILED] Failed generations: {failed}")
    
    # Cleanup
    print("\n[7] Cleaning up...")
    subscriber.unsubscribe_all()
    service.stop()
    print("  Service stopped")
    
    print("\n" + "=" * 70)
    print(" Done! Check the voice_clone_output directory for generated audio.")
    print("=" * 70)


if __name__ == "__main__":
    main()

