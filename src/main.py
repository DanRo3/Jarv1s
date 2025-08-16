"""
Main entry point for Jarv1s backend server.
Handles server startup with proper configuration and logging.
"""

import uvicorn
from dotenv import load_dotenv

from .config.settings import get_settings
from .utils.logger import get_main_logger
from .api.server import app


def setup_environment() -> None:
    """Setup environment variables and configuration."""
    # Load environment variables before importing other modules
    load_dotenv()


def main() -> None:
    """Main entry point for the application."""
    # Setup environment first
    setup_environment()
    
    # Get settings and logger
    settings = get_settings()
    logger = get_main_logger()
    
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Server configuration: {settings.server.host}:{settings.server.port}")
    logger.info(f"Debug mode: {settings.server.debug}")
    
    # Start the server
    uvicorn.run(
        "src.main:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=settings.server.reload,
        log_level=settings.logging.level.lower(),
        access_log=settings.server.debug
    )


if __name__ == "__main__":
    main()