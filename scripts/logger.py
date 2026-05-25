"""
logger.py - ETL Logger Utility
Sets up file + console logging for the ETL pipeline.
"""

import logging
import os
from datetime import datetime


def setup_logger(log_dir: str = "logs", log_level: str = "INFO") -> logging.Logger:
    """
    Set up a logger that writes to both console and a daily log file.

    Args:
        log_dir:   Folder where log files are saved.
        log_level: Logging level string (DEBUG, INFO, WARNING, ERROR).

    Returns:
        Configured Logger instance.
    """
    # Create logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)

    # Log file named by date, e.g. logs/etl_2024-01-15.log
    log_filename = os.path.join(log_dir, f"etl_{datetime.now().strftime('%Y-%m-%d')}.log")

    # Map string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create logger
    logger = logging.getLogger("etl_pipeline")
    logger.setLevel(numeric_level)

    # Avoid adding duplicate handlers on repeated imports
    if logger.handlers:
        return logger

    # --- File Handler ---
    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setLevel(numeric_level)

    # --- Console Handler ---
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)

    # Shared formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(funcName)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info(f"Logger initialised. Log file → {log_filename}")
    return logger
