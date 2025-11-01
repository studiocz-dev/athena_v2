"""
Custom logging configuration with colors
"""
import logging
import colorlog
import os
from config import LOG_LEVEL, LOG_FORMAT, LOG_FILE

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Create color formatter
color_formatter = colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
)

# Create file formatter
file_formatter = logging.Formatter(LOG_FORMAT, datefmt='%Y-%m-%d %H:%M:%S')

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(color_formatter)

# Create file handler
file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
file_handler.setFormatter(file_formatter)

def get_logger(name):
    """Get a configured logger instance"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# Create main logger
log = get_logger('AthenaBot')
