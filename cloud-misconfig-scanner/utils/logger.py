import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(log_level="INFO", log_file="logs/cloud_scanner.log", max_bytes=1_000_000, backup_count=2):
    logger = logging.getLogger("cloud_scanner")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Ensure log directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch_formatter = logging.Formatter('[%(levelname)s] %(message)s')
    ch.setFormatter(ch_formatter)

    # File handler with rotation
    fh = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
    fh.setLevel(logging.DEBUG)
    fh_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s - %(message)s')
    fh.setFormatter(fh_formatter)

    # Avoid duplicate handlers
    if not logger.handlers:
        logger.addHandler(ch)
        logger.addHandler(fh)

    return logger
