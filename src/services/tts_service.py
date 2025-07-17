"""
Text-to-Speech service using Piper TTS.
Handles voice synthesis with robust error handling and configuration management.
"""

import io
import wave
from typing import Tuple, Optional

from piper.voice import PiperVoice

from ..config.settings import get_settings
from ..utils.logger import get_tts_logger
from ..utils.exceptions import TTSException, ModelLoadException


class TTSService:
    """Text-to-Speech service using Piper TTS."""
    
    def __init__(self):
        self.settings = get_settings().tts
        self.logger = get_tts_logger()
        self.model: Optional[PiperVoice] = None
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the Piper TTS model with configured settings."""
        self.logger.info(f"Loading Piper TTS model from {self.settings.model_path}")
        
        try:
            self.model = PiperVoice.load(
                self.settings.model_path,
                config_path=self.settings.config_path
            )
            self.logger.info("Piper TTS model loaded successfully")
            
        except Exception as e:
            error_msg = f"Failed to load Piper TTS model: {str(e)}"
            self.logger.error(error_msg)
            raise ModelLoadException(error_msg, "Piper TTS", str(e))
    
    def _generate_raw_audio(self, text: str) -> bytes:
        """Generate raw PCM audio data from text."""
        if not self.model:
            raise TTSException("Piper TTS model is not available")
        
        try:
            self.logger.debug(f"Generating raw audio for text: '{text}'")
            
            audio_raw_bytes = b''
            for audio_bytes in self.model.synthesize_stream_raw(text):
                audio_raw_bytes += audio_bytes
            
            self.logger.debug(f"Generated {len(audio_raw_bytes)} bytes of raw audio")
            return audio_raw_bytes
            
        except Exception as e:
            error_msg = f"Failed to generate raw audio: {str(e)}"
            self.logger.error(error_msg)
            raise TTSException(error_msg, str(e))
    
    def _create_wav_file(self, raw_audio: bytes, sample_rate: int) -> bytes:
        """Create a complete WAV file from raw PCM audio data."""
        try:
            self.logger.debug("Creating WAV file in memory")
            
            wav_buffer = io.BytesIO()
            
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit audio (2 bytes per sample)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(raw_audio)
            
            wav_bytes = wav_buffer.getvalue()
            self.logger.debug(f"Created WAV file: {len(wav_bytes)} bytes")
            
            return wav_bytes
            
        except Exception as e:
            error_msg = f"Failed to create WAV file: {str(e)}"
            self.logger.error(error_msg)
            raise TTSException(error_msg, str(e))
    
    def synthesize_audio(self, text: str) -> Tuple[bytes, int]:
        """
        Synthesize text to audio and return WAV file bytes.
        
        Args:
            text: Text to synthesize
            
        Returns:
            Tuple of (wav_bytes, sample_rate)
            
        Raises:
            TTSException: If synthesis fails
        """
        if not text.strip():
            raise TTSException("Empty text provided for synthesis")
        
        if not self.model:
            raise TTSException("Piper TTS model is not available")
        
        self.logger.info(f"Synthesizing text: '{text}'")
        
        try:
            # Get sample rate from model config
            sample_rate = self.model.config.sample_rate
            
            # Generate raw PCM audio
            raw_audio = self._generate_raw_audio(text)
            
            # Create complete WAV file
            wav_bytes = self._create_wav_file(raw_audio, sample_rate)
            
            self.logger.info(f"Audio synthesis completed: {len(wav_bytes)} bytes at {sample_rate}Hz")
            return wav_bytes, sample_rate
            
        except TTSException:
            raise
        except Exception as e:
            error_msg = f"Unexpected error during synthesis: {str(e)}"
            self.logger.error(error_msg)
            raise TTSException(error_msg, str(e))
    
    def is_available(self) -> bool:
        """Check if the TTS service is available."""
        return self.model is not None
    
    def get_sample_rate(self) -> int:
        """Get the sample rate of the loaded model."""
        if not self.model:
            raise TTSException("Piper TTS model is not available")
        return self.model.config.sample_rate
    
    def reload_model(self) -> None:
        """Reload the Piper TTS model (useful for configuration changes)."""
        self.logger.info("Reloading Piper TTS model")
        self.model = None
        self._load_model()


# Global service instance
_tts_service: Optional[TTSService] = None


def get_tts_service() -> TTSService:
    """Get the global TTS service instance."""
    global _tts_service
    if _tts_service is None:
        _tts_service = TTSService()
    return _tts_service


def synthesize_audio(text: str) -> Tuple[bytes, int]:
    """
    Convenience function for audio synthesis.
    Maintains backward compatibility with existing code.
    """
    service = get_tts_service()
    return service.synthesize_audio(text)