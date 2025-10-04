"""
Examples of proper logging usage throughout the application.

This module provides example implementations showing:
- Proper logger initialization
- Correct usage of each log level
- Error/exception logging with stack traces
- Context-enriched logging
"""

import time
import logging
import traceback
from typing import Dict, Any, Callable
from functools import wraps

from .config import get_logger

logger = get_logger(__name__)

def log_execution_time(func: Callable) -> Callable:
    """
    Decorator to log the execution time of a function.
    
    Args:
        func: The function to be decorated
        
    Returns:
        Wrapped function that logs execution time
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.debug(f"Function '{func.__name__}' executed in {execution_time:.4f} seconds")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Function '{func.__name__}' failed after {execution_time:.4f} seconds: {str(e)}")
            raise
    
    return wrapper

class ContextualLogger:
    """
    Logger that includes contextual information with each log message.
    
    Example usage:
    ```
    # Create a logger with request context
    ctx_logger = ContextualLogger.with_request(request, logger)
    ctx_logger.info("Processing request")
    ```
    """
    
    def __init__(self, logger: logging.Logger, context: Dict[str, Any]):
        """
        Initialize a contextual logger.
        
        Args:
            logger: Base logger instance
            context: Dictionary of contextual information to include with log messages
        """
        self.logger = logger
        self.context = context
    
    @classmethod
    def with_request(cls, request, logger: logging.Logger):
        """
        Create a contextual logger with request information.
        
        Args:
            request: Flask request object
            logger: Base logger instance
            
        Returns:
            ContextualLogger instance with request context
        """
        context = {
            "request_id": request.headers.get("X-Request-ID", "unknown"),
            "user_agent": request.user_agent.string,
            "remote_addr": request.remote_addr,
            "path": request.path
        }
        return cls(logger, context)
    
    def _format_message(self, msg: str) -> str:
        """Format message with context information."""
        context_str = " ".join(f"{k}={v}" for k, v in self.context.items())
        return f"{msg} [{context_str}]"
    
    def debug(self, msg: str, *args, **kwargs):
        self.logger.debug(self._format_message(msg), *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs):
        self.logger.info(self._format_message(msg), *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs):
        self.logger.warning(self._format_message(msg), *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs):
        self.logger.error(self._format_message(msg), *args, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs):
        self.logger.critical(self._format_message(msg), *args, **kwargs)
    
    def exception(self, msg: str, *args, **kwargs):
        self.logger.exception(self._format_message(msg), *args, **kwargs)


# Example usage
def example_usage():
    """Demonstrate proper logging usage."""
    # Basic logging at different levels
    logger.debug("This is a debug message - use for detailed troubleshooting information")
    logger.info("This is an info message - use for normal application flow information")
    logger.warning("This is a warning message - use for unexpected situations that might need attention")
    logger.error("This is an error message - use for failures that impact functionality")
    logger.critical("This is a critical message - use for severe situations that might crash the application")
    
    # Logging exceptions with stack traces
    try:
        # Simulate an error
        result = 1 / 0
    except Exception as e:
        # Log the exception with full stack trace
        logger.exception(f"An error occurred: {e}")
        
        # Alternative method without using exception()
        stack_trace = traceback.format_exc()
        logger.error(f"Error details: {str(e)}\nStack trace: {stack_trace}")
    
    # Logging with additional structured data
    user_id = "user123"
    action = "login"
    logger.info(f"User action performed", extra={
        "user_id": user_id,
        "action": action,
        "success": True
    })

# Performance-optimized logging
def optimized_logging_example(expensive_data_provider):
    """
    Demonstrate performance-optimized logging.
    
    Args:
        expensive_data_provider: A function that returns data but is expensive to call
    """
    # BAD: Always evaluates the expensive operation
    # logger.debug(f"Debug data: {expensive_data_provider()}")
    
    # GOOD: Only evaluates if debug is enabled
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Debug data: {expensive_data_provider()}")
    
    # ALSO GOOD: Using lazy formatting with %s
    logger.debug("Debug data: %s", expensive_data_provider())