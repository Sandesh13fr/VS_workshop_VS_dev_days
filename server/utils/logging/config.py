"""
Logging configuration for the Flask Dog Shelter application.

This module provides utilities to configure logging with different levels,
formats, and output destinations.
"""

import os
import sys
import json
import logging
import logging.config
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import threading
from typing import Dict, Any, Optional, Union
from datetime import datetime

# Default configuration
DEFAULT_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s.%(msecs)03d [%(levelname)s] [%(thread)d] [%(name)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "simple": {
            "format": "%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "standard",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "standard",
            "filename": "logs/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 10,
            "encoding": "utf8"
        }
    },
    "loggers": {
        "": {  # Root logger
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True
        },
        "dogshelter": {  # Application logger
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False
        },
        "dogshelter.api": {  # API module logger
            "level": "INFO",
            "propagate": True
        },
        "dogshelter.models": {  # Models module logger
            "level": "INFO",
            "propagate": True
        }
    }
}

def load_config_from_file(config_file: str) -> Dict[str, Any]:
    """
    Load logging configuration from a JSON file.
    
    Args:
        config_file: Path to the JSON configuration file
        
    Returns:
        Dictionary containing logging configuration
    """
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"Error loading logging config from file: {e}", file=sys.stderr)
        return DEFAULT_CONFIG

def ensure_log_directory(log_path: str) -> None:
    """
    Ensure that the directory for log files exists.
    
    Args:
        log_path: Path to the log file
    """
    log_dir = os.path.dirname(log_path)
    if log_dir and not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
        except Exception as e:
            print(f"Error creating log directory: {e}", file=sys.stderr)

def configure_logging(
    config_file: Optional[str] = None, 
    log_level: Optional[str] = None,
    log_file: Optional[str] = None
) -> None:
    """
    Configure the logging system for the application.
    
    Args:
        config_file: Path to a JSON configuration file
        log_level: Override the default log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Override the default log file path
    """
    # Load configuration
    if config_file and os.path.exists(config_file):
        config = load_config_from_file(config_file)
    else:
        config = DEFAULT_CONFIG.copy()
    
    # Override log level if provided
    if log_level:
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if log_level.upper() in valid_levels:
            # Update root logger and application logger
            config["loggers"][""]["level"] = log_level.upper()
            config["loggers"]["dogshelter"]["level"] = log_level.upper()
    
    # Override log file if provided
    if log_file:
        if "file" in config["handlers"]:
            config["handlers"]["file"]["filename"] = log_file
            ensure_log_directory(log_file)
    else:
        # Ensure the default log directory exists
        if "file" in config["handlers"]:
            ensure_log_directory(config["handlers"]["file"]["filename"])
    
    # Apply configuration
    logging.config.dictConfig(config)
    
    # Log startup information
    logger = logging.getLogger("dogshelter")
    logger.info("Logging system initialized")
    logger.debug(f"Log configuration: {config}")

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Guidelines for log levels:
    - DEBUG: Detailed information, typically of interest only when diagnosing problems
    - INFO: Confirmation that things are working as expected
    - WARNING: An indication that something unexpected happened, or may happen in the near future
    - ERROR: Due to a more serious problem, the software has not been able to perform some function
    - CRITICAL: A serious error, indicating that the program itself may be unable to continue running
    
    Args:
        name: The logger name, typically __name__ from the calling module
        
    Returns:
        A configured logger instance
    """
    # Use a prefix for application loggers to ensure they inherit the right config
    if not name.startswith("dogshelter.") and name != "dogshelter":
        name = f"dogshelter.{name}"
        
    return logging.getLogger(name)