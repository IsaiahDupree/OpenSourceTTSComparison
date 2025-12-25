"""
Pub/Sub Service Framework
=========================
A lightweight publish-subscribe messaging system with topic support.
"""

import threading
import queue
import time
from typing import Callable, Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import uuid


class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class Message:
    """Message structure for pub/sub system"""
    topic: str
    payload: Any
    message_id: str = None
    timestamp: float = None
    priority: MessagePriority = MessagePriority.NORMAL
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.message_id is None:
            self.message_id = str(uuid.uuid4())
        if self.timestamp is None:
            self.timestamp = time.time()
        if self.metadata is None:
            self.metadata = {}


class Topic:
    """Represents a topic in the pub/sub system"""
    
    def __init__(self, name: str):
        self.name = name
        self.subscribers: List[Callable] = []
        self.message_history: List[Message] = []
        self.max_history: int = 100
        self.lock = threading.Lock()
        self.created_at = time.time()
        self.message_count = 0
    
    def add_subscriber(self, callback: Callable):
        """Add a subscriber callback to this topic"""
        with self.lock:
            if callback not in self.subscribers:
                self.subscribers.append(callback)
                return True
        return False
    
    def remove_subscriber(self, callback: Callable):
        """Remove a subscriber callback from this topic"""
        with self.lock:
            if callback in self.subscribers:
                self.subscribers.remove(callback)
                return True
        return False
    
    def get_subscriber_count(self) -> int:
        """Get the number of subscribers"""
        with self.lock:
            return len(self.subscribers)
    
    def add_to_history(self, message: Message):
        """Add message to history"""
        with self.lock:
            self.message_history.append(message)
            self.message_count += 1
            # Trim history if too long
            if len(self.message_history) > self.max_history:
                self.message_history.pop(0)


class PubSubService:
    """
    Main Pub/Sub Service
    
    Features:
    - Topic-based messaging
    - Multiple subscribers per topic
    - Message priority support
    - Message history
    - Thread-safe operations
    """
    
    def __init__(self, max_queue_size: int = 1000):
        self.topics: Dict[str, Topic] = {}
        self.message_queue = queue.PriorityQueue(maxsize=max_queue_size)
        self.running = False
        self.worker_thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
        self._queue_counter = 0  # Counter to ensure queue items are always comparable
        self.stats = {
            'messages_published': 0,
            'messages_delivered': 0,
            'messages_failed': 0,
            'topics_created': 0,
        }
    
    def create_topic(self, topic_name: str) -> Topic:
        """Create a new topic"""
        with self.lock:
            if topic_name not in self.topics:
                self.topics[topic_name] = Topic(topic_name)
                self.stats['topics_created'] += 1
            return self.topics[topic_name]
    
    def get_topic(self, topic_name: str) -> Optional[Topic]:
        """Get an existing topic"""
        with self.lock:
            return self.topics.get(topic_name)
    
    def delete_topic(self, topic_name: str) -> bool:
        """Delete a topic and all its subscribers"""
        with self.lock:
            if topic_name in self.topics:
                del self.topics[topic_name]
                return True
        return False
    
    def list_topics(self) -> List[str]:
        """List all topic names"""
        with self.lock:
            return list(self.topics.keys())
    
    def subscribe(self, topic_name: str, callback: Callable) -> bool:
        """
        Subscribe to a topic
        
        Args:
            topic_name: Name of the topic
            callback: Function to call when message is received
                     Should accept: callback(message: Message)
        
        Returns:
            True if subscription successful
        """
        topic = self.get_topic(topic_name)
        if topic is None:
            topic = self.create_topic(topic_name)
        return topic.add_subscriber(callback)
    
    def unsubscribe(self, topic_name: str, callback: Callable) -> bool:
        """Unsubscribe from a topic"""
        topic = self.get_topic(topic_name)
        if topic is None:
            return False
        return topic.remove_subscriber(callback)
    
    def publish(self, topic_name: str, payload: Any, 
                priority: MessagePriority = MessagePriority.NORMAL,
                metadata: Dict[str, Any] = None) -> str:
        """
        Publish a message to a topic
        
        Args:
            topic_name: Name of the topic
            payload: Message data
            priority: Message priority
            metadata: Additional metadata
        
        Returns:
            Message ID
        """
        # Create topic if it doesn't exist
        topic = self.get_topic(topic_name)
        if topic is None:
            topic = self.create_topic(topic_name)
        
        # Create message
        message = Message(
            topic=topic_name,
            payload=payload,
            priority=priority,
            metadata=metadata or {}
        )
        
        # Add to history
        topic.add_to_history(message)
        
        # Queue message for delivery (priority queue uses negative for higher priority first)
        # Add counter to ensure items are always comparable even with same priority/timestamp
        try:
            with self.lock:
                counter = self._queue_counter
                self._queue_counter += 1
            # Tuple: (-priority, timestamp, counter, message) - counter ensures comparability
            self.message_queue.put((-priority.value, time.time(), counter, message), block=False)
            self.stats['messages_published'] += 1
        except queue.Full:
            self.stats['messages_failed'] += 1
            raise RuntimeError(f"Message queue is full. Cannot publish to {topic_name}")
        
        return message.message_id
    
    def _process_message(self, message: Message):
        """Process a single message and deliver to subscribers"""
        topic = self.get_topic(message.topic)
        if topic is None:
            return
        
        # Get subscribers (copy to avoid lock issues during iteration)
        with topic.lock:
            subscribers = topic.subscribers.copy()
        
        # Deliver to all subscribers
        for callback in subscribers:
            try:
                callback(message)
                self.stats['messages_delivered'] += 1
            except Exception as e:
                self.stats['messages_failed'] += 1
                print(f"Error delivering message to subscriber: {e}")
    
    def _worker_loop(self):
        """Worker thread that processes messages from queue"""
        while self.running:
            try:
                # Get message from queue (with timeout to check running flag)
                try:
                    _, _, _, message = self.message_queue.get(timeout=0.1)
                    self._process_message(message)
                    self.message_queue.task_done()
                except queue.Empty:
                    continue
            except Exception as e:
                print(f"Error in worker loop: {e}")
    
    def start(self):
        """Start the message processing worker"""
        if self.running:
            return
        
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
    
    def stop(self, wait: bool = True, timeout: float = 5.0):
        """Stop the message processing worker"""
        if not self.running:
            return
        
        self.running = False
        
        if wait and self.worker_thread:
            self.worker_thread.join(timeout=timeout)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        with self.lock:
            return {
                **self.stats,
                'active_topics': len(self.topics),
                'queue_size': self.message_queue.qsize(),
                'running': self.running
            }
    
    def get_topic_stats(self, topic_name: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific topic"""
        topic = self.get_topic(topic_name)
        if topic is None:
            return None
        
        with topic.lock:
            return {
                'name': topic.name,
                'subscribers': len(topic.subscribers),
                'message_count': topic.message_count,
                'history_size': len(topic.message_history),
                'created_at': topic.created_at
            }
    
    def clear_topic_history(self, topic_name: str) -> bool:
        """Clear message history for a topic"""
        topic = self.get_topic(topic_name)
        if topic is None:
            return False
        
        with topic.lock:
            topic.message_history.clear()
        return True


class Publisher:
    """Convenience class for publishing messages"""
    
    def __init__(self, service: PubSubService, default_topic: str = None):
        self.service = service
        self.default_topic = default_topic
    
    def publish(self, payload: Any, topic: str = None,
                priority: MessagePriority = MessagePriority.NORMAL,
                metadata: Dict[str, Any] = None) -> str:
        """Publish a message"""
        topic_name = topic or self.default_topic
        if topic_name is None:
            raise ValueError("Topic must be specified")
        return self.service.publish(topic_name, payload, priority, metadata)


class Subscriber:
    """Convenience class for subscribing to messages"""
    
    def __init__(self, service: PubSubService):
        self.service = service
        self.subscriptions: List[tuple] = []  # (topic, callback)
    
    def subscribe(self, topic: str, callback: Callable) -> bool:
        """Subscribe to a topic"""
        success = self.service.subscribe(topic, callback)
        if success:
            self.subscriptions.append((topic, callback))
        return success
    
    def unsubscribe_all(self):
        """Unsubscribe from all topics"""
        for topic, callback in self.subscriptions:
            self.service.unsubscribe(topic, callback)
        self.subscriptions.clear()

