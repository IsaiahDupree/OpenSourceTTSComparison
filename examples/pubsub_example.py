#!/usr/bin/env python3
"""
Pub/Sub Service Example Usage
===============================
Demonstrates how to use the pub/sub framework.
"""

import sys
import os
import time

# Add parent directory to path to import pubsub
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pubsub.service import PubSubService, Publisher, Subscriber, MessagePriority


def main():
    print("=" * 70)
    print(" Pub/Sub Service Example")
    print("=" * 70)
    
    # Create service
    service = PubSubService()
    service.start()
    print("\n[1] Service started")
    
    # Example 1: Basic publish/subscribe
    print("\n[2] Example 1: Basic Publish/Subscribe")
    print("-" * 70)
    
    def message_handler(message):
        print(f"  Received: {message.payload} (from {message.topic})")
    
    service.subscribe("news", message_handler)
    service.publish("news", "Breaking: New AI model released!")
    time.sleep(0.2)
    
    # Example 2: Multiple subscribers
    print("\n[3] Example 2: Multiple Subscribers")
    print("-" * 70)
    
    subscriber1_messages = []
    subscriber2_messages = []
    
    def handler1(msg):
        subscriber1_messages.append(msg)
        print(f"  Subscriber 1 received: {msg.payload}")
    
    def handler2(msg):
        subscriber2_messages.append(msg)
        print(f"  Subscriber 2 received: {msg.payload}")
    
    service.subscribe("alerts", handler1)
    service.subscribe("alerts", handler2)
    
    service.publish("alerts", "System alert: High CPU usage")
    time.sleep(0.2)
    
    # Example 3: Using Publisher class
    print("\n[4] Example 3: Using Publisher Class")
    print("-" * 70)
    
    publisher = Publisher(service, default_topic="events")
    
    def event_handler(msg):
        print(f"  Event: {msg.payload} (Priority: {msg.priority.name})")
    
    service.subscribe("events", event_handler)
    
    publisher.publish("User logged in", priority=MessagePriority.NORMAL)
    publisher.publish("Critical error occurred", priority=MessagePriority.URGENT)
    publisher.publish("Daily backup completed", priority=MessagePriority.LOW)
    
    time.sleep(0.3)
    
    # Example 4: Using Subscriber class
    print("\n[5] Example 4: Using Subscriber Class")
    print("-" * 70)
    
    subscriber = Subscriber(service)
    
    def data_handler(msg):
        print(f"  Data received: {msg.payload}")
    
    subscriber.subscribe("data", data_handler)
    subscriber.subscribe("metrics", data_handler)
    
    service.publish("data", {"temperature": 25.5, "humidity": 60})
    service.publish("metrics", {"cpu": 45.2, "memory": 78.1})
    
    time.sleep(0.2)
    
    # Example 5: Message with metadata
    print("\n[6] Example 5: Messages with Metadata")
    print("-" * 70)
    
    def metadata_handler(msg):
        print(f"  Message: {msg.payload}")
        print(f"  Metadata: {msg.metadata}")
    
    service.subscribe("logs", metadata_handler)
    
    service.publish(
        "logs",
        "Processing complete",
        metadata={"user_id": 123, "action": "upload", "timestamp": time.time()}
    )
    
    time.sleep(0.2)
    
    # Example 6: Service statistics
    print("\n[7] Example 6: Service Statistics")
    print("-" * 70)
    
    stats = service.get_stats()
    print(f"  Messages published: {stats['messages_published']}")
    print(f"  Messages delivered: {stats['messages_delivered']}")
    print(f"  Active topics: {stats['active_topics']}")
    print(f"  Queue size: {stats['queue_size']}")
    
    topic_stats = service.get_topic_stats("news")
    if topic_stats:
        print(f"\n  Topic 'news' stats:")
        print(f"    Subscribers: {topic_stats['subscribers']}")
        print(f"    Message count: {topic_stats['message_count']}")
    
    # Cleanup
    print("\n[8] Cleaning up...")
    subscriber.unsubscribe_all()
    service.stop()
    print("  Service stopped")
    
    print("\n" + "=" * 70)
    print(" Example completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()

