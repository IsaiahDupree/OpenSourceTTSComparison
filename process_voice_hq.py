#!/usr/bin/env python3
"""
Process Voice with High Quality OpenVoice
==========================================
Generate high-quality audio using OpenVoice API with billing enabled.
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
    print(" High Quality Voice Processing with OpenVoice")
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
    
    # Register ONLY OpenVoice processor (prioritize it)
    print("\n[3] Registering OpenVoice processor...")
    try:
        openvoice_proc = OpenVoiceProcessor(hf_token=hf_token)
        processor.register_processor("openvoice", openvoice_proc)
        print("  [OK] OpenVoice processor registered")
        print("  [INFO] Using OpenVoice for high-quality generation")
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
            processor_name = response.get('metadata', {}).get('processor', 'unknown')
        else:
            request_id = getattr(response, 'request_id', 'unknown')
            success = getattr(response, 'success', False)
            audio_path = getattr(response, 'audio_path', None)
            error = getattr(response, 'error', None)
            processor_name = getattr(response, 'metadata', {}).get('processor', 'unknown')
        
        responses.append({
            'request_id': request_id,
            'success': success,
            'audio_path': audio_path,
            'error': error,
            'processor': processor_name
        })
        
        print(f"\n  [RESPONSE] Request: {request_id[:8]}...")
        if success:
            print(f"    [SUCCESS] Audio generated!")
            if audio_path:
                print(f"    [FILE] {audio_path}")
                if Path(audio_path).exists():
                    file_size = Path(audio_path).stat().st_size
                    print(f"    [SIZE] {file_size:,} bytes")
                    print(f"    [PROCESSOR] {processor_name}")
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
                print(f"  [STATUS] {status_msg}")
    
    subscriber.subscribe("voice.status", status_handler)
    
    print("\n[4] Subscribed to responses and status")
    
    # High-quality test texts
    test_texts = [
        "Hello, this is a high-quality voice cloning test using OpenVoice. The system is generating new speech from my voice data.",
        "This demonstrates the power of modern voice synthesis technology. Each word is carefully crafted to match the original voice characteristics.",
        "The pub/sub messaging system allows for scalable and efficient voice processing workflows. This audio was generated in real-time through the API."
    ]
    
    print("\n[5] Generating high-quality audio...")
    print("-" * 70)
    
    request_ids = []
    for i, text in enumerate(test_texts, 1):
        print(f"\n  Request {i}/{len(test_texts)}:")
        print(f"    Text: {text[:60]}...")
        
        request_id = processor.request_audio(
            text=text,
            reference_audio_path=str(reference_audio),
            style="en_default",
            metadata={"hq_test": True, "test_number": i}
        )
        request_ids.append(request_id)
        print(f"    Request ID: {request_id[:8]}...")
        
        # Small delay between requests
        time.sleep(1.0)
    
    # Wait for all processing to complete
    print(f"\n[6] Waiting for processing...")
    print("    (OpenVoice API may take 15-30 seconds per request)")
    
    max_wait = 120  # 2 minutes for 3 requests
    waited = 0
    while len(responses) < len(test_texts) and waited < max_wait:
        time.sleep(3)
        waited += 3
        if waited % 15 == 0:
            print(f"    Still processing... ({waited}s / {max_wait}s)")
            print(f"    Responses received: {len(responses)}/{len(test_texts)}")
    
    # Results
    print("\n" + "=" * 70)
    print(" RESULTS")
    print("=" * 70)
    
    stats = processor.get_stats()
    print(f"\n  Statistics:")
    print(f"    Requests received: {stats['requests_received']}")
    print(f"    Requests processed: {stats['requests_processed']}")
    print(f"    Requests failed: {stats['requests_failed']}")
    print(f"    Responses collected: {len(responses)}")
    
    # Show successful outputs
    successful = [r for r in responses if r['success']]
    failed = [r for r in responses if not r['success']]
    
    if successful:
        print(f"\n  [SUCCESS] {len(successful)} high-quality audio files generated:")
        for i, resp in enumerate(successful, 1):
            audio_path = resp['audio_path']
            processor_name = resp.get('processor', 'unknown')
            if audio_path:
                file_path = Path(audio_path)
                if file_path.exists():
                    size = file_path.stat().st_size
                    print(f"    {i}. {file_path.name}")
                    print(f"       Size: {size:,} bytes")
                    print(f"       Processor: {processor_name}")
                    print(f"       Path: {file_path.resolve()}")
    
    if failed:
        print(f"\n  [FAILED] {len(failed)} requests failed:")
        for i, resp in enumerate(failed, 1):
            print(f"    {i}. Request {resp['request_id'][:8]}...")
            print(f"       Error: {resp.get('error', 'Unknown error')}")
    
    # Cleanup
    print("\n[7] Cleaning up...")
    subscriber.unsubscribe_all()
    service.stop()
    print("  Service stopped")
    
    print("\n" + "=" * 70)
    if successful:
        print(" [SUCCESS] High-quality audio generation complete!")
        print(f" Check {Path('voice_clone_output').resolve()} for your files")
    else:
        print(" [INFO] Check the output above for details")
    print("=" * 70)


if __name__ == "__main__":
    main()

