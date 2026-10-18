"""
Comprehensive tests for Pub/Sub Service Framework
"""

import unittest
import time
import threading
from pubsub.service import (
    PubSubService,
    Publisher,
    Subscriber,
    Message,
    MessagePriority
)


class TestPubSubService(unittest.TestCase):
    """Test cases for PubSubService"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.service = PubSubService()
        self.service.start()
        self.received_messages = []
    
    def tearDown(self):
        """Clean up after tests"""
        self.service.stop()
        self.received_messages.clear()
    
    def message_handler(self, message: Message):
        """Test message handler"""
        self.received_messages.append(message)
    
    def test_create_topic(self):
        """Test topic creation"""
        topic = self.service.create_topic("test_topic")
        self.assertIsNotNone(topic)
        self.assertEqual(topic.name, "test_topic")
        
        # Creating again should return same topic
        topic2 = self.service.create_topic("test_topic")
        self.assertEqual(topic, topic2)
    
    def test_get_topic(self):
        """Test getting existing topic"""
        self.service.create_topic("test_topic")
        topic = self.service.get_topic("test_topic")
        self.assertIsNotNone(topic)
        self.assertEqual(topic.name, "test_topic")
        
        # Non-existent topic
        topic = self.service.get_topic("nonexistent")
        self.assertIsNone(topic)
    
    def test_list_topics(self):
        """Test listing all topics"""
        self.assertEqual(len(self.service.list_topics()), 0)
        
        self.service.create_topic("topic1")
        self.service.create_topic("topic2")
        
        topics = self.service.list_topics()
        self.assertEqual(len(topics), 2)
        self.assertIn("topic1", topics)
        self.assertIn("topic2", topics)
    
    def test_delete_topic(self):
        """Test topic deletion"""
        self.service.create_topic("test_topic")
        self.assertTrue("test_topic" in self.service.list_topics())
        
        result = self.service.delete_topic("test_topic")
        self.assertTrue(result)
        self.assertFalse("test_topic" in self.service.list_topics())
        
        # Deleting non-existent topic
        result = self.service.delete_topic("nonexistent")
        self.assertFalse(result)
    
    def test_subscribe(self):
        """Test subscribing to a topic"""
        result = self.service.subscribe("test_topic", self.message_handler)
        self.assertTrue(result)
        
        topic = self.service.get_topic("test_topic")
        self.assertEqual(topic.get_subscriber_count(), 1)
        
        # Subscribe again (should not duplicate)
        result = self.service.subscribe("test_topic", self.message_handler)
        self.assertFalse(result)  # Already subscribed
    
    def test_unsubscribe(self):
        """Test unsubscribing from a topic"""
        self.service.subscribe("test_topic", self.message_handler)
        topic = self.service.get_topic("test_topic")
        self.assertEqual(topic.get_subscriber_count(), 1)
        
        result = self.service.unsubscribe("test_topic", self.message_handler)
        self.assertTrue(result)
        self.assertEqual(topic.get_subscriber_count(), 0)
        
        # Unsubscribe from non-existent topic
        result = self.service.unsubscribe("nonexistent", self.message_handler)
        self.assertFalse(result)
    
    def test_publish_and_receive(self):
        """Test publishing and receiving messages"""
        self.service.subscribe("test_topic", self.message_handler)
        
        message_id = self.service.publish("test_topic", "Hello, World!")
        
        # Wait for message to be processed
        time.sleep(0.2)
        
        self.assertEqual(len(self.received_messages), 1)
        self.assertEqual(self.received_messages[0].payload, "Hello, World!")
        self.assertEqual(self.received_messages[0].topic, "test_topic")
        self.assertEqual(self.received_messages[0].message_id, message_id)
    
    def test_multiple_subscribers(self):
        """Test multiple subscribers to same topic"""
        messages1 = []
        messages2 = []
        
        def handler1(msg):
            messages1.append(msg)
        
        def handler2(msg):
            messages2.append(msg)
        
        self.service.subscribe("test_topic", handler1)
        self.service.subscribe("test_topic", handler2)
        
        self.service.publish("test_topic", "Test message")
        
        # Wait for processing
        time.sleep(0.2)
        
        self.assertEqual(len(messages1), 1)
        self.assertEqual(len(messages2), 1)
        self.assertEqual(messages1[0].payload, "Test message")
        self.assertEqual(messages2[0].payload, "Test message")
    
    def test_message_priority(self):
        """Test message priority ordering"""
        received_order = []
        
        def handler(msg):
            received_order.append((msg.priority, msg.payload))
        
        self.service.subscribe("test_topic", handler)
        
        # Publish messages with different priorities
        self.service.publish("test_topic", "Low", priority=MessagePriority.LOW)
        self.service.publish("test_topic", "High", priority=MessagePriority.HIGH)
        self.service.publish("test_topic", "Normal", priority=MessagePriority.NORMAL)
        self.service.publish("test_topic", "Urgent", priority=MessagePriority.URGENT)
        
        # Wait for processing
        time.sleep(0.5)
        
        # Check that all messages were received
        self.assertEqual(len(received_order), 4)
        
        # Higher priority messages should be processed first (due to priority queue)
        priorities = [p for p, _ in received_order]
        # Urgent should be first, then High, then Normal, then Low
        self.assertEqual(priorities[0], MessagePriority.URGENT)
        self.assertEqual(priorities[1], MessagePriority.HIGH)
    
    def test_message_metadata(self):
        """Test message metadata"""
        self.service.subscribe("test_topic", self.message_handler)
        
        metadata = {"source": "test", "version": "1.0"}
        self.service.publish("test_topic", "Test", metadata=metadata)
        
        time.sleep(0.2)
        
        self.assertEqual(len(self.received_messages), 1)
        self.assertEqual(self.received_messages[0].metadata, metadata)
    
    def test_message_history(self):
        """Test message history"""
        topic = self.service.create_topic("test_topic")
        
        self.service.publish("test_topic", "Message 1")
        self.service.publish("test_topic", "Message 2")
        self.service.publish("test_topic", "Message 3")
        
        time.sleep(0.3)
        
        with topic.lock:
            self.assertEqual(len(topic.message_history), 3)
            self.assertEqual(topic.message_history[0].payload, "Message 1")
            self.assertEqual(topic.message_history[2].payload, "Message 3")
    
    def test_service_stats(self):
        """Test service statistics"""
        stats = self.service.get_stats()
        self.assertIn('messages_published', stats)
        self.assertIn('messages_delivered', stats)
        self.assertIn('active_topics', stats)
        self.assertIn('running', stats)
        
        self.service.publish("test_topic", "Test")
        self.service.subscribe("test_topic", self.message_handler)
        self.service.publish("test_topic", "Test 2")
        
        time.sleep(0.2)
        
        stats = self.service.get_stats()
        self.assertEqual(stats['messages_published'], 2)
        self.assertEqual(stats['active_topics'], 1)
    
    def test_topic_stats(self):
        """Test topic statistics"""
        self.service.subscribe("test_topic", self.message_handler)
        self.service.publish("test_topic", "Message 1")
        self.service.publish("test_topic", "Message 2")
        
        time.sleep(0.2)
        
        stats = self.service.get_topic_stats("test_topic")
        self.assertIsNotNone(stats)
        self.assertEqual(stats['name'], "test_topic")
        self.assertEqual(stats['subscribers'], 1)
        self.assertEqual(stats['message_count'], 2)
    
    def test_clear_topic_history(self):
        """Test clearing topic history"""
        self.service.publish("test_topic", "Message 1")
        self.service.publish("test_topic", "Message 2")
        
        time.sleep(0.2)
        
        topic = self.service.get_topic("test_topic")
        self.assertEqual(len(topic.message_history), 2)
        
        result = self.service.clear_topic_history("test_topic")
        self.assertTrue(result)
        self.assertEqual(len(topic.message_history), 0)
    
    def test_thread_safety(self):
        """Test thread safety with concurrent operations"""
        def publish_messages():
            for i in range(10):
                self.service.publish("test_topic", f"Message {i}")
        
        def subscribe_handler(msg):
            self.received_messages.append(msg)
        
        # Subscribe
        self.service.subscribe("test_topic", subscribe_handler)
        
        # Create multiple threads publishing
        threads = []
        for _ in range(5):
            t = threading.Thread(target=publish_messages)
            threads.append(t)
            t.start()
        
        # Wait for all threads
        for t in threads:
            t.join()
        
        # Wait for message processing
        time.sleep(0.5)
        
        # Should have received all messages
        self.assertEqual(len(self.received_messages), 50)


class TestPublisher(unittest.TestCase):
    """Test cases for Publisher class"""
    
    def setUp(self):
        self.service = PubSubService()
        self.service.start()
        self.publisher = Publisher(self.service, "default_topic")
    
    def tearDown(self):
        self.service.stop()
    
    def test_publish_with_default_topic(self):
        """Test publishing with default topic"""
        messages = []
        
        def handler(msg):
            messages.append(msg)
        
        self.service.subscribe("default_topic", handler)
        message_id = self.publisher.publish("Test message")
        
        time.sleep(0.2)
        
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].payload, "Test message")
        self.assertIsNotNone(message_id)
    
    def test_publish_with_specific_topic(self):
        """Test publishing to specific topic"""
        messages = []
        
        def handler(msg):
            messages.append(msg)
        
        self.service.subscribe("custom_topic", handler)
        self.publisher.publish("Test", topic="custom_topic")
        
        time.sleep(0.2)
        
        self.assertEqual(len(messages), 1)
    
    def test_publish_without_topic(self):
        """Test publishing without topic should raise error"""
        publisher = Publisher(self.service)  # No default topic
        
        with self.assertRaises(ValueError):
            publisher.publish("Test")


class TestSubscriber(unittest.TestCase):
    """Test cases for Subscriber class"""
    
    def setUp(self):
        self.service = PubSubService()
        self.service.start()
        self.subscriber = Subscriber(self.service)
        self.received_messages = []
    
    def tearDown(self):
        self.subscriber.unsubscribe_all()
        self.service.stop()
    
    def test_subscribe(self):
        """Test subscribing to topics"""
        def handler(msg):
            self.received_messages.append(msg)
        
        self.subscriber.subscribe("topic1", handler)
        self.subscriber.subscribe("topic2", handler)
        
        self.service.publish("topic1", "Message 1")
        self.service.publish("topic2", "Message 2")
        
        time.sleep(0.2)
        
        self.assertEqual(len(self.received_messages), 2)
    
    def test_unsubscribe_all(self):
        """Test unsubscribing from all topics"""
        def handler(msg):
            self.received_messages.append(msg)
        
        self.subscriber.subscribe("topic1", handler)
        self.subscriber.subscribe("topic2", handler)
        
        self.subscriber.unsubscribe_all()
        
        self.service.publish("topic1", "Message 1")
        self.service.publish("topic2", "Message 2")
        
        time.sleep(0.2)
        
        # Should not receive any messages
        self.assertEqual(len(self.received_messages), 0)


class TestMessage(unittest.TestCase):
    """Test cases for Message class"""
    
    def test_message_creation(self):
        """Test message creation with defaults"""
        msg = Message(topic="test", payload="data")
        
        self.assertIsNotNone(msg.message_id)
        self.assertIsNotNone(msg.timestamp)
        self.assertEqual(msg.priority, MessagePriority.NORMAL)
        self.assertIsNotNone(msg.metadata)
    
    def test_message_custom_values(self):
        """Test message creation with custom values"""
        metadata = {"key": "value"}
        msg = Message(
            topic="test",
            payload="data",
            priority=MessagePriority.HIGH,
            metadata=metadata
        )
        
        self.assertEqual(msg.topic, "test")
        self.assertEqual(msg.payload, "data")
        self.assertEqual(msg.priority, MessagePriority.HIGH)
        self.assertEqual(msg.metadata, metadata)


if __name__ == '__main__':
    unittest.main()

