#!/usr/bin/env python3
"""
Voice Processing with Pub/Sub Example
=====================================
Demonstrates using pub/sub for voice/audio processing.
"""

import sys
import os
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pubsub.service import PubSubService, Subscriber, MessagePriority
from pubsub.voice_processor import VoiceProcessor, AudioRequest, FileAudioProcessor, OpenVoiceProcessor


def main():
    print("=" * 70)
    print(" Voice Processing with Pub/Sub Example")
    print("=" * 70)
    
    # Create pub/sub service
    service = PubSubService()
    service.start()
    print("\n[1] Pub/Sub service started")
    
    # Create voice processor
    processor = VoiceProcessor(service=service)
    
    # Register processors
    print("\n[2] Registering processors...")
    
    # Register file processor (for testing)
    file_processor = FileAudioProcessor()
    processor.register_processor("file", file_processor)
    print("  ✓ File processor registered")
    
    # Try to register OpenVoice processor if token available
    hf_token = os.getenv("HF_TOKEN")
    if hf_token:
        try:
            openvoice_processor = OpenVoiceProcessor(hf_token=hf_token)
            processor.register_processor("openvoice", openvoice_processor)
            print("  ✓ OpenVoice processor registered")
        except Exception as e:
            print(f"  ⚠ OpenVoice processor failed: {e}")
    else:
        print("  ⚠ HF_TOKEN not set, skipping OpenVoice processor")
    
    # Create response collector
    responses = []
    
    def response_handler(message):
        """Handle audio generation responses"""
        response = message.payload
        responses.append(response)
        
        if isinstance(response, dict):
            # Convert dict to AudioResponse-like object for display
            request_id = response.get('request_id', 'unknown')
            success = response.get('success', False)
            audio_path = response.get('audio_path')
            error = response.get('error')
            
            print(f"\n  📢 Response received for request: {request_id}")
            if success:
                print(f"    ✅ Success! Audio saved to: {audio_path}")
            else:
                print(f"    ❌ Failed: {error}")
        else:
            print(f"\n  📢 Response: {response}")
    
    # Subscribe to responses
    response_subscriber = Subscriber(service)
    response_subscriber.subscribe("voice.response", response_handler)
    
    # Subscribe to status updates
    status_messages = []
    
    def status_handler(message):
        """Handle status updates"""
        status_data = message.payload
        status_messages.append(status_data)
        if isinstance(status_data, dict):
            print(f"  📊 Status: {status_data.get('status')} - {status_data.get('message')}")
    
    response_subscriber.subscribe("voice.status", status_handler)
    
    print("\n[3] Subscribed to responses and status updates")
    
    # Example 1: Request with file processor
    print("\n[4] Example 1: Request audio generation (file processor)")
    print("-" * 70)
    
    # Find a reference audio file
    ref_audio = None
    segments_dir = Path("processed_segments")
    if segments_dir.exists():
        wav_files = list(segments_dir.glob("*.wav"))
        if wav_files:
            ref_audio = str(wav_files[0])
            print(f"  Using reference: {Path(ref_audio).name}")
    
    if ref_audio:
        request_id = processor.request_audio(
            text="This is a test of the voice processing system using pub/sub messaging.",
            reference_audio_path=ref_audio,
            style="en_default",
            metadata={"example": 1}
        )
        print(f"  Request ID: {request_id}")
        
        # Wait for processing
        time.sleep(1.0)
    else:
        print("  ⚠ No reference audio found, skipping example")
    
    # Example 2: Direct publish
    print("\n[5] Example 2: Direct publish to voice.request topic")
    print("-" * 70)
    
    if ref_audio:
        request = AudioRequest(
            text="Another test message for voice cloning.",
            reference_audio_path=ref_audio,
            style="en_default",
            metadata={"example": 2}
        )
        
        service.publish(
            "voice.request",
            request,
            priority=MessagePriority.NORMAL
        )
        print(f"  Published request: {request.request_id}")
        
        # Wait for processing
        time.sleep(1.0)
    
    # Example 3: Multiple requests
    print("\n[6] Example 3: Multiple concurrent requests")
    print("-" * 70)
    
    if ref_audio:
        request_ids = []
        for i in range(3):
            req_id = processor.request_audio(
                text=f"Test message number {i+1}.",
                reference_audio_path=ref_audio,
                metadata={"batch": True, "index": i+1}
            )
            request_ids.append(req_id)
        
        print(f"  Published {len(request_ids)} requests")
        
        # Wait for all to process
        time.sleep(2.0)
    
    # Summary
    print("\n[7] Summary")
    print("-" * 70)
    
    stats = processor.get_stats()
    print(f"  Requests received: {stats['requests_received']}")
    print(f"  Requests processed: {stats['requests_processed']}")
    print(f"  Requests failed: {stats['requests_failed']}")
    print(f"  Responses collected: {len(responses)}")
    print(f"  Status updates: {len(status_messages)}")
    
    # Show responses
    if responses:
        print(f"\n  Response details:")
        for i, resp in enumerate(responses[:3], 1):  # Show first 3
            if isinstance(resp, dict):
                print(f"    {i}. Request: {resp.get('request_id', 'unknown')[:8]}...")
                print(f"       Success: {resp.get('success', False)}")
                if resp.get('audio_path'):
                    print(f"       Audio: {Path(resp['audio_path']).name}")
    
    # Cleanup
    print("\n[8] Cleaning up...")
    response_subscriber.unsubscribe_all()
    service.stop()
    print("  Service stopped")
    
    print("\n" + "=" * 70)
    print(" Example completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()

