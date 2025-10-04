"""
Performance optimization strategies for logging.

This module provides utilities and best practices for optimizing logging
performance in production environments.
"""

import logging
from typing import Dict, Any, Callable, Union, List
from functools import lru_cache

from .config import get_logger

logger = get_logger(__name__)

class SampledLogger:
    """
    A logger that only logs a sample of messages to reduce logging volume.
    
    This is useful for high-frequency events that would otherwise generate
    excessive log entries.
    """
    
    def __init__(self, base_logger: logging.Logger, sample_rate: float = 0.01):
        """
        Initialize a sampled logger.
        
        Args:
            base_logger: The underlying logger to use
            sample_rate: Fraction of messages to log (0.01 = 1%)
        """
        self.logger = base_logger
        self.sample_rate = sample_rate
        self._counter = 0
    
    def debug(self, msg: str, *args, **kwargs):
        """Log a debug message (sampled)."""
        self._log(self.logger.debug, msg, *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs):
        """Log an info message (sampled)."""
        self._log(self.logger.info, msg, *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs):
        """Log a warning message (not sampled)."""
        # Warnings and above are always logged
        self.logger.warning(msg, *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs):
        """Log an error message (not sampled)."""
        self.logger.error(msg, *args, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs):
        """Log a critical message (not sampled)."""
        self.logger.critical(msg, *args, **kwargs)
    
    def _log(self, log_func: Callable, msg: str, *args, **kwargs):
        """Internal method to handle sampled logging."""
        self._counter += 1
        if self._counter >= int(1 / self.sample_rate):
            log_func(msg, *args, **kwargs)
            self._counter = 0


@lru_cache(maxsize=100)
def get_cached_logger(name: str) -> logging.Logger:
    """
    Get a logger with caching to avoid repeated logger creation.
    
    In high-performance applications, repeatedly calling getLogger can add overhead.
    This function caches loggers for reuse.
    
    Args:
        name: Logger name
        
    Returns:
        Cached logger instance
    """
    return get_logger(name)


class BatchLogger:
    """
    Logger that collects messages in a batch and logs them periodically.
    
    This reduces the overhead of frequent log calls by batching them together.
    """
    
    def __init__(self, logger: logging.Logger, batch_size: int = 100):
        """
        Initialize a batch logger.
        
        Args:
            logger: The underlying logger
            batch_size: Number of messages to collect before flushing
        """
        self.logger = logger
        self.batch_size = batch_size
        self.messages: Dict[int, List[str]] = {
            logging.DEBUG: [],
            logging.INFO: [],
            logging.WARNING: [],
            logging.ERROR: [],
            logging.CRITICAL: []
        }
    
    def debug(self, msg: str):
        """Add a debug message to the batch."""
        self._add_message(logging.DEBUG, msg)
    
    def info(self, msg: str):
        """Add an info message to the batch."""
        self._add_message(logging.INFO, msg)
    
    def warning(self, msg: str):
        """Add a warning message to the batch."""
        self._add_message(logging.WARNING, msg)
    
    def error(self, msg: str):
        """Add an error message to the batch."""
        self._add_message(logging.ERROR, msg)
        self.flush()  # Always flush on errors
    
    def critical(self, msg: str):
        """Add a critical message to the batch."""
        self._add_message(logging.CRITICAL, msg)
        self.flush()  # Always flush on critical
    
    def _add_message(self, level: int, msg: str):
        """Add a message to the appropriate level batch."""
        self.messages[level].append(msg)
        
        # Check if we've reached the batch size for any level
        total_messages = sum(len(messages) for messages in self.messages.values())
        if total_messages >= self.batch_size:
            self.flush()
    
    def flush(self):
        """Log all batched messages."""
        for level, messages in self.messages.items():
            if not messages:
                continue
                
            # Join messages with newlines
            batch_message = "\n".join(messages)
            
            # Log the batch with the appropriate level
            if level == logging.DEBUG:
                self.logger.debug(f"BATCH LOG:\n{batch_message}")
            elif level == logging.INFO:
                self.logger.info(f"BATCH LOG:\n{batch_message}")
            elif level == logging.WARNING:
                self.logger.warning(f"BATCH LOG:\n{batch_message}")
            elif level == logging.ERROR:
                self.logger.error(f"BATCH LOG:\n{batch_message}")
            elif level == logging.CRITICAL:
                self.logger.critical(f"BATCH LOG:\n{batch_message}")
            
            # Clear the batch
            self.messages[level] = []


def log_performance_optimizations():
    """Provide guidance on performance optimizations for logging."""
    logger.info("Logging Performance Best Practices:")
    logger.info("1. Use lazy evaluation for expensive operations")
    logger.info("2. Set appropriate log levels in production (INFO or higher)")
    logger.info("3. Use asynchronous logging for high-throughput applications")
    logger.info("4. Implement sampling for high-frequency events")
    logger.info("5. Consider structured logging for efficient parsing")
    logger.info("6. Monitor and rotate log files regularly")
    logger.info("7. Use a centralized logging service for distributed applications")