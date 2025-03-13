import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(config=None, log_level=None, log_file=None):
    """
    Configure logging for the application.
    
    Args:
        config: Configuration dictionary
        log_level: Optional override for log level
        log_file: Optional override for log file path
    """
    if config is None:
        config = {}
    
    # Get logging configuration
    logging_config = config.get('logging', {})
    
    # Set log level (priority: function parameter > config > default)
    level_str = log_level or logging_config.get('level', 'INFO')
    level = getattr(logging, level_str.upper())
    
    # Set log file path (priority: function parameter > config > default)
    log_path = log_file or logging_config.get('path', 'logs/app.log')
    
    # Ensure log directory exists
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Clear existing handlers to avoid duplicates
    if logger.handlers:
        logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # Create file handler (rotating file handler to manage log size)
    file_handler = RotatingFileHandler(
        log_path, 
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(level)
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    # Log initial message
    logging.info("Logging initialized at level %s", level_str.upper())
    
    return logger 