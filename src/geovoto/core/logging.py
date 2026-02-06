import logging
import sys
from typing import Optional

from geovoto.config.settings import settings


def setup_logging(name: Optional[str] = None) -> logging.Logger:
    """
    Configures and returns a logger instance.
    
    Args:
        name: The name of the logger (usually __name__).
    
    Returns:
        A configured logging.Logger instance.
    """
    logger = logging.getLogger(name or "geovoto")
    
    # Check if already configured to avoid duplicate handlers
    if logger.handlers:
        return logger
        
    log_level = logging.DEBUG if settings.is_debug() else logging.INFO
    logger.setLevel(log_level)
    
    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    
    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger
