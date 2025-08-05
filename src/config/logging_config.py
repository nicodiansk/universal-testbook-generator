"""
Logging configuration for the Universal Testbook Generator.
"""

import sys
from loguru import logger
from .settings import settings

def setup_logging():
    """Configure logging with loguru."""
    # Remove default handler
    logger.remove()
    
    # Add custom handler with formatted output
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True
    )
    
    # Add file handler for errors
    logger.add(
        "logs/error.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="1 week",
        retention="1 month"
    )
    
    return logger

# Initialize logging
setup_logging()