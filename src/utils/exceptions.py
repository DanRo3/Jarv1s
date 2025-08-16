"""
Custom exceptions for Jarv1s services.
Provides structured error handling across the application.
"""


class JarvisBaseException(Exception):
    """Base exception for all Jarv1s-related errors."""
    
    def __init__(self, message: str, service: str = "unknown", details: str = None):
        self.message = message
        self.service = service
        self.details = details
        super().__init__(self.message)
    
    def __str__(self):
        base = f"[{self.service.upper()}] {self.message}"
        if self.details:
            base += f" - Details: {self.details}"
        return base


class STTException(JarvisBaseException):
    """Exception raised by Speech-to-Text service."""
    
    def __init__(self, message: str, details: str = None):
        super().__init__(message, "STT", details)


class LLMException(JarvisBaseException):
    """Exception raised by LLM service."""
    
    def __init__(self, message: str, details: str = None):
        super().__init__(message, "LLM", details)


class TTSException(JarvisBaseException):
    """Exception raised by Text-to-Speech service."""
    
    def __init__(self, message: str, details: str = None):
        super().__init__(message, "TTS", details)


class ConfigurationException(JarvisBaseException):
    """Exception raised for configuration-related errors."""
    
    def __init__(self, message: str, details: str = None):
        super().__init__(message, "CONFIG", details)


class ModelLoadException(JarvisBaseException):
    """Exception raised when AI models fail to load."""
    
    def __init__(self, message: str, model_type: str, details: str = None):
        super().__init__(f"Failed to load {model_type} model: {message}", model_type.upper(), details)


class AudioProcessingException(JarvisBaseException):
    """Exception raised during audio processing."""
    
    def __init__(self, message: str, details: str = None):
        super().__init__(message, "AUDIO", details)