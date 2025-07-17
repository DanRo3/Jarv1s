"""
Speech-to-Text service using WhisperX.
Handles audio transcription with robust error handling and configuration management.
"""

import subprocess
from tempfile import NamedTemporaryFile
from typing import Optional

import whisperx

from ..config.settings import get_settings
from ..utils.logger import get_stt_logger
from ..utils.exceptions import STTException, ModelLoadException, AudioProcessingException


class STTService:
    """Speech-to-Text service using WhisperX."""
    
    def __init__(self):
        self.settings = get_settings().stt
        self.logger = get_stt_logger()
        self.model: Optional[whisperx.Model] = None
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the WhisperX model with configured settings."""
        self.logger.info(
            f"Loading WhisperX model '{self.settings.model_size}' "
            f"on {self.settings.device.upper()} with compute type '{self.settings.compute_type}'"
        )
        
        try:
            self.model = whisperx.load_model(
                self.settings.model_size,
                device=self.settings.device,
                compute_type=self.settings.compute_type,
                language=self.settings.language
            )
            self.logger.info("WhisperX model loaded successfully")
            
        except Exception as e:
            error_msg = f"Failed to load WhisperX model: {str(e)}"
            self.logger.error(error_msg)
            raise ModelLoadException(error_msg, "WhisperX", str(e))
    
    def _convert_audio_to_wav(self, audio_bytes: bytes) -> str:
        """Convert audio bytes to WAV format using FFmpeg."""
        try:
            with NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav_file:
                wav_filename = temp_wav_file.name
                
                ffmpeg_command = [
                    "ffmpeg", "-i", "pipe:0", 
                    "-ac", str(self.settings.batch_size), 
                    "-ar", "16000", 
                    "-f", "wav", 
                    "-y", wav_filename
                ]
                
                process = subprocess.Popen(
                    ffmpeg_command,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                stdout, stderr = process.communicate(input=audio_bytes)
                
                if process.returncode != 0:
                    error_msg = f"FFmpeg conversion failed: {stderr.decode()}"
                    self.logger.error(error_msg)
                    raise AudioProcessingException("Audio conversion failed", error_msg)
                
                return wav_filename
                
        except Exception as e:
            if isinstance(e, AudioProcessingException):
                raise
            raise AudioProcessingException("Failed to convert audio to WAV", str(e))
    
    def transcribe_audio(self, audio_bytes: bytes) -> str:
        """
        Transcribe audio bytes to text using WhisperX.
        
        Args:
            audio_bytes: Raw audio data in bytes
            
        Returns:
            Transcribed text string
            
        Raises:
            STTException: If transcription fails
        """
        if not self.model:
            raise STTException("WhisperX model is not available")
        
        try:
            self.logger.debug("Starting audio transcription")
            
            # Convert audio to WAV format
            wav_filename = self._convert_audio_to_wav(audio_bytes)
            
            try:
                # Load audio with WhisperX utility
                audio = whisperx.load_audio(wav_filename)
                
                # Transcribe with the loaded model
                self.logger.debug("Transcribing with WhisperX")
                result = self.model.transcribe(audio, batch_size=self.settings.batch_size)
                
                # Join segments to get complete transcription
                transcribed_text = " ".join([
                    segment['text'].strip() 
                    for segment in result.get("segments", [])
                ])
                
                self.logger.info(f"Transcription completed: '{transcribed_text}'")
                return transcribed_text
                
            finally:
                # Clean up temporary file
                import os
                try:
                    os.unlink(wav_filename)
                except OSError:
                    pass
                    
        except Exception as e:
            if isinstance(e, (STTException, AudioProcessingException)):
                raise
            
            error_msg = f"Transcription failed: {str(e)}"
            self.logger.error(error_msg)
            raise STTException(error_msg, str(e))
    
    def is_available(self) -> bool:
        """Check if the STT service is available."""
        return self.model is not None
    
    def reload_model(self) -> None:
        """Reload the WhisperX model (useful for configuration changes)."""
        self.logger.info("Reloading WhisperX model")
        self.model = None
        self._load_model()


# Global service instance
_stt_service: Optional[STTService] = None


def get_stt_service() -> STTService:
    """Get the global STT service instance."""
    global _stt_service
    if _stt_service is None:
        _stt_service = STTService()
    return _stt_service


def transcribe_audio(audio_bytes: bytes) -> str:
    """
    Convenience function for audio transcription.
    Maintains backward compatibility with existing code.
    """
    service = get_stt_service()
    return service.transcribe_audio(audio_bytes)