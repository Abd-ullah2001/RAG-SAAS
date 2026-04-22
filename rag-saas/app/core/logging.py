import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

def setup_logging():
    """ Setup standard logging for the application """
    
    # Define log format - timestamp, level, name/module, message
    log_format = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    # Standard Output handler for console visibility
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)

    # Rotating File handler for persistence (max 10MB per file, keep 5 backups)
    file_handler = RotatingFileHandler(
        LOGS_DIR / "app.log", maxBytes=10*1024*1024, backupCount=5
    )
    file_handler.setFormatter(log_format)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Set external libraries log levels to be less noisy
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.ERROR)

    return root_logger

# Initialize on import
logger = setup_logging()
