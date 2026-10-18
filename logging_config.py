#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Standard Logging Configuration for All Scripts

Use this in all scripts for consistent console logging:
    from logging_config import setup_logging
    logger = setup_logging(__name__)
"""

import sys
import io
import logging
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def setup_logging(
    name: str,
    log_file: str = None,
    level: int = logging.INFO,
    console_format: str = '%(asctime)s [%(levelname)s] %(message)s',
    file_format: str = '%(asctime)s [%(levelname)s] %(name)s - %(message)s',
    date_format: str = '%H:%M:%S'
) -> logging.Logger:
    """
    Set up comprehensive logging with both console and file output.
    
    Args:
        name: Logger name (usually __name__)
        log_file: Optional log file path (default: {script_name}.log)
        level: Logging level (default: INFO)
        console_format: Format for console output
        file_format: Format for file output
        date_format: Date format string
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Clear existing handlers
    logger.handlers.clear()
    logger.setLevel(level)
    
    # Prevent duplicate logs from root logger
    logger.propagate = False
    
    # Console handler with real-time output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(console_format, datefmt=date_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler for persistent logs
    if log_file is None:
        # Auto-generate log filename from script name
        script_name = Path(sys.argv[0]).stem if sys.argv else "script"
        log_file = f"{script_name}.log"
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)  # File gets more detail
    file_formatter = logging.Formatter(
        file_format,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Log startup message
    logger.info("=" * 70)
    logger.info(f"Logging initialized for: {name}")
    logger.info(f"Console output: Enabled")
    logger.info(f"File logging: {log_file}")
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    
    return logger


def log_section(logger: logging.Logger, title: str, char: str = "="):
    """Log a section header."""
    logger.info("")
    logger.info(char * 70)
    logger.info(title)
    logger.info(char * 70)


def log_progress(logger: logging.Logger, current: int, total: int, item: str = ""):
    """Log progress indicator."""
    percent = (current / total * 100) if total > 0 else 0
    logger.info(f"[{current}/{total}] ({percent:.1f}%) {item}")


def log_success(logger: logging.Logger, message: str):
    """Log success message."""
    logger.info(f"✅ {message}")


def log_error(logger: logging.Logger, message: str):
    """Log error message."""
    logger.error(f"❌ {message}")


def log_warning(logger: logging.Logger, message: str):
    """Log warning message."""
    logger.warning(f"⚠️  {message}")


def log_info(logger: logging.Logger, message: str):
    """Log info message."""
    logger.info(f"ℹ️  {message}")

