#!/usr/bin/env python3
"""
Model Wrappers for TTS Comparison Study

Unified interface for all TTS models to enable consistent benchmarking.
"""

import numpy as np
import torch
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import soundfile as sf
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class TTSModelWrapper(ABC):
    """Abstract base class for TTS model wrappers."""
    
    def __init__(self, name: str, model_path: Optional[str] = None):
        self.name = name
        self.model_path = model_path
        self.model = None
        self.is_loaded = False
        
    @abstractmethod
    def load_model(self) -> bool:
        """Load the TTS model."""
        pass
    
    @abstractmethod
    def synthesize(self, text: str, **kwargs) -> np.ndarray:
        """Synthesize speech from text."""
        pass
    
    def supports_voice_cloning(self) -> bool:
        """Check if model supports voice cloning."""
        return hasattr(self, 'clone_voice')
    
    def supports_multilingual(self) -> bool:
        """Check if model supports multiple languages."""
        return hasattr(self, 'set_language')


class ChatterboxWrapper(TTSModelWrapper):
    """Wrapper for Chatterbox TTS."""
    
    def __init__(self):
        super().__init__("Chatterbox")
        
    def load_model(self) -> bool:
        """Load Chatterbox model."""
        try:
            import chatterbox
            self.model = chatterbox.TTS()
            self.is_loaded = True
            logger.info("✅ Chatterbox model loaded successfully")
            return True
        except ImportError as e:
            logger.error(f"❌ Failed to import Chatterbox: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to load Chatterbox: {e}")
            return False
    
    def synthesize(self, text: str, **kwargs) -> np.ndarray:
        """Synthesize speech using Chatterbox."""
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
        
        try:
            # Chatterbox API call (placeholder - adjust based on actual API)
            audio = self.model.synthesize(text)
            return np.array(audio, dtype=np.float32)
        except Exception as e:
            logger.error(f"❌ Chatterbox synthesis failed: {e}")
            raise
    
    def clone_voice(self, reference_audio: np.ndarray, text: str) -> np.ndarray:
        """Clone voice using Chatterbox."""
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
        
        try:
            # Voice cloning API call (placeholder)
            audio = self.model.clone_and_synthesize(reference_audio, text)
            return np.array(audio, dtype=np.float32)
        except Exception as e:
            logger.error(f"❌ Chatterbox voice cloning failed: {e}")
            raise


class OpenVoiceWrapper(TTSModelWrapper):
    """Wrapper for OpenVoice."""
    
    def __init__(self, model_path: str = "models/OpenVoice"):
        super().__init__("OpenVoice", model_path)
        
    def load_model(self) -> bool:
        """Load OpenVoice model."""
        try:
            import sys
            sys.path.append(str(Path(self.model_path)))
            
            # Import OpenVoice modules (adjust based on actual structure)
            from openvoice import se_extractor
            from openvoice.api import ToneColorConverter
            
            self.tone_converter = ToneColorConverter()
            self.is_loaded = True
            logger.info("✅ OpenVoice model loaded successfully")
            return True
        except ImportError as e:
            logger.error(f"❌ Failed to import OpenVoice: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to load OpenVoice: {e}")
            return False
    
    def synthesize(self, text: str, **kwargs) -> np.ndarray:
        """Synthesize speech using OpenVoice."""
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
        
        try:
            # OpenVoice synthesis (placeholder - adjust based on actual API)
            audio = self.tone_converter.synthesize(text)
            return np.array(audio, dtype=np.float32)
        except Exception as e:
            logger.error(f"❌ OpenVoice synthesis failed: {e}")
            raise
    
    def clone_voice(self, reference_audio: np.ndarray, text: str) -> np.ndarray:
        """Clone voice using OpenVoice."""
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
        
        try:
            # Voice cloning with cross-lingual support
            audio = self.tone_converter.convert_voice(reference_audio, text)
            return np.array(audio, dtype=np.float32)
        except Exception as e:
            logger.error(f"❌ OpenVoice voice cloning failed: {e}")
            raise


class FishSpeechWrapper(TTSModelWrapper):
    """Wrapper for Fish-Speech."""
    
    def __init__(self, model_path: str = "models/fish-speech"):
        super().__init__("Fish-Speech", model_path)
        
    def load_model(self) -> bool:
        """Load Fish-Speech model."""
        try:
            import sys
            sys.path.append(str(Path(self.model_path)))
            
            # Import Fish-Speech modules
            from fish_speech.models import FishSpeechModel
            
            self.model = FishSpeechModel.from_pretrained("fishaudio/fish-speech-1.4")
            self.is_loaded = True
            logger.info("✅ Fish-Speech model loaded successfully")
            return True
        except ImportError as e:
            logger.error(f"❌ Failed to import Fish-Speech: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to load Fish-Speech: {e}")
            return False
    
    def synthesize(self, text: str, **kwargs) -> np.ndarray:
        """Synthesize speech using Fish-Speech."""
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
        
        try:
            audio = self.model.generate(text)
            return np.array(audio, dtype=np.float32)
        except Exception as e:
            logger.error(f"❌ Fish-Speech synthesis failed: {e}")
            raise
    
    def set_language(self, language: str):
        """Set language for multilingual synthesis."""
        if hasattr(self.model, 'set_language'):
            self.model.set_language(language)


class GPTSoVITSWrapper(TTSModelWrapper):
    """Wrapper for GPT-SoVITS."""
    
    def __init__(self, model_path: str = "models/GPT-SoVITS"):
        super().__init__("GPT-SoVITS", model_path)
        
    def load_model(self) -> bool:
        """Load GPT-SoVITS model."""
        try:
            import sys
            sys.path.append(str(Path(self.model_path)))
            
            # Import GPT-SoVITS modules
            from GPT_SoVITS.inference import GPTSoVITSInference
            
            self.model = GPTSoVITSInference()
            self.is_loaded = True
            logger.info("✅ GPT-SoVITS model loaded successfully")
            return True
        except ImportError as e:
            logger.error(f"❌ Failed to import GPT-SoVITS: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to load GPT-SoVITS: {e}")
            return False
    
    def synthesize(self, text: str, **kwargs) -> np.ndarray:
        """Synthesize speech using GPT-SoVITS."""
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
        
        try:
            audio = self.model.infer(text)
            return np.array(audio, dtype=np.float32)
        except Exception as e:
            logger.error(f"❌ GPT-SoVITS synthesis failed: {e}")
            raise
    
    def clone_voice(self, reference_audio: np.ndarray, text: str) -> np.ndarray:
        """Clone voice using GPT-SoVITS."""
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
        
        try:
            audio = self.model.infer_with_reference(reference_audio, text)
            return np.array(audio, dtype=np.float32)
        except Exception as e:
            logger.error(f"❌ GPT-SoVITS voice cloning failed: {e}")
            raise


class CosyVoiceWrapper(TTSModelWrapper):
    """Wrapper for CosyVoice."""
    
    def __init__(self, model_path: str = "models/CosyVoice"):
        super().__init__("CosyVoice", model_path)
        
    def load_model(self) -> bool:
        """Load CosyVoice model."""
        try:
            import sys
            sys.path.append(str(Path(self.model_path)))
            
            # Import CosyVoice modules
            from cosyvoice.cli.cosyvoice import CosyVoice
            
            self.model = CosyVoice('pretrained_models/CosyVoice-300M')
            self.is_loaded = True
            logger.info("✅ CosyVoice model loaded successfully")
            return True
        except ImportError as e:
            logger.error(f"❌ Failed to import CosyVoice: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to load CosyVoice: {e}")
            return False
    
    def synthesize(self, text: str, **kwargs) -> np.ndarray:
        """Synthesize speech using CosyVoice."""
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
        
        try:
            audio = self.model.inference_sft(text)
            return np.array(audio, dtype=np.float32)
        except Exception as e:
            logger.error(f"❌ CosyVoice synthesis failed: {e}")
            raise
    
    def clone_voice(self, reference_audio: np.ndarray, text: str) -> np.ndarray:
        """Clone voice using CosyVoice."""
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
        
        try:
            audio = self.model.inference_zero_shot(text, reference_audio)
            return np.array(audio, dtype=np.float32)
        except Exception as e:
            logger.error(f"❌ CosyVoice voice cloning failed: {e}")
            raise


class CoquiTTSWrapper(TTSModelWrapper):
    """Wrapper for Coqui TTS."""
    
    def __init__(self):
        super().__init__("Coqui-TTS")
        
    def load_model(self) -> bool:
        """Load Coqui TTS model."""
        try:
            from TTS.api import TTS
            
            # Load XTTS-v2 model
            self.model = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
            self.is_loaded = True
            logger.info("✅ Coqui TTS model loaded successfully")
            return True
        except ImportError as e:
            logger.error(f"❌ Failed to import Coqui TTS: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to load Coqui TTS: {e}")
            return False
    
    def synthesize(self, text: str, **kwargs) -> np.ndarray:
        """Synthesize speech using Coqui TTS."""
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
        
        try:
            # Use default speaker
            audio = self.model.tts(text=text)
            return np.array(audio, dtype=np.float32)
        except Exception as e:
            logger.error(f"❌ Coqui TTS synthesis failed: {e}")
            raise
    
    def clone_voice(self, reference_audio: np.ndarray, text: str) -> np.ndarray:
        """Clone voice using Coqui TTS."""
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
        
        try:
            # Save reference audio temporarily
            temp_ref_path = "temp_reference.wav"
            sf.write(temp_ref_path, reference_audio, 22050)
            
            # Clone voice
            audio = self.model.tts(text=text, speaker_wav=temp_ref_path)
            
            # Clean up
            Path(temp_ref_path).unlink(missing_ok=True)
            
            return np.array(audio, dtype=np.float32)
        except Exception as e:
            logger.error(f"❌ Coqui TTS voice cloning failed: {e}")
            raise
    
    def set_language(self, language: str):
        """Set language for multilingual synthesis."""
        self.current_language = language


class ModelFactory:
    """Factory for creating model wrappers."""
    
    @staticmethod
    def create_wrapper(model_name: str, **kwargs) -> TTSModelWrapper:
        """Create appropriate model wrapper."""
        wrappers = {
            "chatterbox": ChatterboxWrapper,
            "openvoice": OpenVoiceWrapper,
            "fish-speech": FishSpeechWrapper,
            "gpt-sovits": GPTSoVITSWrapper,
            "cosyvoice": CosyVoiceWrapper,
            "coqui-tts": CoquiTTSWrapper
        }
        
        if model_name.lower() not in wrappers:
            raise ValueError(f"Unknown model: {model_name}")
        
        wrapper_class = wrappers[model_name.lower()]
        return wrapper_class(**kwargs)
    
    @staticmethod
    def get_available_models() -> list:
        """Get list of available models."""
        return ["chatterbox", "openvoice", "fish-speech", "gpt-sovits", "cosyvoice", "coqui-tts"]
