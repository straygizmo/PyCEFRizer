"""Logging configuration for PyCEFRizer."""

import logging
import sys
from typing import Optional


def setup_logger(
    name: str = "pycefrizer",
    level: int = logging.INFO,
    format_string: Optional[str] = None
) -> logging.Logger:
    """Set up and return a logger instance.
    
    Args:
        name: Logger name
        level: Logging level
        format_string: Custom format string for log messages
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)
    
    # Set format
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    formatter = logging.Formatter(format_string)
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    logger.propagate = False
    
    return logger


# Create default logger
logger = setup_logger()