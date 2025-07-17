"""
Centralized configuration management for Jarv1s.
All environment variables and settings are managed here.
"""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class LLMSettings(BaseSettings):
    """LLM service configuration."""
    
    provider: str = Field(default="openai/lmstudio-local-model", env="LLM_PROVIDER")
    api_base: str = Field(default="http://localhost:1234/v1", env="LLM_API_BASE")
    api_key: str = Field(default="not-required", env="LLM_API_KEY")
    model_name: str = Field(default="openai/lmstudio-local-model", env="LLM_MODEL_NAME")
    temperature: float = Field(default=0.7, env="LLM_TEMPERATURE")
    max_history_pairs: int = Field(default=5, env="LLM_MAX_HISTORY_PAIRS")
    
    class Config:
        env_prefix = "LLM_"


class STTSettings(BaseSettings):
    """Speech-to-Text service configuration."""
    
    model_size: str = Field(default="small", env="WHISPERX_MODEL_SIZE")
    device: str = Field(default="cpu", env="STT_DEVICE")
    compute_type: str = Field(default="int8", env="STT_COMPUTE_TYPE")
    language: str = Field(default="es", env="STT_LANGUAGE")
    batch_size: int = Field(default=4, env="STT_BATCH_SIZE")
    
    class Config:
        env_prefix = "STT_"


class TTSSettings(BaseSettings):
    """Text-to-Speech service configuration."""
    
    model_path: str = Field(
        default="models/tts/es_ES-sharvard-medium.onnx", 
        env="TTS_MODEL_PATH"
    )
    config_path: str = Field(
        default="models/tts/es_ES-sharvard-medium.onnx.json", 
        env="TTS_CONFIG_PATH"
    )
    sample_rate: int = Field(default=22050, env="TTS_SAMPLE_RATE")
    
    class Config:
        env_prefix = "TTS_"


class ServerSettings(BaseSettings):
    """Server configuration."""
    
    host: str = Field(default="127.0.0.1", env="HOST")
    port: int = Field(default=8000, env="PORT")
    debug: bool = Field(default=True, env="DEBUG")
    reload: bool = Field(default=True, env="RELOAD")
    cors_origins: list[str] = Field(
        default=["http://localhost:5173", "http://127.0.0.1:5173"],
        env="CORS_ORIGINS"
    )
    
    class Config:
        env_prefix = "SERVER_"


class AudioSettings(BaseSettings):
    """Audio processing configuration."""
    
    sample_rate: int = Field(default=16000, env="AUDIO_SAMPLE_RATE")
    channels: int = Field(default=1, env="AUDIO_CHANNELS")
    chunk_size: int = Field(default=1024, env="AUDIO_CHUNK_SIZE")
    
    class Config:
        env_prefix = "AUDIO_"


class LoggingSettings(BaseSettings):
    """Logging configuration."""
    
    level: str = Field(default="INFO", env="LOG_LEVEL")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    
    class Config:
        env_prefix = "LOG_"


class Settings(BaseSettings):
    """Main application settings."""
    
    # Application info
    app_name: str = "Jarv1s"
    app_version: str = "0.2.0"
    app_description: str = "Personal AI Copilot - 100% Local"
    
    # Service configurations
    llm: LLMSettings = LLMSettings()
    stt: STTSettings = STTSettings()
    tts: TTSSettings = TTSSettings()
    server: ServerSettings = ServerSettings()
    audio: AudioSettings = AudioSettings()
    logging: LoggingSettings = LoggingSettings()
    
    # Fallback messages
    fallback_no_transcription: str = "Sorry, I didn't hear you clearly. Could you repeat that?"
    fallback_internal_error: str = "I'm sorry, I'm having a technical issue. Please try again in a moment."
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings


def reload_settings() -> Settings:
    """Reload settings from environment variables."""
    global settings
    settings = Settings()
    return settings