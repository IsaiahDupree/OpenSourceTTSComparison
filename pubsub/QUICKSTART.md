# Pub/Sub Service Quick Start

## Installation

No external dependencies required! Uses only Python standard library.

## Basic Usage

```python
from pubsub.service import PubSubService

# Create and start service
service = PubSubService()
service.start()

# Define a message handler
def handle_message(message):
    print(f"Received: {message.payload}")

# Subscribe to a topic
service.subscribe("news", handle_message)

# Publish a message
service.publish("news", "Hello, World!")

# Cleanup
service.stop()
```

## Running Tests

```bash
# Run all tests
python -m unittest tests.test_pubsub -v

# Run specific test class
python -m unittest tests.test_pubsub.TestPubSubService -v
```

## Running Examples

```bash
python examples/pubsub_example.py
```

## Key Features

✅ Topic-based messaging  
✅ Multiple subscribers per topic  
✅ Message priority (LOW, NORMAL, HIGH, URGENT)  
✅ Message history  
✅ Thread-safe  
✅ Statistics tracking  
✅ Publisher/Subscriber convenience classes  

## File Structure

```
pubsub/
├── __init__.py          # Package exports
├── service.py           # Main service implementation
├── README.md            # Full documentation
└── QUICKSTART.md        # This file

tests/
└── test_pubsub.py       # Comprehensive test suite

examples/
└── pubsub_example.py    # Usage examples
```

## Next Steps

- Read `README.md` for full API documentation
- Check `examples/pubsub_example.py` for more examples
- Run tests to see all features in action

