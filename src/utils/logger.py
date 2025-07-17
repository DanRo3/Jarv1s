"""
Centralized logging configuration for Jarv1s.
Provides structured logging with consistent formatting across all services.
"""

import logging
import sys
from typing import Optional
from pathlib import Path

from ..config.settings import get_settings


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        # Add color to levelname
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
        
        return super().format(record)


def setup_logging(
    name: Optional[str] = None,
    level: Optional[str] = None,
    log_file: Optional[Path] = None
) -> logging.Logger:
    """
    Setup logging for a service or module.
    
    Args:
        name: Logger name (defaults to calling module)
        level: Log level (defaults to settings)
        log_file: Optional file to write logs to
        
    Returns:
        Configured logger instance
    """
    settings = get_settings()
    
    # Use provided name or derive from caller
    if name is None:
        import inspect
        frame = inspect.currentframe().f_back
        name = frame.f_globals.get('__name__', 'jarv1s')
    
    # Get or create logger
    logger = logging.getLogger(name)
    
    # Set level
    log_level = level or settings.logging.level
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = ColoredFormatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific service/module."""
    return setup_logging(name)


# Service-specific loggers
def get_stt_logger() -> logging.Logger:
    """Get logger for STT service."""
    return get_logger('jarv1s.stt')


def get_llm_logger() -> logging.Logger:
    """Get logger for LLM service."""
    return get_logger('jarv1s.llm')


def get_tts_logger() -> logging.Logger:
    """Get logger for TTS service."""
    return get_logger('jarv1s.tts')


def get_api_logger() -> logging.Logger:
    """Get logger for API service."""
    return get_logger('jarv1s.api')


def get_main_logger() -> logging.Logger:
    """Get logger for main application."""
    return get_logger('jarv1s.main')