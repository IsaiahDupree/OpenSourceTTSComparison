"""
Tests for Voice Processing Service
"""

import unittest
import time
import tempfile
import shutil
from pathlib import Path

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pubsub.service import PubSubService
from pubsub.voice_processor import (
    VoiceProcessor,
    AudioRequest,
    AudioResponse,
    FileAudioProcessor
)


class TestVoiceProcessor(unittest.TestCase):
    """Test cases for VoiceProcessor"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.service = PubSubService()
        self.service.start()
        
        # Create temp output directory
        self.temp_dir = tempfile.mkdtemp()
        self.processor = VoiceProcessor(service=self.service, output_dir=self.temp_dir)
        
        # Register file processor for testing
        file_proc = FileAudioProcessor(output_dir=self.temp_dir)
        self.processor.register_processor("file", file_proc)
        
        self.responses = []
        
        def response_handler(message):
            self.responses.append(message.payload)
        
        # Subscribe to responses
        from pubsub.service import Subscriber
        self.subscriber = Subscriber(self.service)
        self.subscriber.subscribe("voice.response", response_handler)
    
    def tearDown(self):
        """Clean up after tests"""
        self.subscriber.unsubscribe_all()
        self.service.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.responses.clear()
    
    def test_register_processor(self):
        """Test processor registration"""
        def test_processor(request):
            return AudioResponse(request_id=request.request_id, success=True)
        
        self.processor.register_processor("test", test_processor)
        self.assertIn("test", self.processor.processors)
    
    def test_request_audio(self):
        """Test requesting audio generation"""
        request_id = self.processor.request_audio(
            text="Test message",
            reference_audio_path="test.wav"
        )
        
        self.assertIsNotNone(request_id)
        
        # Wait for processing
        time.sleep(0.5)
        
        # Should have received a response
        self.assertGreater(len(self.responses), 0)
    
    def test_audio_request_creation(self):
        """Test AudioRequest creation"""
        request = AudioRequest(
            text="Test",
            reference_audio_path="test.wav",
            style="en_default"
        )
        
        self.assertEqual(request.text, "Test")
        self.assertEqual(request.reference_audio_path, "test.wav")
        self.assertEqual(request.style, "en_default")
        self.assertIsNotNone(request.request_id)
        self.assertIsNotNone(request.metadata)
    
    def test_audio_response_creation(self):
        """Test AudioResponse creation"""
        response = AudioResponse(
            request_id="test-123",
            audio_path="output.wav",
            success=True
        )
        
        self.assertEqual(response.request_id, "test-123")
        self.assertEqual(response.audio_path, "output.wav")
        self.assertTrue(response.success)
        self.assertIsNone(response.error)
    
    def test_file_processor(self):
        """Test FileAudioProcessor"""
        processor = FileAudioProcessor(output_dir=self.temp_dir)
        
        # Create a dummy reference file
        ref_file = Path(self.temp_dir) / "reference.wav"
        ref_file.write_text("dummy audio data")
        
        request = AudioRequest(
            text="Test message",
            reference_audio_path=str(ref_file),
            style="en_default"
        )
        
        response = processor(request)
        
        self.assertTrue(response.success)
        self.assertEqual(response.request_id, request.request_id)
        self.assertIsNotNone(response.audio_path)
        
        # Check that files were created
        info_file = Path(self.temp_dir) / f"request_{request.request_id}.txt"
        self.assertTrue(info_file.exists())
    
    def test_file_processor_no_reference(self):
        """Test FileAudioProcessor without reference audio"""
        processor = FileAudioProcessor(output_dir=self.temp_dir)
        
        request = AudioRequest(
            text="Test message",
            style="en_default"
        )
        
        response = processor(request)
        
        # Should still succeed, just no audio file
        self.assertTrue(response.success)
        self.assertIsNone(response.audio_path)
    
    def test_processor_stats(self):
        """Test processor statistics"""
        stats = self.processor.get_stats()
        
        self.assertIn('requests_received', stats)
        self.assertIn('requests_processed', stats)
        self.assertIn('requests_failed', stats)
        self.assertIn('active_requests', stats)
        self.assertIn('registered_processors', stats)
        
        # Make a request
        self.processor.request_audio(
            text="Test",
            reference_audio_path="test.wav"
        )
        
        time.sleep(0.5)
        
        stats = self.processor.get_stats()
        self.assertGreaterEqual(stats['requests_received'], 1)
    
    def test_multiple_requests(self):
        """Test multiple concurrent requests"""
        request_ids = []
        
        for i in range(3):
            req_id = self.processor.request_audio(
                text=f"Message {i}",
                reference_audio_path="test.wav"
            )
            request_ids.append(req_id)
        
        # Wait for processing
        time.sleep(1.0)
        
        # Should have received responses
        self.assertGreaterEqual(len(self.responses), 3)
    
    def test_error_handling(self):
        """Test error handling in processor"""
        # Create a dummy reference file for file processor
        ref_file = Path(self.temp_dir) / "test_ref.wav"
        ref_file.write_text("dummy")
        
        # Register a processor that fails first
        def failing_processor(request):
            raise ValueError("Test error")
        
        # Register failing processor first, then file processor (which should succeed)
        self.processor.register_processor("failing", failing_processor)
        
        # Make request with valid reference file
        self.processor.request_audio(
            text="Test",
            reference_audio_path=str(ref_file)
        )
        
        # Wait longer for processing
        time.sleep(1.0)
        
        # Should have received a response
        self.assertGreater(len(self.responses), 0, "No response received")
        
        # Check if we got a response (file processor should succeed as fallback)
        found_success = False
        for resp in self.responses:
            # Handle both dict and AudioResponse objects
            if isinstance(resp, dict):
                if resp.get('success'):
                    found_success = True
                    break
            elif hasattr(resp, 'success') and resp.success:
                found_success = True
                break
        
        # File processor should have succeeded as fallback
        self.assertTrue(found_success, "File processor should have succeeded as fallback")


class TestAudioRequestResponse(unittest.TestCase):
    """Test AudioRequest and AudioResponse classes"""
    
    def test_audio_request_defaults(self):
        """Test AudioRequest with defaults"""
        request = AudioRequest(text="Test")
        
        self.assertEqual(request.text, "Test")
        self.assertIsNone(request.reference_audio_path)
        self.assertEqual(request.style, "en_default")
        self.assertIsNotNone(request.request_id)
        self.assertIsNotNone(request.metadata)
    
    def test_audio_response_error(self):
        """Test AudioResponse with error"""
        response = AudioResponse(
            request_id="test-123",
            success=False,
            error="Test error"
        )
        
        self.assertFalse(response.success)
        self.assertEqual(response.error, "Test error")
        self.assertIsNone(response.audio_path)


if __name__ == '__main__':
    unittest.main()

