# Voice Processing with Pub/Sub Guide

## Overview

The voice processing system allows you to feed voice data into the pub/sub framework and get audio back. It integrates with voice cloning services like OpenVoice.

## Quick Start

### Basic Usage

```python
from pubsub.service import PubSubService
from pubsub.voice_processor import VoiceProcessor, FileAudioProcessor

# Create service
service = PubSubService()
service.start()

# Create voice processor
processor = VoiceProcessor(service=service)

# Register a processor
file_proc = FileAudioProcessor()
processor.register_processor("file", file_proc)

# Subscribe to responses
def handle_response(message):
    response = message.payload
    if response.success:
        print(f"Audio saved to: {response.audio_path}")
    else:
        print(f"Error: {response.error}")

from pubsub.service import Subscriber
subscriber = Subscriber(service)
subscriber.subscribe("voice.response", handle_response)

# Request audio generation
request_id = processor.request_audio(
    text="Hello, this is a test",
    reference_audio_path="path/to/reference.wav",
    style="en_default"
)

# Wait for processing...
import time
time.sleep(2.0)

# Cleanup
service.stop()
```

## Topics

The system uses three main topics:

1. **`voice.request`**: Publish audio generation requests here
2. **`voice.response`**: Subscribe here to receive generated audio
3. **`voice.status`**: Status updates during processing

## Request Format

### Using AudioRequest

```python
from pubsub.voice_processor import AudioRequest

request = AudioRequest(
    text="Text to synthesize",
    reference_audio_path="path/to/reference.wav",
    style="en_default",  # or "en_us", "en_br", etc.
    metadata={"user_id": 123}
)

service.publish("voice.request", request)
```

### Using Convenience Method

```python
request_id = processor.request_audio(
    text="Text to synthesize",
    reference_audio_path="path/to/reference.wav",
    style="en_default"
)
```

## Response Format

Responses are `AudioResponse` objects with:

- `request_id`: ID of the original request
- `audio_path`: Path to generated audio file (if successful)
- `success`: Boolean indicating success
- `error`: Error message (if failed)
- `metadata`: Additional metadata

## Processors

### FileAudioProcessor

Simple processor for testing that saves request info to files.

```python
from pubsub.voice_processor import FileAudioProcessor

processor = FileAudioProcessor(output_dir="output")
processor.register_processor("file", processor)
```

### OpenVoiceProcessor

Processor that uses OpenVoice API for voice cloning.

```python
from pubsub.voice_processor import OpenVoiceProcessor
import os

# Set HF_TOKEN environment variable
os.environ["HF_TOKEN"] = "your_token_here"

openvoice_proc = OpenVoiceProcessor()
processor.register_processor("openvoice", openvoice_proc)
```

### Custom Processor

Create your own processor:

```python
def my_processor(request: AudioRequest) -> AudioResponse:
    # Process the request
    # ...
    
    return AudioResponse(
        request_id=request.request_id,
        audio_path="path/to/output.wav",
        success=True,
        metadata={"processor": "my_custom"}
    )

processor.register_processor("custom", my_processor)
```

## Status Updates

Subscribe to status updates:

```python
def status_handler(message):
    status = message.payload
    print(f"Status: {status['status']} - {status['message']}")

subscriber.subscribe("voice.status", status_handler)
```

## Example: Complete Workflow

```python
import os
import time
from pubsub.service import PubSubService, Subscriber
from pubsub.voice_processor import (
    VoiceProcessor, 
    OpenVoiceProcessor,
    AudioRequest
)

# Setup
service = PubSubService()
service.start()

processor = VoiceProcessor(service=service)

# Register OpenVoice processor
if os.getenv("HF_TOKEN"):
    openvoice = OpenVoiceProcessor()
    processor.register_processor("openvoice", openvoice)

# Response handler
responses = []
def handle_response(msg):
    resp = msg.payload
    responses.append(resp)
    if resp.success:
        print(f"✅ Audio: {resp.audio_path}")
    else:
        print(f"❌ Error: {resp.error}")

subscriber = Subscriber(service)
subscriber.subscribe("voice.response", handle_response)

# Make request
request_id = processor.request_audio(
    text="This is a test of voice cloning",
    reference_audio_path="processed_segments/reference.wav",
    style="en_default"
)

print(f"Request ID: {request_id}")

# Wait for processing
time.sleep(5.0)

# Check results
print(f"Received {len(responses)} responses")

# Cleanup
service.stop()
```

## Running the Example

```bash
# Set your HuggingFace token
export HF_TOKEN=your_token_here

# Run the example
python examples/voice_pubsub_example.py
```

## Testing

```bash
# Run voice processor tests
python -m unittest tests.test_voice_processor -v
```

## Integration with Existing Systems

The voice processor can integrate with:
- OpenVoice API (via HuggingFace Spaces)
- Local TTS systems
- Custom voice cloning services

Just register your processor function and it will be called automatically when requests arrive.

