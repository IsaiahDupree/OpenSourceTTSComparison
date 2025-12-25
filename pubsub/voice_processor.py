"""
Voice Processing Service using Pub/Sub
======================================
Handles audio input/output through the pub/sub messaging system.
"""

import os
import sys
import time
import threading
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pubsub.service import PubSubService, Message, MessagePriority, Publisher, Subscriber


@dataclass
class AudioRequest:
    """Request for audio processing"""
    text: str
    reference_audio_path: Optional[str] = None
    reference_audio_data: Optional[bytes] = None
    style: str = "en_default"
    metadata: Dict[str, Any] = None
    request_id: str = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.request_id is None:
            import uuid
            self.request_id = str(uuid.uuid4())


@dataclass
class AudioResponse:
    """Response from audio processing"""
    request_id: str
    audio_path: Optional[str] = None
    audio_data: Optional[bytes] = None
    success: bool = False
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class VoiceProcessor:
    """
    Voice processing service that uses pub/sub for audio input/output.
    
    Topics:
    - 'voice.request': Publish audio generation requests here
    - 'voice.response': Subscribe here to receive generated audio
    - 'voice.status': Status updates during processing
    """
    
    def __init__(self, service: Optional[PubSubService] = None, output_dir: str = "voice_clone_output"):
        self.service = service or PubSubService()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.publisher = Publisher(self.service, "voice.response")
        self.subscriber = Subscriber(self.service)
        
        # Subscribe to requests
        self.subscriber.subscribe("voice.request", self._handle_request)
        
        # Processing callbacks
        self.processors: Dict[str, Callable] = {}
        
        # Request tracking
        self.active_requests: Dict[str, AudioRequest] = {}
        self.lock = threading.Lock()
        
        # Statistics
        self.stats = {
            'requests_received': 0,
            'requests_processed': 0,
            'requests_failed': 0,
        }
    
    def register_processor(self, name: str, processor: Callable[[AudioRequest], AudioResponse]):
        """
        Register an audio processor function.
        
        Args:
            name: Processor name (e.g., 'openvoice', 'coqui')
            processor: Function that takes AudioRequest and returns AudioResponse
        """
        self.processors[name] = processor
    
    def _handle_request(self, message: Message):
        """Handle incoming audio generation request"""
        try:
            request_data = message.payload
            
            # Support both dict and AudioRequest objects
            if isinstance(request_data, dict):
                request = AudioRequest(**request_data)
            elif isinstance(request_data, AudioRequest):
                request = request_data
            else:
                raise ValueError(f"Invalid request type: {type(request_data)}")
            
            with self.lock:
                self.stats['requests_received'] += 1
                self.active_requests[request.request_id] = request
            
            # Publish status
            self._publish_status(request.request_id, "processing", "Request received, processing...")
            
            # Process the request
            response = self._process_request(request)
            
            # Publish response
            self.publisher.publish(
                response,
                topic="voice.response",
                metadata={"request_id": request.request_id, "timestamp": time.time()}
            )
            
            with self.lock:
                if request.request_id in self.active_requests:
                    del self.active_requests[request.request_id]
                if response.success:
                    self.stats['requests_processed'] += 1
                else:
                    self.stats['requests_failed'] += 1
                    
        except Exception as e:
            error_msg = f"Error processing request: {e}"
            print(f"[VoiceProcessor] {error_msg}")
            
            # Send error response
            request_id = getattr(request, 'request_id', 'unknown')
            error_response = AudioResponse(
                request_id=request_id,
                success=False,
                error=str(e)
            )
            self.publisher.publish(
                error_response,
                topic="voice.response",
                metadata={"error": True, "timestamp": time.time()}
            )
    
    def _process_request(self, request: AudioRequest) -> AudioResponse:
        """Process an audio request using registered processors"""
        # Try processors in order - prioritize OpenVoice if available
        processor_order = sorted(self.processors.keys(), key=lambda x: 0 if 'openvoice' in x.lower() else 1)
        
        for name in processor_order:
            processor = self.processors[name]
            try:
                self._publish_status(request.request_id, "processing", f"Trying processor: {name}")
                response = processor(request)
                
                # Ensure response is AudioResponse
                if not isinstance(response, AudioResponse):
                    if isinstance(response, dict):
                        response = AudioResponse(**response)
                    else:
                        raise ValueError(f"Processor {name} returned invalid response type: {type(response)}")
                
                if response.success:
                    self._publish_status(request.request_id, "completed", f"Successfully processed with {name}")
                    return response
                else:
                    # Processor tried but failed - log and continue
                    error_msg = response.error or "Unknown error"
                    print(f"[VoiceProcessor] Processor {name} failed: {error_msg}")
                    continue
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                print(f"[VoiceProcessor] Processor {name} raised exception: {e}")
                print(f"[VoiceProcessor] Traceback: {error_details}")
                continue
        
        # No processor succeeded
        return AudioResponse(
            request_id=request.request_id,
            success=False,
            error="No processor available or all processors failed"
        )
    
    def _publish_status(self, request_id: str, status: str, message: str):
        """Publish status update"""
        try:
            self.service.publish(
                "voice.status",
                {
                    "request_id": request_id,
                    "status": status,
                    "message": message,
                    "timestamp": time.time()
                },
                priority=MessagePriority.NORMAL
            )
        except Exception as e:
            # Silently fail status updates to avoid breaking main flow
            pass
    
    def request_audio(self, text: str, reference_audio_path: Optional[str] = None,
                     style: str = "en_default", metadata: Dict[str, Any] = None) -> str:
        """
        Request audio generation (convenience method)
        
        Returns:
            request_id: ID to track this request
        """
        request = AudioRequest(
            text=text,
            reference_audio_path=reference_audio_path,
            style=style,
            metadata=metadata or {}
        )
        
        # Publish request
        self.service.publish(
            "voice.request",
            request,
            priority=MessagePriority.NORMAL,
            metadata={"request_id": request.request_id}
        )
        
        return request.request_id
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        with self.lock:
            return {
                **self.stats,
                'active_requests': len(self.active_requests),
                'registered_processors': list(self.processors.keys())
            }


class OpenVoiceProcessor:
    """Processor for OpenVoice API"""
    
    def __init__(self, hf_token: Optional[str] = None):
        self.hf_token = hf_token or os.getenv("HF_TOKEN")
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize OpenVoice client"""
        try:
            import sys
            import io
            # Redirect stdout to capture encoding issues
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            
            try:
                from gradio_client import Client, handle_file
                
                # Use canonical Space ID (not replica URL - replicas are not stable)
                SPACE_ID = "myshell-ai/OpenVoiceV2"
                
                if self.hf_token:
                    self.client = Client(SPACE_ID, hf_token=self.hf_token)
                else:
                    self.client = Client(SPACE_ID)
                
                self.handle_file = handle_file
                self.space_id = SPACE_ID
                # Real runtime URL (the actual app, not the Hub page)
                space_subdomain = SPACE_ID.replace("/", "-").lower()
                self.space_app_url = f"https://{space_subdomain}.hf.space/"
                self.space_page = f"https://huggingface.co/spaces/{SPACE_ID}"  # Keep for reference
                
                # Clear any output
                sys.stdout.seek(0)
                sys.stdout.truncate(0)
            finally:
                sys.stdout = old_stdout
            
            print("[OpenVoiceProcessor] Client initialized")
        except Exception as e:
            print(f"[OpenVoiceProcessor] Failed to initialize: {e}")
            import traceback
            traceback.print_exc()
            self.client = None
    
    def __call__(self, request: AudioRequest) -> AudioResponse:
        """Process request using OpenVoice"""
        if self.client is None:
            return AudioResponse(
                request_id=request.request_id,
                success=False,
                error="OpenVoice client not initialized"
            )
        
        try:
            # Get reference audio
            if request.reference_audio_path:
                ref_path = Path(request.reference_audio_path)
                if not ref_path.exists():
                    return AudioResponse(
                        request_id=request.request_id,
                        success=False,
                        error=f"Reference audio not found: {request.reference_audio_path}"
                    )
            else:
                return AudioResponse(
                    request_id=request.request_id,
                    success=False,
                    error="Reference audio path required"
                )
            
            print(f"[OpenVoiceProcessor] Processing request {request.request_id[:8]}...")
            print(f"[OpenVoiceProcessor] Text: {request.text[:50]}...")
            print(f"[OpenVoiceProcessor] Reference: {ref_path.name}")
            
            # Validate text length (up to 200 characters per docs)
            if len(request.text) > 200:
                print(f"[OpenVoiceProcessor] Warning: Text is {len(request.text)} chars, truncating to 200")
                text_to_use = request.text[:200]
            else:
                text_to_use = request.text
            
            # IMPORTANT: Upload local file using handle_file() for gr.Audio(type="filepath")
            audio_file = self.handle_file(str(ref_path.resolve()))
            print(f"[OpenVoiceProcessor] File uploaded via handle_file")
            
            # Wake space function - ping the actual app domain, not the Hub page
            def wake_space():
                """Wake up Space by pinging the actual app domain"""
                try:
                    import requests
                    r = requests.get(self.space_app_url, timeout=15)
                    print(f"[OpenVoiceProcessor] Wake ping: {self.space_app_url} -> HTTP {r.status_code}")
                except Exception as e:
                    print(f"[OpenVoiceProcessor] Wake warning: {e}")
            
            # Call OpenVoice API with retry loop and exponential backoff
            # ValueError: None is NOT "asleep" - it's cold start/overload/crash
            # Use submit().result() with longer timeout for cold starts
            backoffs = [5, 10, 20, 30, 45, 60]  # Exponential backoff
            last_err = None
            
            for attempt, sleep_s in enumerate(backoffs, start=1):
                try:
                    print(f"[OpenVoiceProcessor] Attempt {attempt}/{len(backoffs)} (timeout=300s)...")
                    
                    # Use submit().result() instead of predict() for better timeout handling
                    # Try api_name first, fallback to fn_index
                    try:
                        job = self.client.submit(
                            text_to_use,
                            request.style,
                            audio_file,
                            True,
                            api_name="/predict"  # More stable than fn_index
                        )
                    except:
                        # Fallback to fn_index if api_name doesn't work
                        job = self.client.submit(
                            text_to_use,
                            request.style,
                            audio_file,
                            True,
                            fn_index=1
                        )
                    
                    # Wait with longer timeout for cold starts (can take 30-180s)
                    result_tuple = job.result(timeout=300)
                    print(f"[OpenVoiceProcessor] API call successful!")
                    break
                    
                except ValueError as ve:
                    # ValueError: None is NOT "asleep" - it's cold start/overload/crash
                    last_err = ve
                    error_msg = str(ve).lower()
                    if attempt < len(backoffs):
                        print(f"[OpenVoiceProcessor] Error (attempt {attempt}/{len(backoffs)}): {ve}")
                        print(f"[OpenVoiceProcessor] Waking + waiting {sleep_s}s...")
                        wake_space()
                        time.sleep(sleep_s)
                        continue
                    else:
                        raise
                except Exception as e:
                    last_err = e
                    if attempt < len(backoffs):
                        print(f"[OpenVoiceProcessor] Exception (attempt {attempt}/{len(backoffs)}): {e}")
                        print(f"[OpenVoiceProcessor] Waking + waiting {sleep_s}s...")
                        wake_space()
                        time.sleep(sleep_s)
                        continue
                    else:
                        raise
            
            if result_tuple is None:
                raise RuntimeError(f"Space call never succeeded. Last error: {last_err}")
            
            print(f"[OpenVoiceProcessor] API call completed, result type: {type(result_tuple)}")
            
            if not result_tuple:
                return AudioResponse(
                    request_id=request.request_id,
                    success=False,
                    error="OpenVoice API returned None"
                )
            
            if len(result_tuple) < 2:
                return AudioResponse(
                    request_id=request.request_id,
                    success=False,
                    error=f"OpenVoice API returned invalid result (length: {len(result_tuple)})"
                )
            
            result_path = result_tuple[1]
            print(f"[OpenVoiceProcessor] Result path: {result_path}")
            
            # Save to output directory
            output_dir = Path("voice_clone_output")
            output_dir.mkdir(exist_ok=True)
            output_file = output_dir / f"openvoice_{request.request_id}.wav"
            
            import shutil
            if Path(result_path).exists():
                shutil.move(result_path, output_file)
                print(f"[OpenVoiceProcessor] Moved file to: {output_file}")
            else:
                # If it's a URL, download it
                import urllib.request
                if result_path.startswith("http"):
                    print(f"[OpenVoiceProcessor] Downloading from URL...")
                    urllib.request.urlretrieve(result_path, output_file)
                    print(f"[OpenVoiceProcessor] Downloaded to: {output_file}")
                else:
                    return AudioResponse(
                        request_id=request.request_id,
                        success=False,
                        error=f"Result path not accessible: {result_path} (exists: {Path(result_path).exists()})"
                    )
            
            if not output_file.exists():
                return AudioResponse(
                    request_id=request.request_id,
                    success=False,
                    error=f"Output file was not created: {output_file}"
                )
            
            return AudioResponse(
                request_id=request.request_id,
                audio_path=str(output_file),
                success=True,
                metadata={"processor": "openvoice", "style": request.style}
            )
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"[OpenVoiceProcessor] Exception: {e}")
            print(f"[OpenVoiceProcessor] Traceback:\n{error_trace}")
            return AudioResponse(
                request_id=request.request_id,
                success=False,
                error=f"OpenVoice processing failed: {e}"
            )


class FileAudioProcessor:
    """Simple processor that saves requests to files (for testing)"""
    
    def __init__(self, output_dir: str = "voice_clone_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def __call__(self, request: AudioRequest) -> AudioResponse:
        """Save request info to file"""
        try:
            # Create a simple text file with request info
            info_file = self.output_dir / f"request_{request.request_id}.txt"
            with open(info_file, 'w') as f:
                f.write(f"Text: {request.text}\n")
                f.write(f"Style: {request.style}\n")
                f.write(f"Reference: {request.reference_audio_path}\n")
                f.write(f"Metadata: {request.metadata}\n")
            
            # If reference audio exists, copy it
            audio_path = None
            if request.reference_audio_path and Path(request.reference_audio_path).exists():
                import shutil
                audio_path = self.output_dir / f"audio_{request.request_id}.wav"
                shutil.copy(request.reference_audio_path, audio_path)
            
            return AudioResponse(
                request_id=request.request_id,
                audio_path=str(audio_path) if audio_path else None,
                success=True,
                metadata={"processor": "file", "info_file": str(info_file)}
            )
        except Exception as e:
            return AudioResponse(
                request_id=request.request_id,
                success=False,
                error=f"File processing failed: {e}"
            )

