import logging
import sys
from vira.config import settings

def get_logger(name):
    """Configure and return a logger for the given name."""
    logger = logging.getLogger(name)
    
    # Set log level from settings
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(level)
    
    # Create console handler if not already set up
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger