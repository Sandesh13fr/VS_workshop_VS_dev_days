"""
Logger setup for the Flask application.

This module handles the integration of the logging system with Flask.
"""

import os
import time
import logging
from typing import Dict, Any, Optional
from flask import Flask, request, g

from .config import get_logger, configure_logging
from .examples import ContextualLogger, log_execution_time

logger = get_logger(__name__)

def setup_flask_logging(
    app: Flask, 
    config_file: Optional[str] = None,
    log_level: Optional[str] = None,
    log_file: Optional[str] = None
) -> None:
    """
    Configure logging for a Flask application.
    
    Args:
        app: Flask application instance
        config_file: Path to logging configuration file
        log_level: Override default log level
        log_file: Override default log file path
    """
    # Initialize the logging system
    configure_logging(config_file, log_level, log_file)
    
    # Add request logging middleware
    @app.before_request
    def before_request():
        """Log incoming requests and record start time."""
        g.start_time = time.time()
        logger.debug(f"Request started: {request.method} {request.path}")
        
        # Store a contextual logger in g for use in request handlers
        g.logger = ContextualLogger.with_request(request, logger)
        g.logger.info(f"Processing {request.method} request")
    
    @app.after_request
    def after_request(response):
        """Log completed requests with status code and timing."""
        if hasattr(g, 'start_time'):
            duration_ms = (time.time() - g.start_time) * 1000
            logger.info(
                f"Request completed: {request.method} {request.path} "
                f"- Status: {response.status_code} - Duration: {duration_ms:.2f}ms"
            )
        return response
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Log unhandled exceptions."""
        logger.exception(f"Unhandled exception: {str(error)}")
        return {"error": "Internal Server Error"}, 500
    
    # Log application startup
    logger.info(f"Flask application '{app.name}' configured with logging")
    
    # Override Flask's default logger
    app.logger.handlers = []
    app.logger.propagate = True

def create_log_config(
    log_level: str = "INFO",
    log_to_console: bool = True,
    log_to_file: bool = True,
    log_file_path: str = "logs/app.log",
    max_file_size_mb: int = 10,
    backup_count: int = 5
) -> Dict[str, Any]:
    """
    Create a logging configuration dictionary.
    
    Args:
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_console: Whether to log to console
        log_to_file: Whether to log to a file
        log_file_path: Path to log file
        max_file_size_mb: Maximum size of each log file in MB
        backup_count: Number of backup files to keep
        
    Returns:
        Dictionary containing logging configuration
    """
    handlers = []
    if log_to_console:
        handlers.append("console")
    if log_to_file:
        handlers.append("file")
    
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s.%(msecs)03d [%(levelname)s] [%(thread)d] [%(name)s] %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "standard",
                "stream": "ext://sys.stdout"
            }
        },
        "loggers": {
            "": {
                "handlers": handlers,
                "level": log_level,
                "propagate": True
            },
            "dogshelter": {
                "level": log_level,
                "propagate": True
            }
        }
    }
    
    if log_to_file:
        config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": log_level,
            "formatter": "standard",
            "filename": log_file_path,
            "maxBytes": max_file_size_mb * 1024 * 1024,
            "backupCount": backup_count,
            "encoding": "utf8"
        }
    
    return config