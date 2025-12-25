# Pub/Sub Service Framework

A lightweight, thread-safe publish-subscribe messaging system with topic support.

## Features

- **Topic-based messaging**: Organize messages by topics
- **Multiple subscribers**: Multiple callbacks per topic
- **Message priority**: Support for priority levels (LOW, NORMAL, HIGH, URGENT)
- **Message history**: Automatic message history per topic
- **Thread-safe**: Safe for concurrent operations
- **Statistics**: Built-in statistics tracking
- **Easy to use**: Simple API with Publisher/Subscriber convenience classes

## Quick Start

### Basic Usage

```python
from pubsub.service import PubSubService

# Create and start service
service = PubSubService()
service.start()

# Subscribe to a topic
def message_handler(message):
    print(f"Received: {message.payload}")

service.subscribe("news", message_handler)

# Publish a message
service.publish("news", "Breaking news!")

# Cleanup
service.stop()
```

### Using Publisher and Subscriber Classes

```python
from pubsub.service import PubSubService, Publisher, Subscriber, MessagePriority

service = PubSubService()
service.start()

# Create publisher with default topic
publisher = Publisher(service, default_topic="events")

# Create subscriber
subscriber = Subscriber(service)

def handler(msg):
    print(f"Event: {msg.payload}")

subscriber.subscribe("events", handler)

# Publish with priority
publisher.publish("User logged in", priority=MessagePriority.HIGH)

service.stop()
```

## API Reference

### PubSubService

Main service class for managing topics and messages.

#### Methods

- `create_topic(topic_name: str) -> Topic`: Create a new topic
- `get_topic(topic_name: str) -> Optional[Topic]`: Get existing topic
- `delete_topic(topic_name: str) -> bool`: Delete a topic
- `list_topics() -> List[str]`: List all topic names
- `subscribe(topic_name: str, callback: Callable) -> bool`: Subscribe to topic
- `unsubscribe(topic_name: str, callback: Callable) -> bool`: Unsubscribe from topic
- `publish(topic_name: str, payload: Any, priority: MessagePriority, metadata: Dict) -> str`: Publish message
- `start()`: Start message processing worker
- `stop(wait: bool, timeout: float)`: Stop message processing
- `get_stats() -> Dict`: Get service statistics
- `get_topic_stats(topic_name: str) -> Optional[Dict]`: Get topic statistics
- `clear_topic_history(topic_name: str) -> bool`: Clear topic message history

### Message

Message structure with the following fields:

- `topic: str`: Topic name
- `payload: Any`: Message data
- `message_id: str`: Unique message ID
- `timestamp: float`: Creation timestamp
- `priority: MessagePriority`: Message priority
- `metadata: Dict[str, Any]`: Additional metadata

### MessagePriority

Enum values: `LOW`, `NORMAL`, `HIGH`, `URGENT`

### Publisher

Convenience class for publishing messages.

```python
publisher = Publisher(service, default_topic="events")
publisher.publish("Message", priority=MessagePriority.HIGH)
```

### Subscriber

Convenience class for managing subscriptions.

```python
subscriber = Subscriber(service)
subscriber.subscribe("topic", handler)
subscriber.unsubscribe_all()  # Unsubscribe from all topics
```

## Examples

See `examples/pubsub_example.py` for comprehensive examples.

## Running Tests

```bash
python -m pytest tests/test_pubsub.py
# or
python -m unittest tests.test_pubsub
```

## Thread Safety

All operations are thread-safe. Multiple threads can publish, subscribe, and perform other operations concurrently.

## Message Processing

Messages are processed asynchronously in a background worker thread. Higher priority messages are processed first.

## Statistics

The service tracks:
- Messages published
- Messages delivered
- Messages failed
- Active topics
- Queue size

Use `get_stats()` to retrieve statistics.

